"""Collect public announcement candidates via configured RSS/Atom and optional official X API.
Never auto-publish unverified stream times or images. Set X_BEARER_TOKEN in GitHub Secrets.
"""
import json, pathlib, re, hashlib, datetime, urllib.request, urllib.parse, os, xml.etree.ElementTree as ET
from html import unescape
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'candidates.json'
PAT=re.compile(r'初配信|デビュー|初枠|立ち絵|配信|週間予定|今週|タイムテーブル|ガチイベ|バナイベ|ハフアニ|アニバーサリー|ギフ禁|ギフト禁止|イベント|IRIAM',re.I)
def fetch(url,headers=None):
    req=urllib.request.Request(url,headers={'User-Agent':'ProjectionScheduleWatch/2.0',**(headers or {})})
    with urllib.request.urlopen(req,timeout=20) as r:return r.read(2_000_000)
def textnode(e,names):
    for n in names:
        x=e.find(n)
        if x is not None and x.text:return x.text.strip()
    return ''
def main():
    sources=json.loads((ROOT/'data'/'sources.json').read_text(encoding='utf-8'))
    existing={v['id']:v for v in json.loads(OUT.read_text(encoding='utf-8'))} if OUT.exists() else {}
    now=datetime.datetime.now(datetime.timezone.utc).isoformat()
    def add(title,body,url,source,published='',media=None,author=''):
        plain=unescape(re.sub(r'<[^>]+>',' ',title+' '+body))
        if not PAT.search(plain) or not url.startswith('https://'):return
        key=hashlib.sha256(url.encode()).hexdigest()[:20]
        if key not in existing:existing[key]={'id':key,'title':title[:180], 'excerpt':plain[:800], 'url':url,'source':source[:100],'published_at':published,'discovered_at':now,'reviewed':False,'kind':'stream_or_debut_candidate','media':media or [],'author':author}
    feed_errors=[]
    feed_success=0
    for src in sources:
        url=src.get('feed_url','')
        if not url.startswith('https://'):continue
        try:
            root=ET.fromstring(fetch(url));feed_success+=1;nodes=root.findall('.//item') or root.findall('{http://www.w3.org/2005/Atom}entry')
            for e in nodes[:80]:
                title=textnode(e,['title','{http://www.w3.org/2005/Atom}title']);desc=textnode(e,['description','{http://www.w3.org/2005/Atom}summary','{http://www.w3.org/2005/Atom}content'])
                link=textnode(e,['link']);x=e.find('{http://www.w3.org/2005/Atom}link')
                if not link and x is not None:link=x.get('href','')
                add(title,desc,link,src.get('name','RSS'),textnode(e,['pubDate','{http://www.w3.org/2005/Atom}published']))
        except Exception as ex:
            feed_errors.append({'source':src.get('name',url),'error':str(ex)[:160]})
            print('Feed unavailable:',src.get('name',url),str(ex)[:160])
    token=os.getenv('X_BEARER_TOKEN','').strip()
    config=json.loads((ROOT/'data'/'x_accounts.json').read_text(encoding='utf-8'))
    report={'checked_at':now,'api_configured':bool(token),'accounts_configured':len(config.get('handles',[])),'posts_received':0,'feed_success':feed_success,'feed_errors':feed_errors,'errors':[],'note':'候補収集のみ。日時・イベント・配信中の確定には確認が必要。'}
    report['x_collection_state']='api_ready' if token else 'not_configured'
    report['hourly_full_coverage']=False
    if token:
        # One query for groups of accounts reduces API requests. Search only returns the recent-search window.
        handles=list(dict.fromkeys(h.lstrip('@').strip() for h in config.get('handles',[]) if isinstance(h,str)))
        handles=[h for h in handles if re.fullmatch(r'[A-Za-z0-9_]{1,15}',h)]
        # Optional cap to prevent unexpected API spending. Default: 2 queries/run.
        max_queries=max(0,int(os.getenv('X_MAX_QUERIES_PER_RUN','2')))
        report['query_limit']=max_queries
        report['total_account_batches']=(len(handles)+7)//8
        # Rotate batches across hourly runs instead of repeatedly checking the first 16 accounts.
        cursor_path=ROOT/'data'/'x_query_cursor.json'
        try:
            cursor_state=json.loads(cursor_path.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            cursor_state={}
        batches=[handles[i:i+8] for i in range(0,len(handles),8)]
        fingerprint=hashlib.sha256(','.join(handles).encode()).hexdigest()[:16]
        start=int(cursor_state.get('next_batch',0))%len(batches) if batches and cursor_state.get('fingerprint')==fingerprint else 0
        selected=[(start+i)%len(batches) for i in range(min(max_queries,len(batches)))] if batches else []
        report['batches_attempted']=len(selected)
        report['accounts_attempted']=sum(len(batches[i]) for i in selected)
        report['next_batch']=(start+len(selected))%len(batches) if batches else 0
        report['coverage_note']='Batches rotate and failed batches are retried. This is NOT hourly coverage per account. API limits and failures may delay coverage.'
        failed_batches=[]
        successful_batches=[]
        for batch_index in selected:
            batch=batches[batch_index]
            query='('+' OR '.join('from:'+h for h in batch)+') -is:retweet'
            params=urllib.parse.urlencode({'query':query,'max_results':100,'tweet.fields':'created_at,attachments,author_id','expansions':'attachments.media_keys,author_id','media.fields':'type,url,preview_image_url','user.fields':'username'})
            try:
                obj=json.loads(fetch('https://api.x.com/2/tweets/search/recent?'+params,{'Authorization':'Bearer '+token}))
                media_map={m['media_key']:m for m in obj.get('includes',{}).get('media',[]) if 'media_key' in m}
                users={u['id']:u['username'] for u in obj.get('includes',{}).get('users',[]) if 'id' in u and 'username' in u}
                if obj.get('errors') and not obj.get('data'):
                    raise ValueError('X API returned errors without usable data: '+str(obj['errors'])[:160])
                successful_batches.append(batch_index)
                for tweet in obj.get('data',[]):
                    author=users.get(tweet.get('author_id',''),'')
                    if not author:continue
                    medias=[{'type':media_map[k].get('type',''),'url':media_map[k].get('url') or media_map[k].get('preview_image_url','')} for k in tweet.get('attachments',{}).get('media_keys',[]) if k in media_map]
                    body=tweet.get('text','');url=f'https://x.com/{author}/status/{tweet["id"]}'
                    add(body[:100],body,url,'X @'+author,tweet.get('created_at',''),medias,author)
                    report['posts_received']+=1
            except Exception as ex:
                failed_batches.append(batch_index)
                report['errors'].append({'batch_index':batch_index,'accounts':batch,'error':str(ex)[:220]})
        report['batches_succeeded']=len(successful_batches)
        report['batches_failed']=len(failed_batches)
        report['failed_batch_indices']=failed_batches
        # Retry the first failed batch next run instead of silently skipping it.
        # Previously every API error advanced the cursor and could leave accounts unchecked for hours.
        if failed_batches:
            report['next_batch']=failed_batches[0]
        report['partial_coverage']=len(batches)>len(selected)
        report['hourly_full_coverage']=bool(batches) and len(selected)==len(batches) and not report['errors']
        report['x_collection_state']='api_error' if report['errors'] else ('partial_coverage' if report['partial_coverage'] else 'queried')
        # Failed batches are retried next run; monitoring reports persistent failures.
        cursor_path.write_text(json.dumps({'next_batch':report['next_batch'],'fingerprint':fingerprint},indent=2)+'\n',encoding='utf-8')

    else:
        print('X_BEARER_TOKEN not configured; skipping X API collection.')
    (ROOT/'data'/'collection_status.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    OUT.write_text(json.dumps(sorted(existing.values(),key=lambda v:v.get('discovered_at',''),reverse=True)[:1000],ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()

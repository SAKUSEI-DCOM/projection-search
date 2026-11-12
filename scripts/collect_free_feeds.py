"""Fetch explicitly configured public RSS/Atom feeds, no X scraping or paid API.
Feeds must be operated by the account owner or another authorized source.
"""
import json, pathlib, urllib.request, urllib.parse, xml.etree.ElementTree as ET
import hashlib, datetime, re, html
ROOT=pathlib.Path(__file__).resolve().parents[1]
CONFIG=ROOT/'data'/'free_feeds.json'
OUT=ROOT/'candidates.json'
STATUS=ROOT/'data'/'free_feed_status.json'
NS={'atom':'http://www.w3.org/2005/Atom','content':'http://purl.org/rss/1.0/modules/content/'}
PAT=re.compile('配信|初枠|初配信|IRIAM|立ち絵|ガチイベ|バナイベ|ハフアニ|ギフ禁|イベント|週間予定')
def txt(node, path):
    child=node.find(path,NS)
    return ''.join(child.itertext()).strip() if child is not None else ''
def items(xml):
    root=ET.fromstring(xml)
    for item in root.findall('.//item'):
        yield {'title':txt(item,'title'),'body':txt(item,'description') or txt(item,'content:encoded'),'url':txt(item,'link'),'date':txt(item,'pubDate')}
    for item in root.findall('.//atom:entry',NS):
        link=item.find('atom:link',NS)
        yield {'title':txt(item,'atom:title'),'body':txt(item,'atom:summary') or txt(item,'atom:content'),'url':link.get('href','') if link is not None else '', 'date':txt(item,'atom:published') or txt(item,'atom:updated')}
def normalized_date(raw):
    if not raw:return ''
    try:
        from email.utils import parsedate_to_datetime
        dt=parsedate_to_datetime(raw)
    except (TypeError,ValueError):
        try:dt=datetime.datetime.fromisoformat(raw.replace('Z','+00:00'))
        except ValueError:return ''
    if dt.tzinfo is None:return ''
    return dt.astimezone(datetime.timezone.utc).isoformat()
def main():
    feeds=json.loads(CONFIG.read_text(encoding='utf-8'))
    old=json.loads(OUT.read_text(encoding='utf-8')) if OUT.exists() else []
    known={c['id']:c for c in old}
    status={'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'feeds':[],'new_candidates':0}
    for feed in feeds:
        url=feed.get('url','');author=feed.get('x_handle','').lstrip('@')
        record={'name':feed.get('name',''),'url':url,'new':0}
        if not url.startswith('https://'):
            record['error']='HTTPS URL required';status['feeds'].append(record);continue
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'ProjectionPublicFeedWatcher/1.0 (+GitHub Pages fan project)'})
            with urllib.request.urlopen(req,timeout=18) as response: raw=response.read(2_000_000)
            for item in list(items(raw))[:100]:
                link=item['url']
                if not link.startswith('https://'):continue
                body=html.unescape(re.sub('<[^>]+>',' ',item['title']+' '+item['body']))
                if not PAT.search(body):continue
                ident=hashlib.sha256(link.encode()).hexdigest()[:20]
                if ident in known:continue
                known[ident]={'id':ident,'title':item['title'][:180],'excerpt':body[:1200],'url':link,
                  'source':feed.get('name','Public RSS'),'published_at':normalized_date(item['date']),
                  'discovered_at':status['checked_at'],'reviewed':False,'kind':'stream_or_debut_candidate',
                  'media':[],'author':author if feed.get('author_verified') is True else '',
                  'feed_origin':url,'source_author_verified':feed.get('author_verified') is True}
                record['new']+=1;status['new_candidates']+=1
        except Exception as exc:record['error']=str(exc)[:180]
        status['feeds'].append(record)
    OUT.write_text(json.dumps(sorted(known.values(),key=lambda x:x.get('discovered_at',''),reverse=True)[:2000],ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    STATUS.write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Create a reviewable audit of public Wiki profile links without contacting X.

The crawler reads only public Wiki profile pages. Ambiguous accounts are NOT assigned.
"""
import datetime,json,pathlib,re,urllib.parse,urllib.request,os
from bs4 import BeautifulSoup
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'data/profile_link_audit.json'
VALID=re.compile(r"[A-Za-z0-9_]{1,15}\Z")
RESERVED={'home','search','intent','share','i','settings','messages','notifications','explore','projecti0n','projection_vl'}
def find_x_links(html,base):
    soup=BeautifulSoup(html,'html.parser'); found={}
    for a in soup.select('a[href]'):
        u=urllib.parse.urlsplit(urllib.parse.urljoin(base,a['href']))
        if u.scheme!='https' or (u.hostname or '').lower() not in {'x.com','www.x.com','twitter.com','www.twitter.com'}:continue
        parts=[x for x in u.path.split('/') if x]
        if len(parts)!=1 or not VALID.fullmatch(parts[0]) or parts[0].lower() in RESERVED:continue
        key=parts[0].lower()
        context=' '.join(a.stripped_strings).strip()[:100]
        found.setdefault(key,{'handle':parts[0],'url':'https://x.com/'+parts[0],'link_texts':[]})
        if context and context not in found[key]['link_texts']:found[key]['link_texts'].append(context)
    return list(found.values())
def audit(fetch=None,batch=None):
    records=json.loads((ROOT/'livers.json').read_text(encoding='utf-8'))
    old=json.loads(OUT.read_text(encoding='utf-8')) if OUT.exists() else {}
    cursor=int(old.get('cursor',0))%max(1,len(records))
    batch=min(max(int(batch if batch is not None else os.getenv('LINK_AUDIT_BATCH','15')),1),30)
    previous={v['name']:v for v in old.get('results',[]) if isinstance(v,dict) and v.get('name')}
    checked=0
    for n in range(min(batch,len(records))):
        item=records[(cursor+n)%len(records)]; url=item.get('wiki') or item.get('source','')
        if not url.startswith('https://wikiwiki.jp/projecti0n/'):continue
        result={'name':item.get('name',''),'wiki':url,'registered_x':item.get('x',''),'candidates':[],'status':'unknown'}
        try:
            if fetch:html=fetch(url)
            else:
                req=urllib.request.Request(url,headers={'User-Agent':'ProjectionScheduleWatch/2.6 (public profile audit)'})
                with urllib.request.urlopen(req,timeout=12) as r:html=r.read(1200000)
            links=find_x_links(html,url)
            result['candidates']=links
            result['status']='already_registered' if item.get('x') else ('single_candidate' if len(links)==1 else 'ambiguous' if len(links)>1 else 'not_found')
        except Exception as e:result['status']='fetch_error';result['error']=str(e)[:140]
        previous[result['name']]=result;checked+=1
    results=[previous[r['name']] for r in records if r.get('name') in previous]
    report={'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'cursor':(cursor+batch)%max(1,len(records)),'roster_total':len(records),'checked_this_run':checked,'checked_unique':len(results),'results':results,'counts':{s:sum(x['status']==s for x in results) for s in ('single_candidate','ambiguous','not_found','already_registered','fetch_error')},'note':'Review candidates manually. No X pages fetched, no guessed handles assigned.'}
    OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return report
if __name__=='__main__':
    r=audit();print('Checked:',r['checked_this_run'],'review candidates:',r['counts']['single_candidate'])

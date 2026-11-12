#!/usr/bin/env python3
"""Discover RSS/Atom/iCalendar links in public Wiki profiles; do not auto-trust sources."""
import datetime,json,pathlib,re,urllib.parse,urllib.request,os
from bs4 import BeautifulSoup
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'data'/'feed_discovery.json'
SUFFIX=re.compile(r'\.(?:rss|atom|xml|ics)(?:$|[?#])',re.I)
FEED_TYPES={'application/rss+xml','application/atom+xml','text/calendar','application/ics','text/xml'}
def extract(html,base):
    soup=BeautifulSoup(html,'html.parser'); found={}
    for tag in soup.select('a[href],link[href]'):
        href=tag.get('href','').strip()
        if not href:continue
        u=urllib.parse.urljoin(base,href); p=urllib.parse.urlsplit(u)
        if p.scheme!='https' or not p.hostname or p.username or p.password:continue
        if p.hostname.lower() in {'x.com','twitter.com','www.x.com','www.twitter.com'}:continue
        kind='calendar' if SUFFIX.search(p.path) and p.path.lower().endswith('.ics') else 'feed'
        typ=tag.get('type','').lower().split(';')[0].strip()
        text=tag.get_text(' ',strip=True)[:90]
        if not (SUFFIX.search(p.path) or typ in FEED_TYPES or re.search(r'RSS|Atom|iCal|カレンダー|配信予定',text,re.I)):continue
        # A calendar label without an actual calendar URL is not enough.
        if not (SUFFIX.search(p.path) or typ in FEED_TYPES):continue
        clean=urllib.parse.urlunsplit((p.scheme,p.netloc,p.path,p.query,''))
        found[clean]={'url':clean,'kind':kind,'label':text,'mime':typ}
    return list(found.values())
def main(fetch=None,batch=None):
    roster=json.loads((ROOT/'livers.json').read_text(encoding='utf-8'))
    old=json.loads(OUT.read_text(encoding='utf-8')) if OUT.exists() else {}
    prev={x['name']:x for x in old.get('results',[]) if isinstance(x,dict) and x.get('name')}
    cursor=int(old.get('cursor',0))%max(1,len(roster)); batch=max(1,min(20,int(batch or os.getenv('FEED_DISCOVERY_BATCH','10'))))
    for i in range(min(batch,len(roster))):
        item=roster[(cursor+i)%len(roster)]; url=item.get('wiki') or item.get('source','')
        if not url.startswith('https://wikiwiki.jp/projecti0n/'):continue
        row={'name':item.get('name',''),'wiki':url,'sources':[],'status':'none'}
        try:
            if fetch: html=fetch(url)
            else:
                req=urllib.request.Request(url,headers={'User-Agent':'ProjectionPublicFeedDiscovery/1.0'})
                with urllib.request.urlopen(req,timeout=12) as r:html=r.read(1200000)
            row['sources']=extract(html,url);row['status']='candidate' if row['sources'] else 'none'
        except Exception as ex:row['status']='error';row['error']=str(ex)[:140]
        prev[row['name']]=row
    results=[prev[x['name']] for x in roster if x.get('name') in prev]
    report={'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'cursor':(cursor+batch)%max(1,len(roster)),
      'roster_total':len(roster),'checked_unique':len(results),'results':results,
      'candidate_sources':sum(len(x['sources']) for x in results),
      'note':'候補の自動検出のみ。取得元の利用許可・本人との対応は確認が必要。'}
    OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return report
if __name__=='__main__':
    r=main();print('Checked',r['checked_unique'],'candidate sources',r['candidate_sources'])

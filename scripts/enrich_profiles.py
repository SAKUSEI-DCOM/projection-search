#!/usr/bin/env python3
"""Conservatively discover X/IRIAM profile URLs from public Wiki individual pages.
Only fills blank fields; never copies images or guesses schedules. Limited batch per run.
"""
import json, pathlib, urllib.request, urllib.parse, re, os, datetime
from bs4 import BeautifulSoup
ROOT=pathlib.Path(__file__).resolve().parents[1]
ROSTER=ROOT/'livers.json'
REPORT=ROOT/'data/profile_enrichment_report.json'
def main():
    records=json.loads(ROSTER.read_text(encoding='utf-8'))
    old=json.loads(REPORT.read_text(encoding='utf-8')) if REPORT.exists() else {}
    cursor=int(old.get('cursor',0))%max(1,len(records))
    batch=min(max(int(os.getenv('PROFILE_BATCH','12')),1),25)
    checked=[]; updated=[]; errors=[]
    for offset in range(min(batch,len(records))):
        i=(cursor+offset)%len(records); item=records[i]
        url=item.get('wiki') or item.get('source','')
        if not url.startswith('https://wikiwiki.jp/projecti0n/'):continue
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'ProjectionScheduleWatch/2.1 (public wiki profile links)'})
            with urllib.request.urlopen(req,timeout=15) as r: html=r.read(1500000)
            soup=BeautifulSoup(html,'html.parser')
            links=[urllib.parse.urljoin(url,a.get('href','')) for a in soup.select('a[href]')]
            checked.append(item['name'])
            for field in ('x','iriam'):
                if item.get(field):continue
                candidates=[]
                for link in links:
                    p=urllib.parse.urlparse(link); host=p.hostname or ''
                    if field=='x' and host in ('x.com','twitter.com','www.x.com','www.twitter.com'):
                        path=p.path.strip('/').split('/')
                        if len(path)==1 and re.fullmatch(r'[A-Za-z0-9_]{1,15}',path[0]) and path[0].lower() not in ('intent','share','home','search','projecti0n','projection_vl'):
                            candidates.append('https://x.com/'+path[0])
                    if field=='iriam' and (host=='web.iriam.app' or host.endswith('.iriam.app')) and p.path.strip('/'):
                        candidates.append('https://'+host+p.path)
                candidates=list(dict.fromkeys(candidates))
                if len(candidates)==1:
                    item[field]=candidates[0];updated.append({'name':item['name'],'field':field,'url':candidates[0]})
        except Exception as e: errors.append({'name':item['name'],'error':str(e)[:130]})
    ROSTER.write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    REPORT.write_text(json.dumps({'updated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'cursor':(cursor+batch)%max(1,len(records)),'checked':checked,'updated':updated,'errors':errors,'note':'Only unique public profile links filled. No stream dates inferred.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Checked',len(checked),'updated',len(updated),'errors',len(errors))
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Synchronize monitored X handles from verified roster URLs, preserving manual handles.
No scraping or X login is performed. Invalid/ambiguous URLs are not guessed.
"""
import datetime, json, pathlib, re, urllib.parse
ROOT=pathlib.Path(__file__).resolve().parents[1]
HANDLES=ROOT/'data/x_accounts.json'
REPORT=ROOT/'data/x_account_sync_report.json'
VALID=re.compile(r"[A-Za-z0-9_]{1,15}\Z")
RESERVED={'home','search','intent','share','i','settings','messages','notifications','explore'}
def handle_from_url(url):
    if not isinstance(url,str):return None
    p=urllib.parse.urlsplit(url.strip())
    if p.scheme!='https' or (p.hostname or '').lower() not in {'x.com','www.x.com','twitter.com','www.twitter.com'}:return None
    parts=[x for x in p.path.split('/') if x]
    if len(parts)!=1 or not VALID.fullmatch(parts[0]) or parts[0].lower() in RESERVED:return None
    return parts[0]
def sync():
    livers=json.loads((ROOT/'livers.json').read_text(encoding='utf-8'))
    config=json.loads(HANDLES.read_text(encoding='utf-8'))
    manual=config.get('manual_handles',config.get('handles',[]))
    if not isinstance(manual,list):manual=[]
    roster={}; invalid=[]
    for liver in livers:
        url=liver.get('x','')
        if not url:continue
        h=handle_from_url(url)
        if h:roster.setdefault(h.lower(),{'handle':h,'livers':[]})['livers'].append(liver.get('name',''))
        else:invalid.append({'name':liver.get('name',''),'x':url})
    combined={}
    for h in manual:
        if isinstance(h,str) and VALID.fullmatch(h.lstrip('@')):combined[h.lstrip('@').lower()]=h.lstrip('@')
    for key,item in roster.items():combined[key]=item['handle']
    config['manual_handles']=list(dict.fromkeys(h.lstrip('@') for h in manual if isinstance(h,str) and VALID.fullmatch(h.lstrip('@'))))
    config['handles']=list(combined.values())
    HANDLES.write_text(json.dumps(config,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    report={'updated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'roster_total':len(livers),'roster_x_linked':sum(bool(x.get('x')) for x in livers),'roster_handles':len(roster),'manual_handles':len(config['manual_handles']),'total_handles':len(combined),'invalid_profile_urls':invalid,'duplicate_handles':[v for v in roster.values() if len(v['livers'])>1], 'note':'X handles synchronized only. X post collection still requires an authorized source or API credentials.'}
    REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return report
if __name__=='__main__':
    r=sync();print('Monitored handles:',r['total_handles'],'roster:',r['roster_handles'],'invalid:',len(r['invalid_profile_urls']))

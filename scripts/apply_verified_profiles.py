#!/usr/bin/env python3
"""Apply human-approved X account mappings, never guess identities.

Edit data/verified_x_profiles.json manually and commit. A mapping is applied
only when the account URL is valid, the liver name is unique, and the same
handle is not assigned to another liver. Existing differing URLs are preserved.
"""
import datetime,json,pathlib,sys
from sync_x_accounts import handle_from_url
ROOT=pathlib.Path(__file__).resolve().parents[1]
APPROVED=ROOT/'data/verified_x_profiles.json'
ROSTER=ROOT/'livers.json'
REPORT=ROOT/'data/verified_x_apply_report.json'
def run():
    approvals=json.loads(APPROVED.read_text(encoding='utf-8'))
    roster=json.loads(ROSTER.read_text(encoding='utf-8'))
    if not isinstance(approvals,list):raise ValueError('Approvals must be a JSON list')
    names={}; used={}; rejected=[]; applied=[]
    for i,item in enumerate(roster):
        names.setdefault(item.get('name',''),[]).append(i)
        h=handle_from_url(item.get('x',''))
        if h:used.setdefault(h.lower(),set()).add(item.get('name',''))
    seen_names=set()
    for row in approvals:
        if not isinstance(row,dict):rejected.append({'entry':str(row)[:80],'reason':'not_object'});continue
        name=row.get('name',''); url=row.get('x',''); handle=handle_from_url(url)
        if not name or len(names.get(name,[]))!=1 or name in seen_names:
            rejected.append({'name':name,'reason':'unknown_duplicate_or_repeated_name'});continue
        seen_names.add(name)
        if not handle:
            rejected.append({'name':name,'reason':'invalid_x_url'});continue
        idx=names[name][0]; existing=roster[idx].get('x','')
        if existing and handle_from_url(existing) != handle:
            rejected.append({'name':name,'reason':'conflicting_existing_x'});continue
        others=used.get(handle.lower(),set())-{name}
        if others:
            rejected.append({'name':name,'reason':'handle_already_used','other_names':sorted(others)});continue
        roster[idx]['x']='https://x.com/'+handle
        used.setdefault(handle.lower(),set()).add(name)
        applied.append({'name':name,'x':roster[idx]['x']})
    if applied:ROSTER.write_text(json.dumps(roster,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    report={'updated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'approved_entries':len(approvals),'applied_or_confirmed':len(applied),'rejected':rejected,'note':'Only manually verified mapping entries are applied; no X scraping.'}
    REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return report
if __name__=='__main__':
    result=run();print('Verified:',result['applied_or_confirmed'],'rejected:',len(result['rejected']))
    if result['rejected']:sys.exit(1)

#!/usr/bin/env python3
"""Generate public, secret-free operational diagnostics for static GitHub Pages."""
import json, re
from pathlib import Path
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parent.parent

def load(name, default):
    try: return json.loads((ROOT/name).read_text(encoding='utf-8'))
    except (OSError, ValueError): return default

def count_sources(data):
    if isinstance(data,list): return len(data)
    if isinstance(data,dict):
        return sum(len(v) for v in data.values() if isinstance(v,list))
    return 0

def main():
    livers=load('livers.json',[])
    accounts=load('data/x_accounts.json',{})
    handles=accounts.get('handles',[]) if isinstance(accounts,dict) else accounts
    handles={str(h).lower().lstrip('@') for h in handles if isinstance(h,str)}
    profile_handles={}
    for liver in livers:
        x=str(liver.get('x') or '')
        match=re.search(r'(?:x\.com|twitter\.com)/([A-Za-z0-9_]{1,15})(?:/|$)',x,re.I)
        if match: profile_handles[match.group(1).lower()]=liver.get('name','')
    # List is an ingestion target, not proof that account belongs to a roster member.
    missing=[{'name':str(l.get('name','')),'id':str(l.get('id',''))} for l in livers if not re.search(r'(?:x\.com|twitter\.com)/[A-Za-z0-9_]{1,15}(?:/|$)',str(l.get('x') or ''),re.I)]
    collection=load('data/collection_status.json',{})
    free=load('data/free_feed_status.json',{})
    inbox=load('data/inbox_report.json',{})
    auto=load('data/auto_publish_report.json',{})
    candidates=load('candidates.json',[])
    schedules=load('schedules.json',[])
    status={
      'generated_at':datetime.now(timezone.utc).isoformat(),
      'roster_total':len(livers),
      'x_profiles_known':len(livers)-len(missing),
      'x_profiles_missing':len(missing),
      'configured_x_handles':len(handles),
      'roster_x_handles_in_collection_list':len(handles.intersection(profile_handles)),
      'configured_public_feeds':count_sources(load('data/free_feeds.json',[]))+count_sources(load('data/sources.json',[])),
      'candidates_total':len(candidates),
      'schedules_total':len(schedules),
      'collection':collection,'free_feeds':free,'inbox':inbox,'auto_publish':auto,
      'missing_profiles':missing,
      'limitations':['Xのフォロー・リストは投稿の外部取得権限を付与しません。','X公式APIは別途利用資格・権限・料金の確認が必要です。','GitHub Actionsは定期実行されますが、遅延・スキップがあり得ます。','公開フィードが0件ならフィードからの投稿取得はできません。']
    }
    (ROOT/'data/automation_dashboard.json').write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('dashboard: roster',len(livers),'missing X',len(missing),'feeds',status['configured_public_feeds'])
if __name__=='__main__': main()

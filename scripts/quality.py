#!/usr/bin/env python3
"""Audit public data without assuming wiki listing proves debut or image rights."""
import json, pathlib, datetime, re
root=pathlib.Path(__file__).resolve().parents[1]
def read(name, fallback):
 try: return json.loads((root/name).read_text(encoding='utf-8'))
 except (OSError, ValueError): return fallback
rows=read('livers.json',[]); schedules=read('schedules.json',[]); events=read('special_events.json',[])
portraits=read('data/portrait_candidates.json',[]); feeds=read('data/sources.json',[])
health=read('data/health.json',{}); scan=read('data/portrait_scan_status.json',{})
issues=[]; ids=set(); names=set()
for r in rows:
 key=r.get('id','');name=r.get('name','')
 if not key or key in ids: issues.append({'kind':'duplicate_or_missing_id','name':name})
 ids.add(key)
 if not name or name in names: issues.append({'kind':'duplicate_or_missing_name','name':name})
 names.add(name)
 if r.get('image') and not (r.get('image_source') or r.get('portrait_source_url')):
  issues.append({'kind':'portrait_provenance_missing','name':name})
 if r.get('image') and r.get('portrait_status') != 'approved': issues.append({'kind':'portrait_not_approved','name':name})
 if r.get('portrait_status') == 'approved' and not r.get('image_permission'): issues.append({'kind':'portrait_permission_not_recorded','name':name})
for e in schedules+events:
 if not e.get('source') and not e.get('source_url'):issues.append({'kind':'event_source_missing','name':e.get('name','')})
 if e.get('name') not in names:issues.append({'kind':'event_unknown_liver','name':e.get('name','')})
now=datetime.datetime.now(datetime.timezone.utc)
def fresh(value):
 try:return (now-datetime.datetime.fromisoformat(value.replace('Z','+00:00'))).total_seconds()/3600
 except (ValueError,AttributeError,TypeError):return None
age=fresh(health.get('last_checked_at'))
result={'generated_at':now.isoformat(),'roster_count':len(rows),'debuted_wiki_classification':sum(x.get('status')=='debuted' for x in rows),'predebut_wiki_classification':sum(x.get('status')!='debuted' for x in rows),'debut_datetime_known':sum(bool(x.get('debut')) for x in rows),'portrait_registered':sum(bool(x.get('image')) for x in rows),'portrait_candidates_unverified':len(portraits),'x_profiles_known':sum(bool(x.get('x')) for x in rows),'iriam_profiles_known':sum(bool(x.get('iriam')) for x in rows),'published_schedules':len(schedules),'published_events':len(events),'configured_public_feeds':len(feeds),'x_direct_monitoring':bool(health.get('x_auto_monitoring_active')),'last_collection_at':health.get('last_checked_at'),'last_collection_age_hours':round(age,1) if age is not None else None,'collection_stale':age is None or age>3,'portrait_last_scan_at':scan.get('checked_at'),'issues':issues[:100],'issue_count':len(issues),'notes':['Wikiの所属区分は初配信の実施証明ではありません。','立ち絵候補は本人・公開状態・転載許可の確認前に公開しません。','X APIなしでは全ライバーのX投稿を自動監視できません。']}
out=root/'data/quality.json';out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Quality audit:',len(rows),'livers,',len(issues),'issues')

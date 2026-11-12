"""Conservatively derive sourced, explicitly dated announcements from configured public feeds.
No X scraping, no claims of live status. Requires year/month/day/time in the text.
"""
import json,re,datetime,pathlib,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
JST=datetime.timezone(datetime.timedelta(hours=9))
def load(name,default):
 p=ROOT/name
 try:return json.loads(p.read_text(encoding='utf8'))
 except (FileNotFoundError,json.JSONDecodeError):return default

def extract(text, published_at='', now=None):
 """Return a JST ISO timestamp only when the announcement has an unambiguous time.
 Relative dates are anchored to the X post's actual creation date, NOT crawl time.
 """
 now=now or datetime.datetime.now(JST)
 text=re.sub(r'\s+', ' ', text)
 m=re.search(r'(20\d{2})[年/.-]\s*(1[0-2]|0?[1-9])[月/.-]\s*(3[01]|[12]\d|0?[1-9])日?[^\n]{0,65}?(?:午前|午後)?\s*([01]?\d|2[0-3])[:：時]([0-5]\d)?',text)
 if m:
  y,mo,d,h,mi=m.groups()
  try: dt=datetime.datetime(int(y),int(mo),int(d),int(h),int(mi or 0),tzinfo=JST)
  except ValueError:return None
 else:
  # Month/day announcements are common in Japanese posts. Resolve the year from
  # the actual publication timestamp, not the crawler clock. For Nov/Dec posts,
  # Jan/Feb dates may refer to the following year.
  short=re.search(r'(?<!\d)(1[0-2]|0?[1-9])\s*月\s*(3[01]|[12]\d|0?[1-9])\s*日[^\n]{0,65}?(?:午前|午後)?\s*([01]?\d|2[0-3])\s*(?:[:：時]\s*([0-5]\d)?\s*分?)',text)
  if short and published_at:
   try: published=datetime.datetime.fromisoformat(published_at.replace('Z','+00:00')).astimezone(JST)
   except (ValueError,TypeError):return None
   mo,d,h,mi=map(int,(short.group(1),short.group(2),short.group(3),short.group(4) or '0'))
   year=published.year + (1 if published.month>=11 and mo<=2 else 0)
   try:dt=datetime.datetime(year,mo,d,h,mi,tzinfo=JST)
   except ValueError:return None
   if now-datetime.timedelta(days=1)<=dt<=now+datetime.timedelta(days=90):return dt.isoformat()
   return None
  # No reliable post timestamp means relative words cannot be safely resolved.
  if not published_at:return None
  try: published=datetime.datetime.fromisoformat(published_at.replace('Z','+00:00')).astimezone(JST)
  except (ValueError,TypeError):return None
  rel=re.search(r'(明日|あした|翌日|本日|今日|きょう|明後日|あさって)[^\n]{0,65}?(?<!\d)([01]?\d|2[0-3])\s*(?:[:：時]\s*([0-5]\d)?\s*分?)',text)
  if not rel:return None
  word,h,mi=rel.groups()
  delta=2 if word in ('明後日','あさって') else 1 if word in ('明日','あした','翌日') else 0
  d=published.date()+datetime.timedelta(days=delta)
  try:dt=datetime.datetime(d.year,d.month,d.day,int(h),int(mi or 0),tzinfo=JST)
  except ValueError:return None
 if now-datetime.timedelta(days=1)<=dt<=now+datetime.timedelta(days=90):return dt.isoformat()
 return None

def reconcile(candidates,livers,schedules,events,now=None):
 """Update only auto-imported records; keep manually curated records untouched.
 A source post URL is the stable identity, even when its announced time changes.
 """
 if not isinstance(schedules,list):schedules=[]
 if not isinstance(events,list):events=[]
 added=updated=cancelled=ambiguous=cancel_review=0
 # Old announcements must be processed before newer corrections/cancellations.
 for c in sorted(candidates,key=lambda x: str(x.get('published_at',''))):
  txt=(c.get('title','')+' '+c.get('excerpt','')).strip()
  url=c.get('url','')
  if not isinstance(url,str) or not url.startswith('https://'):continue
  author=str(c.get('author','')).lower().lstrip('@')
  matches=[x for x in livers if author and str(x.get('x','')).lower().rstrip('/').endswith('/'+author)]
  if len(matches)!=1:
   ambiguous+=1;continue
  liver=matches[0]
  owned=[(collection,item) for collection in (schedules,events) for item in collection
         if item.get('auto_imported') is True and item.get('source_url',item.get('source'))==url]
  is_cancel=bool(re.search(r'配信(?:は|を|が)?(?:お休み|休止|中止|延期)|(?:中止|延期|お休み|休止|配信なし|配信しません|配信できません|枠なし|休枠|リスケ)',txt))
  if is_cancel:
   # A separate cancellation post can refer to an older announcement.
   # Only reconcile when a precise date+time identifies exactly ONE auto schedule
   # belonging to the same verified account. Never touch manually entered data.
   if not owned:
    cancelled_time=extract(txt,c.get('published_at',''),now=now)
    if cancelled_time:
     possible=[(collection,item) for collection in (schedules,events) for item in collection
               if item.get('auto_imported') is True and item.get('name')==liver['name']
               and item.get('start')==cancelled_time]
     if len(possible)==1:owned=possible
     elif len(possible)>1:cancel_review+=1
    else:cancel_review+=1
   for collection,item in owned:
    collection.remove(item);cancelled+=1
   continue
  dt=extract(txt,c.get('published_at',''),now=now)
  if not dt:continue
  kind=next((k for key,k in [('ギフ禁','giftban'),('ギフト禁止','giftban'),('バナイベ','banner'),('ハフアニ','half'),('アニバーサリー','anniversary'),('ガチイベ','gachi')] if key in txt),None)
  if not kind and not re.search('配信|初枠|初配信|IRIAM',txt,re.I):continue
  target=events if kind else schedules
  key='auto-'+hashlib.sha256(url.encode()).hexdigest()[:18]
  entry={'id':key,'name':liver['name'],'start':dt,'title':c.get('title','')[:120],
         'source':url,'source_url':url,'auto_imported':True,
         'verification':'告知本文から日時を自動抽出・要確認'}
  if kind:entry['type']=kind
  else:entry['status']='tentative'
  if owned:
   # Move between schedule/event lists when a source post is corrected.
   changed=len(owned)!=1 or owned[0][0] is not target or any(owned[0][1].get(k)!=v for k,v in entry.items())
   if changed:
    for collection,item in owned:collection.remove(item)
    target.append(entry);updated+=1
  elif not any(item.get('id')==key for item in schedules+events):
   target.append(entry);added+=1
 return schedules,events,{'auto_added':added,'auto_updated':updated,'auto_cancelled':cancelled,'ambiguous_author':ambiguous,'cancellations_needing_review':cancel_review,
  'notice':'本人アカウント照合が成立する投稿のみ仮登録。既存の手動登録は変更しない。X API未設定ではX自動収集不可。'}

def main():
 candidates=load('candidates.json',[]);livers=load('livers.json',[])
 schedules,events,report=reconcile(candidates,livers,load('schedules.json',[]),load('special_events.json',[]))
 (ROOT/'data'/'auto_publish_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 (ROOT/'schedules.json').write_text(json.dumps(schedules,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 (ROOT/'special_events.json').write_text(json.dumps(events,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
if __name__=='__main__':main()

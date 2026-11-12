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

def main():
 candidates=load('candidates.json',[]); livers=load('livers.json',[])
 schedules=load('schedules.json',[]); events=load('special_events.json',[])
 if not isinstance(schedules,list):schedules=[]
 if not isinstance(events,list):events=[]
 known={x.get('id') for x in schedules+events}
 added=0; ambiguous=0
 for c in candidates:
  txt=(c.get('title','')+' '+c.get('excerpt','')).strip()
  # Cancellation, postponement, and retrospective notices must never create a new live slot.
  if re.search(r'配信(?:は|を|が)?(?:お休み|休止|中止|延期)|(?:中止|延期|お休み|休止|配信なし|配信しません|配信できません|枠なし|休枠|リスケ)',txt):
   continue
  dt=extract(txt,c.get('published_at',''))
  if not dt:continue
  author=c.get('author','').lower().lstrip('@')
  matches=[x for x in livers if author and x.get('x','').lower().rstrip('/').endswith('/'+author)]
  if len(matches)!=1:
   # Do not trust a name merely mentioned in a third-party post.
   # A verified author-to-profile mapping is required for automatic publication.
   ambiguous+=1;continue
  if len(matches)!=1:ambiguous+=1;continue
  liver=matches[0]; url=c.get('url','')
  if not url.startswith('https://'):continue
  kind=next((k for key,k in [('ギフ禁','giftban'),('ギフト禁止','giftban'),('バナイベ','banner'),('ハフアニ','half'),('アニバーサリー','anniversary'),('ガチイベ','gachi')] if key in txt),None)
  key='auto-'+hashlib.sha256((url+dt+str(kind)).encode()).hexdigest()[:18]
  if key in known:continue
  # Do not silently replace human-maintained records; keep separate sourced candidate records.
  entry={'id':key,'name':liver['name'],'start':dt,'title':c.get('title','')[:120], 'source':url,'source_url':url,'auto_imported':True,'verification':'告知本文から日時を自動抽出・要確認'}
  if kind:
   entry['type']=kind;events.append(entry)
  elif re.search('配信|初枠|初配信|IRIAM',txt,re.I):
   entry['status']='tentative';schedules.append(entry)
  else:continue
  known.add(key);added+=1
 (ROOT/'data'/'auto_publish_report.json').write_text(json.dumps({'auto_added':added,'ambiguous_author':ambiguous,'notice':'本人アカウント照合が成立する投稿のみ仮登録。休止・中止・延期は自動追加しない。X API未設定ではX自動収集不可。'},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 (ROOT/'schedules.json').write_text(json.dumps(schedules,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 (ROOT/'special_events.json').write_text(json.dumps(events,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
if __name__=='__main__':main()

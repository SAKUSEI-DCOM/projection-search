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

def extract(text):
 # Require an explicit year to avoid incorrectly dating old/relative announcements.
 m=re.search(r'(20\d{2})[年/.-]\s*(1[0-2]|0?[1-9])[月/.-]\s*(3[01]|[12]\d|0?[1-9])日?[^\n]{0,65}?(?:午前|午後)?\s*([01]?\d|2[0-3])[:：時]([0-5]\d)?',text)
 if not m:return None
 year,month,day,hour,minute=m.groups()
 try:
  dt=datetime.datetime(int(year),int(month),int(day),int(hour),int(minute or 0),tzinfo=JST)
  if not datetime.datetime.now(JST)-datetime.timedelta(days=1)<=dt<=datetime.datetime.now(JST)+datetime.timedelta(days=90):return None
  return dt.isoformat()
 except ValueError:return None

def main():
 candidates=load('candidates.json',[]); livers=load('livers.json',[])
 schedules=load('schedules.json',[]); events=load('special_events.json',[])
 if not isinstance(schedules,list):schedules=[]
 if not isinstance(events,list):events=[]
 known={x.get('id') for x in schedules+events}
 added=0; ambiguous=0
 for c in candidates:
  txt=(c.get('title','')+' '+c.get('excerpt','')).strip()
  dt=extract(txt)
  if not dt:continue
  author=c.get('author','').lower().lstrip('@')
  matches=[x for x in livers if author and x.get('x','').lower().rstrip('/').endswith('/'+author)]
  if len(matches)!=1:
   # Only use explicit unambiguous full name in post when author mapping absent.
   matches=[x for x in livers if len(x.get('name',''))>=3 and x['name'] in txt]
  if len(matches)!=1:ambiguous+=1;continue
  liver=matches[0]; url=c.get('url','')
  if not url.startswith('https://'):continue
  kind=next((k for key,k in [('ギフ禁','giftban'),('ギフト禁止','giftban'),('バナイベ','banner'),('ハフアニ','half'),('アニバーサリー','anniversary'),('ガチイベ','gachi')] if key in txt),None)
  key='auto-'+hashlib.sha256((url+dt+str(kind)).encode()).hexdigest()[:18]
  if key in known:continue
  # Do not silently replace human-maintained records; keep separate sourced candidate records.
  entry={'id':key,'name':liver['name'],'start':dt,'title':c.get('title','')[:120], 'source':url,'source_url':url,'auto_imported':True,'verification':'告知から自動抽出・要確認'}
  if kind:
   entry['type']=kind;events.append(entry)
  elif re.search('配信|初枠|初配信|IRIAM',txt,re.I):
   entry['status']='tentative';schedules.append(entry)
  else:continue
  known.add(key);added+=1
 (ROOT/'data'/'auto_publish_report.json').write_text(json.dumps({'auto_added':added,'ambiguous_author':ambiguous,'notice':'公開RSS等の取得済み告知に限定。Xの直接自動取得や実配信の確認は行っていません。'},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 (ROOT/'schedules.json').write_text(json.dumps(schedules,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 (ROOT/'special_events.json').write_text(json.dumps(events,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
if __name__=='__main__':main()

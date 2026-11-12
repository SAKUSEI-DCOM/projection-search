"""Import locally supplied, authorized CSV exports and trusted GitHub issue submissions.
No scraping or X access. Untrusted submissions stay in review queue.
"""
import csv, json, pathlib, re, hashlib, datetime, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
INBOX=ROOT/'data'/'incoming'
URL=re.compile(r'https://(?:www\.)?(?:x\.com|twitter\.com)/([A-Za-z0-9_]{1,15})/status/(\d+)(?:[/?#].*)?$',re.I)
def load(path,default):
 try:return json.loads(path.read_text(encoding='utf8'))
 except (OSError,ValueError):return default
def save(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def valid(row):
 url=str(row.get('post_url') or row.get('url') or '').strip(); m=URL.fullmatch(url)
 body=str(row.get('post_text') or row.get('text') or '').strip()
 published=str(row.get('published_at') or '').strip()
 author=str(row.get('author') or m.group(1) if m else row.get('author') or '').lstrip('@').strip()
 if not m or not body or not published or author.lower()!=m.group(1).lower():return None
 try:
  dt=datetime.datetime.fromisoformat(published.replace('Z','+00:00'))
  if not dt.tzinfo:return None
 except ValueError:return None
 return {'id':hashlib.sha256(url.encode()).hexdigest()[:20],'title':body[:120],'excerpt':body[:1500],'published_at':dt.isoformat(),'author':author,'url':url,'source':'authorized CSV / trusted issue','reviewed':False}
def main():
 path=ROOT/'candidates.json'; existing=load(path,[])
 if not isinstance(existing,list):existing=[]
 seen={x.get('url') for x in existing}; added=0; rejected=0; files=0
 for file in sorted(INBOX.glob('*.csv')):
  with file.open(encoding='utf-8-sig',newline='') as f:
   for row in csv.DictReader(f):
    item=valid(row)
    if not item:rejected+=1;continue
    if item['url'] not in seen:existing.append(item);seen.add(item['url']);added+=1
  files+=1
 # Only consume JSON created by the trusted-issue workflow.
 for file in sorted(INBOX.glob('*.json')):
  data=load(file,[])
  for row in data if isinstance(data,list) else [data]:
   item=valid(row)
   if not item:rejected+=1;continue
   if item['url'] not in seen:existing.append(item);seen.add(item['url']);added+=1
  files+=1
 save(path,existing[-2000:]);save(ROOT/'data'/'inbox_report.json',{'files_checked':files,'added':added,'invalid_rows':rejected,'note':'CSV/承認済みIssueの入力。X自動取得ではありません。'})
 print(f'inbox files={files} added={added} invalid={rejected}')
if __name__=='__main__':main()

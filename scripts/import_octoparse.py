"""Import a manually exported Octoparse CSV into candidates.json, then auto_publish.py.
Usage: python scripts/import_octoparse.py path/to/export.csv
Required columns: post_url, post_text, published_at, author (aliases accepted).
No X scraping is performed here.
"""
import csv, json, pathlib, re, sys, datetime
ROOT=pathlib.Path(__file__).resolve().parents[1]
ALIASES={
 'url':['post_url','tweet_url','tweet link','link','url','投稿url','ツイートurl','ツイートリンク'],
 'text':['post_text','tweet_text','text','content','full_text','本文','投稿本文','ツイート本文'],
 'published_at':['published_at','created_at','date','post_date','投稿日時','投稿日'],
 'author':['author','username','screen_name','handle','投稿者','ユーザー名'],
}
def pick(row,field):
 keys={str(k).strip().lower().replace(' ','_'):v for k,v in row.items() if k}
 for alias in ALIASES[field]:
  v=keys.get(alias.lower().replace(' ','_'))
  if v:return str(v).strip()
 return ''
def run(path):
 try: existing=json.loads((ROOT/'candidates.json').read_text(encoding='utf-8'))
 except (OSError,ValueError):existing=[]
 if not isinstance(existing,list):existing=[]
 known={x.get('url') for x in existing}; added=0; skipped=0
 with open(path,encoding='utf-8-sig',newline='') as f:
  for row in csv.DictReader(f):
   url=pick(row,'url'); body=pick(row,'text'); published=pick(row,'published_at'); author=pick(row,'author')
   m=re.fullmatch(r'https://(?:www\.)?(?:x\.com|twitter\.com)/([A-Za-z0-9_]{1,15})/status/(\d+)(?:[/?#].*)?',url)
   if not m or not body or not published or url in known:skipped+=1;continue
   try:
    dt=datetime.datetime.fromisoformat(published.replace('Z','+00:00'))
    if dt.tzinfo is None:raise ValueError('Timezone missing')
   except ValueError:skipped+=1;continue
   if author and author.lower().lstrip('@')!=m.group(1).lower():skipped+=1;continue
   existing.append({'title':body[:120],'excerpt':body,'published_at':dt.isoformat(),'author':m.group(1),'url':url,'source':'Octoparse CSV (manual export)'})
   known.add(url);added+=1
 (ROOT/'candidates.json').write_text(json.dumps(existing,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(f'Imported {added}; skipped {skipped}; total {len(existing)}. Run: python scripts/auto_publish.py')
if __name__=='__main__':
 if len(sys.argv)!=2:raise SystemExit('Usage: python scripts/import_octoparse.py export.csv')
 run(sys.argv[1])

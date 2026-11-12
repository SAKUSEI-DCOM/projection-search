#!/usr/bin/env python3
"""Refresh public Projection Wiki roster. Manual edits to existing fields are preserved.
Run via GitHub Actions. Wiki is unofficial; extracted changes require review for uncertain fields.
"""
import json, pathlib, re, urllib.request
from urllib.parse import urljoin, unquote
from bs4 import BeautifulSoup
ROOT=pathlib.Path(__file__).resolve().parents[1]
URL='https://wikiwiki.jp/projecti0n/'
def load(path):
 try:return json.loads(path.read_text(encoding='utf-8'))
 except (FileNotFoundError,ValueError):return []
def main():
 path=ROOT/'livers.json'; old=load(path)
 known={x['name']:x for x in old}
 req=urllib.request.Request(URL,headers={'User-Agent':'ProjectionCommunitySchedule/1.0 (public roster synchronization)'})
 try:
  with urllib.request.urlopen(req,timeout=20) as response: html=response.read().decode('utf-8','replace')
 except Exception as exc:
  print('Wiki fetch failed; keeping current roster:',exc);return
 soup=BeautifulSoup(html,'html.parser')
 # Collect only links to individual pages in the known roster, and update their source URLs.
 # Avoid treating navigation and retired profiles as current members.
 found=set()
 for a in soup.select('a[href]'):
  href=urljoin(URL,a.get('href',''))
  if not href.startswith('https://wikiwiki.jp/projecti0n/') or href.rstrip('/')==URL.rstrip('/'):continue
  name=a.get_text(' ',strip=True)
  if name in known:
   known[name]['wiki']=href
   found.add(name)
 # Do not delete anyone merely because the wiki markup changed.
 # Flag missing people for manual review rather than altering membership status.
 report={'source':URL,'matched_existing':len(found),'missing_from_parsed_links':sorted(set(known)-found)}
 (ROOT/'data/wiki_sync_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 path.write_text(json.dumps(old,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('Matched',len(found),'roster profiles; existing records preserved')
if __name__=='__main__':main()

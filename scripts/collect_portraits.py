#!/usr/bin/env python3
"""Conservative portrait discovery from Wiki. No X scraping, no partial-reveal guesses.
Creates review candidates, not public image changes. A human must verify identity,
full reveal and permission before adding a portrait URL to livers.json.
"""
import json, pathlib, datetime, urllib.request, urllib.parse, re, os
from bs4 import BeautifulSoup
ROOT=pathlib.Path(__file__).resolve().parents[1]
ROSTER=ROOT/'livers.json'
OUT=ROOT/'data/portrait_candidates.json'
EXAMPLE_POST='https://x.com/Orphe_watson96/status/1985127073497948355'
REPORT=ROOT/'data/portrait_scan_status.json'
CURSOR=ROOT/'data/portrait_cursor.json'
def main():
    rows=json.loads(ROSTER.read_text(encoding='utf-8'))
    previous=json.loads(OUT.read_text(encoding='utf-8')) if OUT.exists() else []
    bykey={(x.get('liver_id'),x.get('url')):x for x in previous}
    errors=[]; checked=0
    batch=max(1,int(os.getenv("PORTRAIT_BATCH","12")))
    cursor=json.loads(CURSOR.read_text(encoding='utf-8')).get('next_index',0) if CURSOR.exists() else 0
    cursor=cursor%len(rows) if rows else 0
    selected=[rows[(cursor+i)%len(rows)] for i in range(min(batch,len(rows)))] if rows else []
    for item in selected:
        wiki=item.get('wiki','')
        if not wiki.startswith('https://wikiwiki.jp/projecti0n/') or item.get('image'):continue
        try:
            req=urllib.request.Request(wiki,headers={'User-Agent':'ProjectionFanSchedule/1.0 (portrait-source review)'})
            with urllib.request.urlopen(req,timeout=12) as r: page=r.read(1500000)
            soup=BeautifulSoup(page,'html.parser');checked+=1
            # Candidate ONLY when image alt/title explicitly mentions 立ち絵, 全身 or キービジュアル.
            # Avoid unrelated thumbnails, avatars, and unfinished reveal challenge panels.
            # Find X posts explicitly labelled as portrait/reveal challenges in the Wiki.
            # Store the post as a candidate link only; X media is not scraped or republished.
            for link in soup.select('a[href]'):
                href=urllib.parse.urljoin(wiki,link.get('href',''))
                if not re.match(r'https://(?:www\.)?(?:x\.com|twitter\.com)/[^/]+/status/\d+',href):continue
                context=' '.join([link.get_text(' ',strip=True),link.get('title',''),link.parent.get_text(' ',strip=True)[:240] if link.parent else ''])
                if not re.search(r'立ち絵|公開チャレンジ|全身公開|シルエット公開|お披露目',context,re.I):continue
                key=(item['id'],href)
                bykey.setdefault(key,{'liver_id':item['id'],'name':item['name'],'url':href,'source':wiki,'description':context[:160],'candidate_type':'x_reveal_post','review_status':'unreviewed','note':'X post linked from Wiki. Confirm completed reveal, subject and image reuse rights.'})
            for img in soup.select('img[src]'):
                context=' '.join([img.get('alt',''),img.get('title','')])
                if not re.search('立ち絵|全身|キービジュアル',context):continue
                src=urllib.parse.urljoin(wiki,img.get('src',''))
                if not src.startswith('https://'):continue
                key=(item['id'],src)
                bykey.setdefault(key,{'liver_id':item['id'],'name':item['name'],'url':src,'source':wiki,'description':context[:160],'candidate_type':'wiki_image','review_status':'unreviewed','note':'Wiki image candidate. Check full reveal, ownership and permission.'})
        except Exception as exc:errors.append({'name':item['name'],'error':str(exc)[:140]})
    CURSOR.write_text(json.dumps({'next_index':(cursor+len(selected))%len(rows) if rows else 0},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    OUT.write_text(json.dumps(list(bykey.values()),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    REPORT.write_text(json.dumps({'checked':checked,'batch_start':cursor,'batch_size':len(selected),'total_livers':len(rows),'candidate_count':len(bykey),'errors':errors,'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat()},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()

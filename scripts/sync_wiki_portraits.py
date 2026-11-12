#!/usr/bin/env python3
"""Attach unambiguous public portrait URLs from each liver's Wiki profile.
Never download/rehost images; skip ambiguous, placeholders, and already-set portraits.
"""
import json, os, pathlib, re, urllib.request
from urllib.parse import urljoin, urlsplit
from bs4 import BeautifulSoup
from datetime import datetime, timezone
ROOT=pathlib.Path(__file__).resolve().parents[1]
ROSTER=ROOT/'livers.json'; REPORT=ROOT/'data/wiki_portrait_report.json'; STATE=ROOT/'data/wiki_portrait_cursor.json'; REGISTRY=ROOT/'data/wiki_portrait_candidates.json'; APPROVALS=ROOT/'data/wiki_portrait_approvals.json'
BAD=re.compile(r'logo|banner|icon[-_]?menu|advert|emoji|badge|thumb|noimage|placeholder|sample|face_orig',re.I)
GOOD=re.compile(r'立ち絵|全身|キービジュアル|プロフィール画像|ライバー画像|character|portrait',re.I)
def extract(html,base):
    """Only collect explicitly identified portrait images from Wiki-hosted assets.

    Supports lazy-loaded image URLs and labelled figure captions; does not
    infer that an arbitrary image on a person's profile is their portrait.
    """
    soup=BeautifulSoup(html,'html.parser'); matches=[]
    for img in soup.select('img'):
        labels=[str(img.get('alt') or ''),str(img.get('title') or '')]
        figure=img.find_parent('figure')
        if figure:
            caption=figure.find('figcaption')
            if caption: labels.append(caption.get_text(' ',strip=True)[:160])
        # Wiki pages sometimes use a caption in the immediate image link title.
        parent=img.parent
        if parent and parent.name=='a': labels.append(str(parent.get('title') or ''))
        # Wiki profiles often put the image label in the same table cell or
        # immediately preceding paragraph, rather than in an img alt attribute.
        # Restrict context to a short, adjacent label to avoid matching an
        # unrelated '立ち絵' elsewhere on the page.
        cell=img.find_parent(['td','th'])
        if cell:
            local=cell.get_text(' ',strip=True)[:90]
            if len(cell.select('img'))==1: labels.append(local)
        previous=img.find_previous_sibling(string=True)
        if previous: labels.append(str(previous).strip()[:60])
        desc=' '.join(labels)
        if not GOOD.search(desc) or BAD.search(desc):continue
        for attr in ('data-src','data-original','data-lazy-src','src'):
            raw=str(img.get(attr) or '').strip()
            if not raw or raw.startswith('data:'):continue
            url=urljoin(base,raw); p=urlsplit(url)
            host=(p.hostname or '').lower()
            if p.scheme!='https' or p.username or p.password or not host or BAD.search(url):continue
            if host!='wikiwiki.jp' and not host.endswith('.wikiwiki.jp'):continue
            matches.append(url)
            break
    return list(dict.fromkeys(matches))

def run(fetch=None,batch_size=None):
    roster=json.loads(ROSTER.read_text(encoding='utf-8'))
    eligible=[r for r in roster if r.get('wiki','').startswith('https://wikiwiki.jp/projecti0n/') and r.get('status') not in ('retired','graduated')]
    cursor=json.loads(STATE.read_text()).get('cursor',0) if STATE.exists() else 0
    registry=json.loads(REGISTRY.read_text(encoding='utf-8')) if REGISTRY.exists() else {}
    count=min(len(eligible),max(0,int(batch_size if batch_size is not None else os.getenv('WIKI_PORTRAIT_BATCH','12'))))
    approvals=json.loads(APPROVALS.read_text(encoding='utf-8')) if APPROVALS.exists() else {}
    report={'checked_at':datetime.now(timezone.utc).isoformat(),'checked':0,'filled':[],'candidates':[],'ambiguous':[],'missing':[],'errors':[],'approved':[],'approval_mismatches':[],'previously_approved_missing':[],'previously_approved_changed':[],'note':'Only explicitly labelled portrait images are linked, not copied; check rights before public display.'}
    for i in range(count):
        row=eligible[(cursor+i)%len(eligible)]
        # Previously approved Wiki images must still be audited for source changes.
        # Manually assigned images are never overwritten.
        if row.get('image') and row.get('portrait_status')!='wiki_embed_approved_by_operator':
            continue
        url=row['wiki']
        try:
            if fetch: html=fetch(url)
            else:
                req=urllib.request.Request(url,headers={'User-Agent':'ProjectionCommunitySchedule/1.0 (public wiki portrait audit)'})
                with urllib.request.urlopen(req,timeout=12) as resp:html=resp.read(1500000).decode('utf-8','replace')
            candidates=extract(html,url);report['checked']+=1
            if row.get('portrait_status')=='wiki_embed_approved_by_operator':
                if not candidates:
                    report['previously_approved_missing'].append(row['name'])
                elif row.get('image') not in candidates:
                    report['previously_approved_changed'].append(row['name'])
                # Do not silently replace or remove an existing published image.
                continue
            if len(candidates)==1:
                report['candidates'].append({'name':row['name'],'wiki':url,'image_url':candidates[0]})
                registry[str(row['id'])]={'name':row['name'],'wiki':url,'image_url':candidates[0],'status':'permission_check_required','last_seen':report['checked_at']}
                # Explicit per-liver approval only; global blanket approval is intentionally disabled.
                approval=approvals.get(str(row['id']),{})
                if approval.get('approved') is True and approval.get('image_url')==candidates[0] and approval.get('source_url')==url and approval.get('rights_confirmed_by'):
                    row['image']=candidates[0];row['image_source']=url;row['portrait_source_url']=url;row['portrait_status']='wiki_embed_approved_by_operator';report['filled'].append(row['name']);report['approved'].append(row['name'])
                elif approval.get('approved'):
                    report['approval_mismatches'].append(row['name'])
            elif len(candidates)>1:
                report['ambiguous'].append(row['name'])
                # Keep historical candidate for audit; do not publish ambiguous results.
                if str(row['id']) in registry: registry[str(row['id'])]['status']='ambiguous_recheck_required'
            else:
                report['missing'].append(row['name'])
                if str(row['id']) in registry: registry[str(row['id'])]['status']='not_found_on_latest_check'
        except Exception as exc:report['errors'].append({'name':row['name'],'error':str(exc)[:150]})
    REGISTRY.write_text(json.dumps(registry,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    ROSTER.write_text(json.dumps(roster,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    STATE.write_text(json.dumps({'cursor':(cursor+count)%max(len(eligible),1),'total':len(eligible)},indent=2)+'\n')
    REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return report
if __name__=='__main__':print(json.dumps(run(),ensure_ascii=False))

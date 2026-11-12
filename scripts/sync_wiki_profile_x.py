#!/usr/bin/env python3
"""Incrementally inspect public Wiki profile pages for linked X profiles.
No X pages or posts are fetched. Ambiguous matches never overwrite existing data.
"""
import json, pathlib, time, urllib.request, os
from datetime import datetime, timezone
from urllib.parse import urlsplit
from bs4 import BeautifulSoup
from sync_wiki_x_links import ROOT, WIKI, x_profile

ROSTER = ROOT / 'livers.json'
STATE = ROOT / 'data/wiki_profile_cursor.json'
REPORT = ROOT / 'data/wiki_profile_x_report.json'

def extract_profile_links(html):
    soup = BeautifulSoup(html, 'html.parser')
    urls = set()
    for a in soup.select('a[href]'):
        url = a.get('href', '')
        if url.startswith('//'):
            url = 'https:' + url
        url = x_profile(url)
        if url:
            urls.add(url)
    return sorted(urls)

def sync(fetch=None, batch_size=12, pause=1.0):
    roster = json.loads(ROSTER.read_text(encoding='utf-8'))
    eligible = [r for r in roster if r.get('wiki', '').startswith(WIKI) and r.get('status') not in ('retired', 'graduated')]
    cursor = json.loads(STATE.read_text(encoding='utf-8')).get('cursor', 0) if STATE.exists() else 0
    cursor %= max(len(eligible), 1)
    batch = [eligible[(cursor+i) % len(eligible)] for i in range(min(batch_size, len(eligible)))]
    report = {'checked_at': datetime.now(timezone.utc).isoformat(), 'eligible':len(eligible), 'checked':0,
              'added':[], 'conflicts':[], 'multiple':[], 'no_links':[], 'errors':[],
              'note':'X profile links only; X posts not collected. Missing links do not prove retirement.'}
    for r in batch:
        url = r['wiki']
        if urlsplit(url).hostname != 'wikiwiki.jp' or not urlsplit(url).path.startswith('/projecti0n/'):
            continue
        try:
            if fetch is None:
                req = urllib.request.Request(url, headers={'User-Agent':'ProjectionCommunitySchedule/1.0 (wiki profile link audit)'})
                with urllib.request.urlopen(req, timeout=12) as response:
                    html = response.read(1_500_000).decode('utf-8', 'replace')
            else:
                html = fetch(url)
            links = extract_profile_links(html)
            report['checked'] += 1
            if not links:
                report['no_links'].append(r['name'])
            elif len(links) > 1:
                report['multiple'].append({'name':r['name'], 'urls':links})
            else:
                current = x_profile(r.get('x', ''))
                if not current:
                    r['x'] = links[0]
                    report['added'].append({'name':r['name'], 'x':links[0]})
                elif current.lower() != links[0].lower():
                    report['conflicts'].append({'name':r['name'], 'existing':current, 'wiki':links[0]})
        except Exception as exc:
            report['errors'].append({'name':r['name'], 'error':str(exc)[:160]})
        if fetch is None and pause:
            time.sleep(pause)
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps({'cursor':(cursor+len(batch))%max(len(eligible),1), 'total':len(eligible)}, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    ROSTER.write_text(json.dumps(roster, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print('Profile wiki audit:', report['checked'], 'new:', len(report['added']), 'errors:',len(report['errors']))
    return report

if __name__ == '__main__':
    sync(batch_size=min(200, max(1, int(os.getenv('WIKI_PROFILE_BATCH', '12')))))

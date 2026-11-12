#!/usr/bin/env python3
"""Conservative public Wiki X-profile link sync; never collects X posts."""
import json, pathlib, re, urllib.request
from datetime import datetime, timezone
from urllib.parse import urljoin, urlsplit
from bs4 import BeautifulSoup
ROOT = pathlib.Path(__file__).resolve().parents[1]
WIKI = 'https://wikiwiki.jp/projecti0n/'
XHOST = {'x.com', 'www.x.com', 'twitter.com', 'www.twitter.com'}
HANDLE = re.compile(r'[A-Za-z0-9_]{1,15}\Z')
BLOCKED = {'i','home','search','intent','share','explore','settings','messages','notifications'}

def x_profile(url):
    try:
        u = urlsplit(url)
        parts = [p for p in u.path.split('/') if p]
        if u.scheme != 'https' or u.hostname not in XHOST or len(parts) != 1:
            return ''
        if not HANDLE.fullmatch(parts[0]) or parts[0].lower() in BLOCKED:
            return ''
        return 'https://x.com/' + parts[0]
    except (ValueError, TypeError):
        return ''

def extract(html, names):
    """Only associate X URLs in the same compact list item/table row/paragraph.
    Stop at the next roster name. Conflicts require human review.
    """
    soup = BeautifulSoup(html, 'html.parser')
    found, ambiguous = {}, {}
    for a in soup.select('a[href]'):
        name = a.get_text(' ', strip=True)
        if name not in names:
            continue
        target = urljoin(WIKI, a['href'])
        if urlsplit(target).hostname != 'wikiwiki.jp' or not urlsplit(target).path.startswith('/projecti0n/'):
            continue
        container = a.find_parent(['tr','li','p']) or a.parent
        if container is None:
            continue
        links = container.find_all('a', href=True)
        try:
            index = links.index(a)
        except ValueError:
            continue
        xs = []
        for b in links[index + 1:]:
            if b.get_text(' ', strip=True) in names:
                break
            candidate = x_profile(urljoin(WIKI, b['href']))
            if candidate and candidate.lower() not in {x.lower() for x in xs}:
                xs.append(candidate)
            if len(xs) > 3:
                break
        if len(xs) == 1:
            if name in found and found[name].lower() != xs[0].lower():
                ambiguous[name] = list(dict.fromkeys([found[name], xs[0]]))
            elif name not in ambiguous:
                found[name] = xs[0]
        elif len(xs) > 1:
            ambiguous[name] = xs
    for name in ambiguous:
        found.pop(name, None)
    return found, ambiguous

def sync(html=None):
    roster_path = ROOT / 'livers.json'
    roster = json.loads(roster_path.read_text(encoding='utf-8'))
    names = {r['name'] for r in roster if r.get('name')}
    report_path = ROOT / 'data/wiki_x_link_report.json'
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report = {'source': WIKI, 'checked_at': datetime.now(timezone.utc).isoformat(),
              'roster_count': len(roster), 'status': 'pending', 'matched': 0,
              'newly_linked': [], 'changed_needs_review': [],
              'ambiguous_needs_review': {}, 'unmatched_not_retired': [],
              'note': 'Wiki link absence, network failure, or X access error does not establish retirement. X posts are not fetched.'}
    if html is None:
        req = urllib.request.Request(WIKI, headers={'User-Agent': 'ProjectionCommunitySchedule/1.0 (public roster links; hourly)'})
        try:
            with urllib.request.urlopen(req, timeout=25) as res:
                html = res.read(3_000_000).decode('utf-8', 'replace')
        except Exception as e:
            report.update(status='fetch_error', error=str(e)[:250])
            report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
            print('Wiki unavailable; existing links retained:', e)
            return False
    found, ambiguous = extract(html, names)
    report['matched'] = len(found)
    report['ambiguous_needs_review'] = ambiguous
    report['unmatched_not_retired'] = sorted(names - found.keys() - ambiguous.keys())
    if not found:
        report['status'] = 'no_matches'
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        print('No matching Wiki X links; existing links retained')
        return False
    for r in roster:
        name = r.get('name', '')
        if name not in found:
            continue
        candidate = found[name]
        existing = x_profile(r.get('x', ''))
        if not existing:
            r['x'] = candidate
            report['newly_linked'].append({'name': name, 'x': candidate})
        elif existing.lower() != candidate.lower():
            report['changed_needs_review'].append({'name': name, 'existing': existing, 'wiki': candidate})
    report['status'] = 'ok'
    roster_path.write_text(json.dumps(roster, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print('Wiki links:', len(found), 'new:', len(report['newly_linked']), 'review:', len(report['changed_needs_review']) + len(ambiguous))
    return True

if __name__ == '__main__':
    sync()

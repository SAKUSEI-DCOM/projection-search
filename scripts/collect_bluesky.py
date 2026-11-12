"""Collect public Bluesky posts through the official unauthenticated AppView API.
Only explicitly verified actor-to-liver mappings are eligible for auto-publishing.
No X scraping or account credentials are used.
"""
import datetime
import hashlib
import json
import pathlib
import re
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONFIG = ROOT / 'data' / 'bluesky_accounts.json'
OUT = ROOT / 'candidates.json'
STATUS = ROOT / 'data' / 'bluesky_collection_status.json'
KEYWORDS = re.compile(r'配信|初枠|初配信|IRIAM|ガチイベ|バナイベ|ハフアニ|ギフ禁|立ち絵|週間予定|アニバーサリー')


def parse_posts(payload, actor, x_handle, verified, discovered_at):
    results = []
    for item in payload.get('feed', []):
        post = item.get('post') or {}
        author = post.get('author') or {}
        record = post.get('record') or {}
        uri = post.get('uri', '')
        text = record.get('text', '')
        # Exclude reposts and posts from other actors; avoid accidental attribution.
        if item.get('reason') or not uri.startswith('at://') or not isinstance(text, str):
            continue
        if author.get('handle', '').lower() != actor.lower() and author.get('did') != actor:
            continue
        if not KEYWORDS.search(text):
            continue
        parts = uri.split('/')
        if len(parts) < 5 or parts[-2] != 'app.bsky.feed.post':
            continue
        url = 'https://bsky.app/profile/' + urllib.parse.quote(author.get('did', ''), safe=':') + '/post/' + urllib.parse.quote(parts[-1], safe='')
        published = record.get('createdAt', '')
        # Publication date is essential for resolving relative dates.
        try:
            parsed = datetime.datetime.fromisoformat(published.replace('Z', '+00:00'))
            if parsed.tzinfo is None:
                continue
        except (ValueError, AttributeError):
            continue
        results.append({
            'id': hashlib.sha256(uri.encode()).hexdigest()[:20],
            'title': text[:120], 'excerpt': text[:1200], 'url': url,
            'published_at': published, 'discovered_at': discovered_at,
            'source': 'Bluesky public API', 'kind': 'stream_or_debut_candidate',
            'reviewed': False, 'media': [],
            'author': x_handle if verified else '',
            'source_author_verified': verified,
            'source_actor': actor, 'source_uri': uri,
        })
    return results


def collect(fetch=None):
    fetch = fetch or _fetch
    accounts = json.loads(CONFIG.read_text(encoding='utf8'))
    candidates = json.loads(OUT.read_text(encoding='utf8')) if OUT.exists() else []
    known = {c['id']: c for c in candidates if isinstance(c, dict) and c.get('id')}
    livers = json.loads((ROOT / 'livers.json').read_text(encoding='utf8'))
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    report = {'checked_at': now, 'accounts': [], 'new_candidates': 0, 'note': 'Official Bluesky public API only; no X data fetched'}
    for account in accounts:
        actor = str(account.get('actor', '')).strip().removeprefix('@')
        x_handle = str(account.get('x_handle', '')).strip().lstrip('@')
        verified = account.get('verified_mapping') is True
        # Verified mapping must also match exactly one known X profile.
        matched = [l for l in livers if x_handle and str(l.get('x', '')).lower().rstrip('/').endswith('/' + x_handle.lower())]
        verified = verified and len(matched) == 1
        item_report = {'actor': actor, 'verified_mapping': verified, 'new': 0}
        if not re.fullmatch(r'[A-Za-z0-9._:-]{3,253}', actor):
            item_report['error'] = 'Invalid Bluesky actor'; report['accounts'].append(item_report); continue
        try:
            payload = fetch(actor)
            for entry in parse_posts(payload, actor, x_handle, verified, now):
                if entry['id'] in known:
                    # Update edits to same post without losing initial discovery timestamp.
                    entry['discovered_at'] = known[entry['id']].get('discovered_at', now)
                else:
                    item_report['new'] += 1
                    report['new_candidates'] += 1
                known[entry['id']] = entry
        except Exception as exc:
            item_report['error'] = str(exc)[:200]
        report['accounts'].append(item_report)
    OUT.write_text(json.dumps(sorted(known.values(), key=lambda c: c.get('discovered_at', ''), reverse=True)[:2000], ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    STATUS.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    return report


def _fetch(actor):
    url = 'https://public.api.bsky.app/xrpc/app.bsky.feed.getAuthorFeed?' + urllib.parse.urlencode({'actor': actor, 'filter': 'posts_no_replies', 'limit': 50})
    req = urllib.request.Request(url, headers={'User-Agent': 'ProjectionPublicScheduleBot/1.0'})
    with urllib.request.urlopen(req, timeout=20) as response:
        return json.loads(response.read(2_000_000))


if __name__ == '__main__':
    print(json.dumps(collect(), ensure_ascii=False))

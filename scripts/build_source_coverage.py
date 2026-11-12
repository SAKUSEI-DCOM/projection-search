#!/usr/bin/env python3
"""Generate factual monitoring coverage counts; no network calls or false success."""
import json,pathlib,datetime,os
ROOT=pathlib.Path(__file__).resolve().parents[1]
def read(path,default):
    try:return json.loads((ROOT/path).read_text(encoding='utf-8'))
    except (OSError,ValueError,TypeError):return default

def build():
    roster=read('livers.json',[])
    feeds=read('data/free_feeds.json',[])
    approvals=read('data/wiki_portrait_approvals.json',{})
    portraits=read('data/wiki_portrait_candidates.json',{})
    xstatus=read('data/x_collection_status.json',{})
    # Presence of an X profile URL does not imply any X posts are accessible.
    result={'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
      'liver_total':len(roster),
      'x_profile_links':sum(bool(r.get('x') or r.get('twitter') or r.get('x_url')) for r in roster),
      'x_api_credentials_configured':bool(os.getenv('X_BEARER_TOKEN')),
      'x_posts_automatically_available':bool(xstatus.get('success_count', 0) or xstatus.get('posts_fetched', 0)),
      'x_posts_note':'X profile links alone cannot provide post bodies. API credentials and quota are required; even with credentials, availability depends on the API.',
      'configured_authorized_feeds':len(feeds),
      'wiki_portrait_candidates':len(portraits),
      'wiki_portraits_approved':sum(bool(v.get('approved') and v.get('rights_confirmed_by')) for v in approvals.values() if isinstance(v,dict)),
      'wiki_portraits_displayed':sum(bool(r.get('image')) for r in roster),
      'x_collection_status':xstatus}
    out=ROOT/'data/source_coverage.json';out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return result
if __name__=='__main__':print(json.dumps(build(),ensure_ascii=False))

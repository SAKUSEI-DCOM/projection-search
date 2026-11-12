"""Hourly source coverage report. Never scrapes X or claims inaccessible posts were checked."""
import datetime,json,pathlib,re
ROOT=pathlib.Path(__file__).resolve().parents[1]
JST=datetime.timezone(datetime.timedelta(hours=9))

def handle(url):
    if not isinstance(url,str):return None
    m=re.fullmatch(r'https://(?:www\.)?(?:x\.com|twitter\.com)/([A-Za-z0-9_]{1,15})/?(?:\?.*)?',url.strip(),re.I)
    return m.group(1).lower() if m else None

def report(livers,accounts,feed_status,collection_status,issue_status):
    registered={h.lower() for h in accounts.get('handles',[]) if isinstance(h,str) and re.fullmatch(r'[A-Za-z0-9_]{1,15}',h)}
    members=[]
    for liver in livers:
        h=handle(liver.get('x',''))
        members.append({'name':liver.get('name',''),'x_url':liver.get('x',''),'handle':h,'registered':bool(h and h in registered)})
    feed_list=feed_status.get('feeds',[])
    feeds_ok=sum(1 for f in feed_list if not f.get('error'))
    return {'checked_at':datetime.datetime.now(JST).isoformat(),'cadence':'毎時23分（GitHub Actionsの遅延あり）',
      'liver_count':len(members),'profiles_with_x_url':sum(bool(m['handle']) for m in members),
      'registered_x_handles':len(registered),'feed_sources_configured':len(feed_list),
      'feeds_successfully_fetched':feeds_ok,'official_x_api_configured':bool(collection_status.get('api_configured')),
      'official_x_api_posts_received':collection_status.get('posts_received',0),
      'issue_import_status':issue_status.get('note',''),
      'x_monitoring_active':bool(collection_status.get('api_configured')),
      'notice':'登録したXプロフィールURLだけでは投稿は取得できません。X APIの権限ある接続または許可済みフィードが必要です。',
      'wiki_profile_sync':load('data/wiki_profile_x_report.json',{}),
      'members':members}

def load(name,default):
    try:return json.loads((ROOT/name).read_text(encoding='utf-8'))
    except (OSError,ValueError):return default

def main():
    obj=report(load('livers.json',[]),load('data/x_accounts.json',{}),load('data/free_feed_status.json',{}),load('data/collection_status.json',{}),load('data/github_issue_collection.json',{}))
    (ROOT/'data/hourly_monitor_status.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('X profiles:',obj['profiles_with_x_url'],'/',obj['liver_count'],'| authorized feeds:',obj['feeds_successfully_fetched'],'/',obj['feed_sources_configured'],'| X API:',obj['official_x_api_configured'])
if __name__=='__main__':main()

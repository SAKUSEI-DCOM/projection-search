"""Summarize actually configured input sources and avoid claiming X ingestion without credentials."""
import json,os,pathlib,datetime
ROOT=pathlib.Path(__file__).resolve().parents[1]
def load(path,default):
 try:return json.loads((ROOT/path).read_text(encoding='utf8'))
 except (OSError,ValueError):return default
def count_sources(value):
 if isinstance(value,list):return len(value)
 if isinstance(value,dict):
  for key in ('feeds','sources','calendars'):
   if isinstance(value.get(key),list):return len(value[key])
 return 0
def main():
 report={'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'x_official_api_configured':bool(os.environ.get('X_BEARER_TOKEN')),'rss_sources_configured':count_sources(load('data/free_feeds.json',[])),'calendar_sources_configured':count_sources(load('data/calendar_feeds.json',[])),'note':'Configured source counts do not establish successful data collection. See collection status reports.'}
 (ROOT/'data'/'source_readiness.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()

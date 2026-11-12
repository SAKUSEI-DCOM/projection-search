"""Publish honest data-source health and freshness metadata."""
import json, pathlib, datetime
root=pathlib.Path(__file__).resolve().parents[1]
def load(p, default):
 try:return json.loads((root/p).read_text(encoding="utf-8"))
 except (OSError, ValueError):return default
status=load("data/collection_status.json",{})
sources=load("data/sources.json",[])
candidates=load("candidates.json",[])
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
result={"last_checked_at":now,"schedule":"1時間ごと（毎時23分予定。遅延・スキップの可能性あり）","configured_feeds":len([s for s in sources if s.get("feed_url","").startswith("https://")]),"candidate_count":len(candidates),"x_api_enabled":bool(status.get("api_configured")),"x_posts_received_last_run":status.get("posts_received",0),"x_auto_monitoring_active":bool(status.get("api_configured")) and not bool(status.get("errors")),"feed_errors":status.get("feed_errors",[]),"notice":"X APIなしではX投稿の直接自動監視はできません。配信中表示は予定時刻に基づきます。"}
(root/"data/health.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(result,ensure_ascii=False))

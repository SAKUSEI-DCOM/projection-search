"""Import issue events only after collaborator trust or explicit moderation approval."""
import json,os,pathlib,sys
from collect_github_issues import accepted,extract
from process_inbox import valid
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
 event=json.loads(pathlib.Path(os.environ['GITHUB_EVENT_PATH']).read_text(encoding='utf8'))
 issue=event.get('issue') or {}
 if not accepted(issue):
  print('Issue is not eligible for import; waiting for moderator approval.');return
 row=extract(issue.get('body',''))
 if not valid(row):
  print('Issue form invalid; skipped.');return
 p=ROOT/'data'/'incoming'/('issue-'+str(issue['number'])+'.json')
 p.parent.mkdir(parents=True,exist_ok=True)
 if not p.exists():
  p.write_text(json.dumps(row,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print('Staged approved issue',issue['number'])
if __name__=='__main__':main()

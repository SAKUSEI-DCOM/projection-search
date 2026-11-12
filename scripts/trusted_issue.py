"""Read GitHub issue event from environment, import only repository collaborators' announcements.
The issue form fields are parsed as untrusted text, validated by process_inbox.
"""
import json,os,pathlib,re,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
event=json.loads(pathlib.Path(os.environ['GITHUB_EVENT_PATH']).read_text())
issue=event.get('issue') or {}
if issue.get('author_association') not in ('OWNER','MEMBER','COLLABORATOR'):
 print('Not a trusted repository contributor; ignored.');sys.exit(0)
if '配信告知' not in [x.get('name') for x in issue.get('labels',[])]:
 print('Not a stream announcement issue; ignored.');sys.exit(0)
body=issue.get('body') or ''
def field(name):
 m=re.search(r'^### '+re.escape(name)+r'\s*\n+(.*?)(?=\n### |\Z)',body,re.M|re.S)
 return m.group(1).strip() if m else ''
record={'post_url':field('X投稿URL'),'post_text':field('投稿本文'),'published_at':field('投稿日時（ISO 8601・タイムゾーン付き）'),'author':field('Xユーザー名（@なし）')}
p=ROOT/'data'/'incoming'/('issue-'+str(issue.get('number',0))+'.json')
p.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Staged trusted issue',issue.get('number'))

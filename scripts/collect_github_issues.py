"""Reconcile trusted public GitHub announcement issues hourly (no X scraping).
Trusted contributors qualify, or public issues explicitly marked 掲載承認 by a moderator.
GitHub API is the source; untrusted submissions never become schedule candidates.
"""
import datetime,json,os,pathlib,re,urllib.request,urllib.error
ROOT=pathlib.Path(__file__).resolve().parents[1]
TRUSTED={'OWNER','MEMBER','COLLABORATOR'}
def extract(body):
 def field(name):
  m=re.search(r'^### '+re.escape(name)+r'\s*\n+(.*?)(?=\n### |\Z)',body or '',re.M|re.S)
  return m.group(1).strip() if m else ''
 return {'post_url':field('X投稿URL'),'post_text':field('投稿本文'),'published_at':field('投稿日時（ISO 8601・タイムゾーン付き）'),'author':field('Xユーザー名（@なし）')}
def accepted(issue):
 # Only moderator-applied approval labels permit publication.
 return (any(x.get('name')=='掲載承認' for x in issue.get('labels',[])) and
         any(x.get('name')=='配信告知' for x in issue.get('labels',[])) and
         'pull_request' not in issue and issue.get('state')=='open')
def fetch(repo,token):
 if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',repo):raise ValueError('invalid repo')
 result=[]
 for page in range(1,6):
  url=f'https://api.github.com/repos/{repo}/issues?state=open&labels=%E9%85%8D%E4%BF%A1%E5%91%8A%E7%9F%A5&per_page=100&page={page}'
  headers={'Accept':'application/vnd.github+json','User-Agent':'projection-schedule-collector','X-GitHub-Api-Version':'2022-11-28'}
  if token:headers['Authorization']='Bearer '+token
  with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=20) as resp:items=json.load(resp)
  if not isinstance(items,list):raise ValueError('unexpected response')
  result.extend(items)
  if len(items)<100:break
 return result
def main():
 repo=os.environ.get('GITHUB_REPOSITORY','').strip()
 report={'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':'GitHub public issues','repository':repo,'accepted':0,'rejected':0,'errors':[]}
 if not repo:
  report['errors'].append('GITHUB_REPOSITORY is not set; no remote collection attempted')
 else:
  try:
   issues=fetch(repo,os.environ.get('GITHUB_TOKEN',''))
   for issue in issues:
    if not accepted(issue):report['rejected']+=1;continue
    row=extract(issue.get('body',''))
    # Validate against the same strict URL/author/timestamp rules as local inbox.
    from process_inbox import valid
    if not valid(row):report['rejected']+=1;continue
    file=ROOT/'data'/'incoming'/f"issue-{issue['number']}.json"
    file.parent.mkdir(parents=True,exist_ok=True)
    if not file.exists():
     file.write_text(json.dumps(row,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    report['accepted']+=1
  except (urllib.error.URLError,ValueError,KeyError,OSError) as exc:
   report['errors'].append(str(exc)[:250])
 out=ROOT/'data'/'github_issue_collection.json'
 out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()

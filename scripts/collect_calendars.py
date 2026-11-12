"""Import explicitly authorized public iCalendar (.ics) feeds without scraping X.
The feed owner must consent to republication of its schedule. Never ingest private URLs.
"""
import datetime, hashlib, json, pathlib, re, urllib.request
ROOT=pathlib.Path(__file__).resolve().parents[1]
JST=datetime.timezone(datetime.timedelta(hours=9))
def unfold(s):return re.sub(r'\r?\n[ \t]','',s)
def parse_ics(s):
    for block in re.findall(r'BEGIN:VEVENT\r?\n(.*?)END:VEVENT',unfold(s),re.S):
        data={}
        for line in block.splitlines():
            if ':' not in line:continue
            key,val=line.split(':',1);data[key.split(';')[0].upper()]=val.replace('\\n',' ').replace('\\,',',')
        if 'DTSTART' in data and 'UID' in data:yield data
def date_iso(raw):
    try:
        if re.fullmatch(r'\d{8}T\d{6}Z',raw):return datetime.datetime.strptime(raw,'%Y%m%dT%H%M%SZ').replace(tzinfo=datetime.timezone.utc).astimezone(JST).isoformat()
        if re.fullmatch(r'\d{8}T\d{6}',raw):return datetime.datetime.strptime(raw,'%Y%m%dT%H%M%S').replace(tzinfo=JST).isoformat()
    except ValueError:pass
    return None

def main():
    feeds=json.loads((ROOT/'data/calendar_feeds.json').read_text(encoding='utf8'))
    target=ROOT/'schedules.json'; current=json.loads(target.read_text(encoding='utf8'))
    known={x.get('id') for x in current}
    report={'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'feeds':[],'new':0,'updated':0,'cancelled':0}
    for feed in feeds:
        url=feed.get('url','');name=feed.get('liver_name','')
        result={'name':name,'new':0,'updated':0,'cancelled':0}
        if not (feed.get('owner_authorized') is True and url.startswith('https://') and name):
            result['error']='Owner authorization, HTTPS URL and liver name required';report['feeds'].append(result);continue
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'ProjectionCalendarReader/1.0'})
            with urllib.request.urlopen(req,timeout=15) as response:body=response.read(1_000_000).decode('utf8-sig')
            if 'BEGIN:VCALENDAR' not in body:raise ValueError('Not an iCalendar feed')
            seen=set()
            for event in list(parse_ics(body))[:250]:
                dt=date_iso(event['DTSTART']);
                if not dt:continue
                start=datetime.datetime.fromisoformat(dt)
                now=datetime.datetime.now(JST)
                if not now-datetime.timedelta(days=1)<=start<=now+datetime.timedelta(days=90):continue
                ident='calendar-'+hashlib.sha256((url+event['UID']).encode()).hexdigest()[:20]
                seen.add(ident)
                old=next((x for x in current if x.get('id')==ident),None)
                cancelled=event.get('STATUS','').upper()=='CANCELLED'
                if old:
                    if cancelled:
                        if old.get('status')!='cancelled':
                            old['status']='cancelled';old['verification']='公開カレンダーで中止を確認';result['cancelled']+=1;report['cancelled']+=1
                    elif old.get('start')!=dt or old.get('title')!=event.get('SUMMARY','配信予定')[:120] or old.get('status')=='cancelled':
                        old.update(start=dt,title=event.get('SUMMARY','配信予定')[:120],status='tentative',verification='公開カレンダーで変更を検出・要確認')
                        result['updated']+=1;report['updated']+=1
                    continue
                if cancelled:continue
                current.append({'id':ident,'name':name,'start':dt,'title':event.get('SUMMARY','配信予定')[:120], 'source':url,'source_url':url,'status':'tentative','verification':'公開カレンダー由来・要確認','auto_imported':True})
                known.add(ident);result['new']+=1;report['new']+=1
            # Do not delete events absent from a feed: some feeds only expose a rolling window.
        except Exception as exc:result['error']=str(exc)[:160]
        report['feeds'].append(result)
    target.write_text(json.dumps(current,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    (ROOT/'data/calendar_feed_status.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
if __name__=='__main__':main()

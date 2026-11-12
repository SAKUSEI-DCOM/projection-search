#!/usr/bin/env python3
"""Export transparent data-quality audit, without inventing portraits or dates."""
import json,csv,pathlib,datetime
root=pathlib.Path(__file__).resolve().parents[1]
rows=json.loads((root/'livers.json').read_text(encoding='utf-8'))
fields=['name','generation','status','has_portrait','has_x','has_iriam','has_debut_date','wiki_url','x_url','portrait_url']
out=root/'data/portrait_audit.csv'
with out.open('w',newline='',encoding='utf-8-sig') as f:
 writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
 for r in rows:
  writer.writerow(dict(name=r.get('name',''),generation=r.get('generation',''),status=r.get('status',''),has_portrait=bool(r.get('image')),has_x=bool(r.get('x')),has_iriam=bool(r.get('iriam')),has_debut_date=bool(r.get('debut')),wiki_url=r.get('wiki',''),x_url=r.get('x',''),portrait_url=r.get('image','')))
print('Audited',len(rows),'livers; portrait count',sum(bool(r.get('image')) for r in rows))

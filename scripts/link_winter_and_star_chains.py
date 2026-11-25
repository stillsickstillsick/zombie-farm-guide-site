#!/usr/bin/env python3
"""Connect source-supported locations and story-chain boundaries, not object coordinates."""
import json,pathlib
P=pathlib.Path(__file__).resolve().parents[1];p=P/'data/quests.json';q=json.loads(p.read_text());Q={x['slug']:x for x in q};C={}
for cat in ('locations','buildings'):
 for x in json.loads((P/'data'/f'{cat}.json').read_text()):C[cat,x['slug']]=x
rows=[('unesennye-vetrom-1-2016-4196','locations','zombicity-island-4168'),('unesennye-vetrom-1-2016-4197','locations','zombicity-island-4168'),('unesennye-vetrom-1-2016-4198','locations','zombicity-island-4168'),('zvezdnyy-urozhay-2-2016-4340','locations','zombicity-island-4317'),('zvezdnyy-urozhay-2-2016-4340','locations','zombicity-island-4335'),('zvezdnyy-urozhay-2-2016-4340','buildings','khizhina-prishelcev-2016'),('zvezdnyy-urozhay-2-2016-4342','buildings','drevniy-tonnel-2016'),('zvezdnyy-urozhay-2-2016-3776','buildings','drevniy-tonnel-2016'),('zvezdnyy-urozhay-2-2016-3776','locations','zombicity-island-4336'),('zvezdnyy-urozhay-2-2016-4346','locations','zombicity-island-4334')]
for a,c,b in rows:
 x=Q[a];y=C[c,b]
 if not any(z.get('category')==c and z.get('slug')==b for z in x['links']):x['links'].append({'category':c,'slug':b,'name':y['name'],'relation':'локация или постройка задания'})
for a,b in [('unesennye-vetrom-1-2016-4198','unesennye-vetrom-2-2016-4221'),('zvezdnyy-urozhay-1-2016-4332','zvezdnyy-urozhay-2-2016-4338')]:
 x=Q[a];y=Q[b]
 if not any(z.get('category')=='quests' and z.get('slug')==b for z in x['links']):x['links'].append({'category':'quests','slug':b,'name':y['name'],'relation':'следующая часть истории'})
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n');print('Созданы связи между линиями, островами и постройками')

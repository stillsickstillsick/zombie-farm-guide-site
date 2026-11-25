#!/usr/bin/env python3
"""Connect quest destinations and transports only where corroborated by texts/index."""
import json,pathlib
P=pathlib.Path(__file__).resolve().parents[1];p=P/'data/quests.json';q=json.loads(p.read_text());I={x['slug']:x for x in q};objs={}
for cat in ('locations','buildings'):
 for x in json.loads((P/'data'/f'{cat}.json').read_text()):objs[cat,x['slug']]=x
rows=[('unesennye-vetrom-3-2016-4273','locations','zombicity-island-4210'),('unesennye-vetrom-3-2016-4276','locations','zombicity-island-4210'),('unesennye-vetrom-3-2016-4284','locations','zombicity-island-4211'),('unesennye-vetrom-3-2016-4289','locations','zombicity-island-4211'),('unesennye-vetrom-3-2016-4290','locations','zombicity-island-4210'),('unesennye-vetrom-3-2016-4295','locations','zombicity-island-4211'),('unesennye-vetrom-3-2016-4297','locations','zombicity-island-4210'),('zvezdnyy-urozhay-1-2016-4324','buildings','lodka-strannika-2016'),('zvezdnyy-urozhay-1-2016-4325','buildings','lodka-strannika-2016'),('zvezdnyy-urozhay-1-2016-4326','locations','zombicity-island-4316'),('zvezdnyy-urozhay-1-2016-4326','buildings','lodka-strannika-2016'),('zvezdnyy-urozhay-1-2016-4328','buildings','staraya-raketa-2016'),('zvezdnyy-urozhay-1-2016-4329','buildings','staraya-raketa-2016'),('zvezdnyy-urozhay-1-2016-4329','locations','zombicity-island-4317')]
for a,cat,slug in rows:
 x=I[a];y=objs[cat,slug]
 if not any(i.get('slug')==slug and i.get('category')==cat for i in x['links']):x['links'].append({'category':cat,'slug':slug,'name':y['name'],'relation':'локация или транспорт задания'})
for a,b in [('unesennye-vetrom-2-2016-4233','unesennye-vetrom-3-2016-4273')]:
 x=I[a];y=I[b]
 if not any(i.get('slug')==b for i in x['links']):x['links'].append({'category':'quests','slug':b,'name':y['name'],'relation':'следующая часть истории'})
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n');print('Связи добавлены; исходные координаты не выводились')

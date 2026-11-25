#!/usr/bin/env python3
"""Link winter quest steps to named destinations and audit the 2016 ticket count."""
import re,json,pathlib
P=pathlib.Path(__file__).resolve().parents[1];p=P/'data/quests.json';q=json.loads(p.read_text());I={x['slug']:x for x in q};locations={x['slug']:x for x in json.loads((P/'data/locations.json').read_text())}
for n,ls in [(4224,['zombicity-island-4168','zombicity-island-4209']),(4225,['zombicity-island-4209']),(4227,['zombicity-island-4209']),(4232,['zombicity-island-4209','zombicity-island-4210']),(4233,['zombicity-island-4209','zombicity-island-4210'])]:
 x=I[f'unesennye-vetrom-2-2016-{n}']
 for slug in ls:
  if not any(l.get('slug')==slug and l.get('category')=='locations' for l in x['links']):x['links'].append({'category':'locations','slug':slug,'name':locations[slug]['name'],'relation':'локация задания'})
a=[x for x in q if x['slug'].startswith('don-sanches-priklyuchenie-2015-')];total=0;count=0
for x in a:
 reward=x['prior_records'][0]['fields']['Награда'];m=re.search(r'(\d+)\s+Билет 2016',reward)
 if m:total+=int(m[1]);count+=1
assert len(a)==30 and total==32 and count==22,(len(a),total,count)
x=I['don-sanches-priklyuchenie-2015-4074'];x['prior_records'][0]['fields']['Сверка наград линии']='Сумма явно указанных Билетов 2016 в 30 отдельных карточках — 32, они перечислены в 22 заданиях. Источники принадлежат одному сайту; это не независимое подтверждение, а проверка арифметики опубликованного перечня.'
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n');print('Проверены 30 заданий:',count,'наград с билетами, всего',total,'билета')

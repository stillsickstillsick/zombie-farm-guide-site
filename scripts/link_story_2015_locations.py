#!/usr/bin/env python3
"""Explicit source-supported links, never inferred object coordinates."""
import json,pathlib
P=pathlib.Path(__file__).resolve().parents[1];p=P/'data/quests.json';q=json.loads(p.read_text());I={x['slug']:x for x in q};loc={x['slug']:x for x in json.loads((P/'data/locations.json').read_text())}
for quest,where in [('gribnoy-sezon-2015-3889','gribnaya-polyana-2015'),('gribnoy-sezon-2015-3890','gribnaya-polyana-2015'),('den-rozhdeniya-zombi-2015-4046','zombicity-island-4040')]:
 x=I[quest];y=loc[where]
 if not any(a.get('slug')==where and a.get('category')=='locations' for a in x['links']):x['links'].append({'category':'locations','slug':where,'name':y['name'],'relation':'локация задания'})
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n');print('Связаны три задания и две локации без указания исходных координат')

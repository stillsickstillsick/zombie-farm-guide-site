#!/usr/bin/env python3
"""Check the index's second-series 42-ticket claim against individual articles."""
import pathlib,json,re
p=pathlib.Path(__file__).resolve().parents[1]/'data/quests.json';q=json.loads(p.read_text());a=[x for x in q if x['slug'].startswith('mylnaya-opera-2-2015-')];total=0
for x in a:
 r=x['prior_records'][0]['fields']['Награда'];m=re.search(r'(\d+)\s+Билет в кино',r)
 if m:total+=int(m[1])
assert len(a)==31 and total==42,(len(a),total)
x=next(x for x in a if x['slug']=='mylnaya-opera-2-2015-3794');x['prior_records'][0]['fields']['Проверка общей награды']='Индекс второй серии указывает 42 Билета в кино за всю линию; сумма количеств в 31 отдельной статье также равна 42. Источники принадлежат одному сайту и не считаются независимыми.'
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n');print('Заданий:',len(a),'билетов:',total)

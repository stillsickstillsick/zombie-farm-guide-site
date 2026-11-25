#!/usr/bin/env python3
"""Retain a source mismatch rather than silently merge contradictory story text."""
import pathlib,json,sys
from bs4 import BeautifulSoup
P=pathlib.Path(__file__).resolve().parents[1];cache=pathlib.Path(sys.argv[1]);p=P/'data/quests.json';q=json.loads(p.read_text());x=next(x for x in q if x['slug']=='biznes-tropiki');s=BeautifulSoup((cache/'pages/2684.html').read_bytes(),'html.parser');t=s.find('h1').find_parent('table');text=t.get_text(' ',strip=True)
assert all(v in text for v in ['80 Костирузы','10 Чёрных сердец','Бизнес-Центр','250 Опыт','1 Невод','10000 Монеты','Университет'])
url=next(z['final_url'] for z in map(json.loads,(cache/'download-log.jsonl').read_text().splitlines()) if z.get('id')==2684 and z.get('status')=='downloaded_unreviewed')
rid='bulk-moy-quest-2684-disagreement'
if not any(r.get('original_id')==rid for r in x['prior_records']):
 x['prior_records'].append({'original_id':rid,'original_category':'Задание — отдельная статья, текст противоречив','version':'браузерная игра; платформа и редакция требуют сверки','date':'дата в URL статьи; время последней правки не установлено','fields':{'Текст отдельной статьи':text,'Сопоставление':'Цели и награда совпадают с карточкой ZOMBIA, но описание и текст завершения говорят об Университете, а не о Бизнес-центре. Это внутреннее противоречие статьи; возможна ошибка редактирования, причина не установлена.'},'confidence':'Сопоставление по совпадению трёх целей и награды; описание противоречит целям. Источники могут зависеть друг от друга.'});x['sources'].append({'url':url,'label':'Zombie-island: статья с противоречивым описанием'})
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n');print('Зафиксировано противоречие: Бизнес тропики / Университет')

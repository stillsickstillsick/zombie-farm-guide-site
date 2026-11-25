#!/usr/bin/env python3
"""Merge reviewed exact-identity 2014 quest articles; retain prior versions separately.
Cached research pages are private; pass the cache directory as argument."""
import sys,json,re,pathlib,datetime
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
P=pathlib.Path(__file__).resolve().parents[1];cache=pathlib.Path(sys.argv[1]); path=P/'data/quests.json';quests=json.loads(path.read_text()); normalize=lambda s:re.sub(r'[^а-яa-z0-9]+','',s.lower().replace('ё','е'))
log=[json.loads(x) for x in (cache/'download-log.jsonl').read_text().splitlines()];count=0
for item in log:
 if item.get('status')!='downloaded_unreviewed' or not item.get('title','').startswith('Прохождение квеста '):continue
 name=item['title'].replace('Прохождение квеста ','',1);matches=[q for q in quests if normalize(q['name'])==normalize(name)]
 if len(matches)!=1:print('SKIP ambiguous',item['id'],name,len(matches));continue
 q=matches[0];soup=BeautifulSoup((cache/'pages'/f"{item['id']}.html").read_bytes(),'html.parser');h=soup.find('h1');table=h.find_parent('table') if h else None
 if not table:continue
 text=table.get_text(' ',strip=True);m=re.search(r'Задание:\s*(.+?)(?=\s+1\.)',text)
 if not m:print('SKIP missing description',item['id']);continue
 description=m.group(1); prior=' '.join(str(v) for r in q.get('prior_records',[]) for v in r.get('fields',{}).values());
 # Match the narrative against previous entry to avoid conflating same-named quests.
 if normalize(description[:60]) not in normalize(prior):print('SKIP identity',item['id'],name);continue
 goals=[];reward=[]
 for tr in table.find_all('tr'):
  td=tr.find_all('td',recursive=False)
  if len(td)>=3 and re.fullmatch(r'\d+\.',td[0].get_text(' ',strip=True)):goals.append(td[-1].get_text(' ',strip=True))
  if 'Награда за прохождение задания' in tr.get_text(' ',strip=True):reward.append(tr.get_text(' ',strip=True).replace('Награда за прохождение задания:','').strip())
 if not goals or not reward:print('SKIP incomplete',item['id'],name);continue
 url=item['final_url'];rid=f"bulk-moy-quest-{item['id']}"
 if not any(x.get('original_id')==rid for x in q.setdefault('prior_records',[])):
  q['prior_records'].append({'original_id':rid,'original_category':'Задание — отдельная статья','version':'браузерная игра; платформа и редакция требуют сверки','date':'дата в URL статьи; время последней правки не установлено','fields':{'Цели и пропуск':' | '.join(f'{i}. {g}' for i,g in enumerate(goals,1)),'Награда согласно статье':' | '.join(reward),'Оговорка':'Цветные значки цены пропуска в статье показывают зомбаксы; исходное перечисление наград сохранено отдельно от других источников — возможны разночтения.'},'confidence':'Фанатский источник; текст сопоставлен с описанием существующего квеста, независимость и соответствие редакциям не установлены.'})
  q.setdefault('sources',[]).append({'url':url,'label':'Zombie-island: отдельная статья квеста'});count+=1;print('ADDED',item['id'],name)
path.write_text(json.dumps(quests,ensure_ascii=False,indent=2)+'\n');print('updated',count)

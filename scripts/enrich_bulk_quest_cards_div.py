#!/usr/bin/env python3
"""Enrich div-format quest articles, conservative matching using existing narrative and goals."""
import sys,json,re,pathlib
from bs4 import BeautifulSoup
P=pathlib.Path(__file__).resolve().parents[1];cache=pathlib.Path(sys.argv[1]);data=P/'data/quests.json';qs=json.loads(data.read_text());normalize=lambda s:re.sub(r'[^а-яa-z0-9]+',' ',s.lower().replace('ё','е')).strip();compact=lambda s:normalize(s).replace(' ','');tokens=lambda s:set(w for w in normalize(s).split() if len(w)>4 or w.isdigit());count=0
for line in (cache/'download-log.jsonl').read_text().splitlines():
 a=json.loads(line)
 if a.get('status')!='downloaded_unreviewed' or not a.get('title','').startswith('Прохождение квеста '):continue
 name=a['title'].replace('Прохождение квеста ','',1);matches=[q for q in qs if normalize(q['name'])==normalize(name)]
 if not matches:continue
 soup=BeautifulSoup((cache/'pages'/f"{a['id']}.html").read_bytes(),'html.parser');d=soup.select_one('div.kvest_ind')
 if not d or not d.find('ol'):continue
 p=d.select_one('p.kvest_ind_p');narrative=p.get_text(' ',strip=True).removeprefix('Задание:').strip() if p else ''
 goals=[li.get_text(' ',strip=True) for li in d.find('ol').find_all('li',recursive=False)];reward=d.find_next_sibling('div',class_='kvest_ind_nagr')
 if not narrative or not goals or not reward:continue
 candidates=[]
 for q in matches:
  orig=' '.join(str(v) for r in q.get('prior_records',[]) if r.get('original_id','').startswith('zombia-quest-') for v in r.get('fields',{}).values())
  if compact(narrative[:60]) not in compact(orig):continue
  candidates.append((len(tokens(' '.join(goals)) & tokens(orig)),q))
 candidates.sort(key=lambda x:x[0],reverse=True)
 if not candidates:print('SKIP narrative',a['id'],name);continue
 if len(matches)>1 and (len(candidates)>1 and (candidates[0][0]<8 or candidates[0][0]-candidates[1][0]<4)):
  print('SKIP ambiguous',a['id'],name,[(score,q['slug']) for score,q in candidates]);continue
 q=candidates[0][1];rid='bulk-moy-quest-'+str(a['id']);
 if any(r.get('original_id')==rid for r in q.get('prior_records',[])):continue
 rewardtext=reward.get_text(' ',strip=True).replace('Награда за прохождение задания:','').strip()
 q.setdefault('prior_records',[]).append({'original_id':rid,'original_category':'Задание — отдельная статья','version':'браузерная игра; платформа и редакция требуют сверки','date':'дата публикации в URL; время поздних правок неизвестно','fields':{'Цели и пропуск':' | '.join(f'{i}. {g}' for i,g in enumerate(goals,1)),'Награда согласно статье':rewardtext,'Оговорка':'При отсутствии цены пропуска нельзя заключать, что пропуск недоступен. Данные сохранены отдельно от других источников; возможны разные редакции.'},'confidence':'Фанатский источник; совпадение оценено по описанию и целям. Зависимость источников и версии требуют проверки.'});q.setdefault('sources',[]).append({'url':a['final_url'],'label':'Zombie-island: отдельная статья квеста'});count+=1;print('ADDED',a['id'],name,q['slug'])
data.write_text(json.dumps(qs,ensure_ascii=False,indent=2)+'\n');print('updated',count)

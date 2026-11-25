"""Historical collection digging table, My World; retain uncertainty in source text."""
from pathlib import Path
import json,requests,bs4,re
P=Path(__file__).resolve().parents[1];url='https://zombiemail.do.am/publ/instrukcii/kollekcii/kollekcii/2-1-0-3';q=requests.get(url,timeout=10);q.raise_for_status();s=bs4.BeautifulSoup(q.content,'html.parser');d=json.loads((P/'data/collections.json').read_text());norm=lambda t:re.sub(r'\s+',' ',t.replace('ё','е').casefold()).strip();aliases={'Люксорская коллекция':'Луксорская коллекция','Коллекция Хеллоуин':'Коллекция Хэллоуина'};n=0;unmatched=[]
for tr in s.select('tr'):
 cells=tr.find_all('td',recursive=False)
 if len(cells)!=3:continue
 values=[c.get_text(' ',strip=True) for c in cells];name=values[0].strip(' "«»\u00a0')
 if not (values[0].startswith('"') and 'коллекц' in name.lower()):continue
 target=aliases.get(name,name);matches=[x for x in d if norm(x['name'])==norm(target)]
 if len(matches)!=1:unmatched.append(name);continue
 e=matches[0];rid='zombiemail-collection-'+e['slug'];rec={'original_id':rid,'original_category':'Коллекции','version':'Мой Мир (Mail.ru); историческая таблица','date':'дата редакции не установлена','fields':{'Название в источнике':name,'Где копать':values[1],'Награда':values[2]},'confidence':'Источник сам использует знаки вопроса; не следует считать такие места подтверждёнными. Возможны изменения патча и платформы; независимость от других справочников не доказана.'};e.setdefault('prior_records',[]);e['prior_records']=[x for x in e['prior_records'] if x.get('original_id')!=rid]+[rec]
 if not any(x['url']==url for x in e['sources']):e['sources'].append({'url':url,'label':'Zombiemail: строка таблицы коллекций; Мой Мир'})
 n+=1
(P/'data/collections.json').write_text(json.dumps(d,ensure_ascii=False,indent=2));src=json.loads((P/'data/sources.json').read_text())
for e in src:
 if e['number']==10 and '29 строк коллекций' not in e['summary']:e['summary']+=' Перенесены 29 строк коллекций для Моего Мира, включая указанные источником сомнения о местах копания.'
(P/'data/sources.json').write_text(json.dumps(src,ensure_ascii=False,indent=2));print('imported',n,'unmatched',unmatched)

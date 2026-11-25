"""Import the second part of the historical My World building table."""
import requests,bs4,json,re
from pathlib import Path
P=Path(__file__).resolve().parents[1];url='https://zombiemail.do.am/publ/instrukcii/postrojki/postrojki_2_chast/3-1-0-32';r=requests.get(url,timeout=10);r.raise_for_status();s=bs4.BeautifulSoup(r.content,'html.parser');tables=[t for t in s.select('table') if len(t.select('tr'))==26 and 'Останкино' in t.get_text(' ',strip=True) and 'Пирамида Майя' in t.get_text(' ',strip=True)];assert len(tables)==1; data=json.loads((P/'data/buildings.json').read_text());normalize=lambda x:re.sub(r'\s+',' ',x.casefold().replace('ё','е')).strip();aliases={'Флаг Беларуси':'Флаг Белоруси','Пристань "На остров любви"':'Пристань на Остров Любви','Пристань "На остров Майя"':'Пристань на Остров Майя'};n=0;skips=[]
for tr in tables[0].select('tr'):
 c=tr.find_all(['td','th'],recursive=False)
 if len(c)!=2:continue
 left=c[0].get_text('\n',strip=True);right=c[1].get_text('\n',strip=True)
 if not left or not right or 'Стадии строительства' not in right:continue
 name=left.split('\n')[0];target=aliases.get(name,name);matches=[e for e in data if normalize(e['name'])==normalize(target)]
 if len(matches)!=1:skips.append(name);continue
 e=matches[0];rid='zombiemail-building-part2-'+e['slug'];rec={'original_id':rid,'original_category':'Постройки','version':'Мой Мир (Mail.ru), историческая таблица','date':'дата редакции не установлена','fields':{'Название и первая колонка источника':left,'Опыт, стадии, производство и модернизация':right},'confidence':'Таблица источника; обозначения валют/уровней могут быть пиктограммами и в тексте отсутствовать. Сопоставление названий пристаней и флага Беларуси выполнено по названию и требует сверки.'};e.setdefault('prior_records',[]);e['prior_records']=[x for x in e['prior_records'] if x.get('original_id')!=rid]+[rec]
 if not any(t.get('url')==url for t in e['sources']):e['sources'].append({'url':url,'label':'Zombiemail: таблица построек, часть 2; версия Мой Мир'})
 n+=1
(P/'data/buildings.json').write_text(json.dumps(data,ensure_ascii=False,indent=2));src=json.loads((P/'data/sources.json').read_text())
for e in src:
 if e['number']==10 and '21 строка второй части' not in e['summary']:e['summary']+=' Прочитана 21 строка второй части таблицы построек Мой Мир; числовые обозначения-пиктограммы требуют сверки.'
(P/'data/sources.json').write_text(json.dumps(src,ensure_ascii=False,indent=2));print('rows imported',n,'unmatched',skips)

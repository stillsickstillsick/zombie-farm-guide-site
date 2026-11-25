"""Read part 1 of Mail.ru historical building table, retaining version and original row text."""
import json,requests,bs4,re
from pathlib import Path
P=Path(__file__).resolve().parents[1];url='https://zombiemail.do.am/publ/3-1-0-31';q=requests.get(url,timeout=10);q.raise_for_status();s=bs4.BeautifulSoup(q.content,'html.parser');tables=[t for t in s.select('table') if 'Склеп' in t.get_text(' ',strip=True) and 'Пирамида' in t.get_text(' ',strip=True)];t=min(tables,key=lambda t:len(t.get_text()));data=json.loads((P/'data/buildings.json').read_text());n=0;skips=[]
for row in t.select('tr'):
 c=row.find_all(['td','th'],recursive=False)
 if len(c)!=2:continue
 text=c[0].get_text('\n',strip=True); detail=c[1].get_text('\n',strip=True)
 if not text or not detail:continue
 name=text.split('\n')[0].strip(); matches=[e for e in data if e['name'].casefold().replace('ё','е')==name.casefold().replace('ё','е')]
 if len(matches)!=1:skips.append(name);continue
 e=matches[0];rid='zombiemail-building-'+e['slug'];e.setdefault('prior_records',[])
 record={'original_id':rid,'original_category':'Постройки','version':'Мой Мир (Mail.ru), историческая таблица','date':'дата редакции таблицы не установлена','fields':{'Название и данные первой колонки':text,'Опыт, стадии, производство и модернизация':detail},'confidence':'Текст таблицы Мой Мир. Некоторые обозначения валют и уровней на странице являются изображениями и могут быть потеряны при извлечении. Источники не обязательно независимы.'}
 e['prior_records']=[x for x in e['prior_records'] if x.get('original_id')!=rid]+[record]
 if not any(x.get('url')==q.url for x in e['sources']):e['sources'].append({'url':q.url,'label':'Zombiemail: строка таблицы построек, часть 1, версия Мой Мир'})
 n+=1
(P/'data/buildings.json').write_text(json.dumps(data,ensure_ascii=False,indent=2));src=json.loads((P/'data/sources.json').read_text())
for e in src:
 if e['number']==10:e['summary']+=' Прочитана первая часть таблицы построек Мой Мир: 13 строк перенесены в карточки; обозначения на рисунках нуждаются в сверке.'
(P/'data/sources.json').write_text(json.dumps(src,ensure_ascii=False,indent=2));print('rows',n,'not matched',skips)

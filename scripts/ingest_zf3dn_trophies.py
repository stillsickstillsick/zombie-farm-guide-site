#!/usr/bin/env python3
import json,re,requests,bs4,concurrent.futures
from pathlib import Path
from urllib.parse import urljoin
P=Path(__file__).resolve().parents[1];p=P/'data/eggs-trophies.json';data=json.loads(p.read_text());by={x['slug']:x for x in data}
mapping={'НЕОНОВЫЙ ЩИТ':'neonovyy-shchit','ВЛЮБЛЕННЫЕ':'vlyublennye-trofey','ЧАСЫ':'chasy-trofey','СИРЕНЫ':'sireny-trofey','ЦАРЬ ЛЕВ':'tsar-lev-trofey','ЦАРЬ-ПУШКА':'tsar-pushka-trofey','ФОНТАН':'zolotoy-fontan-trofey','ЗОЛОТОЙ РОСТОК':'zolotoy-rostok-trofey','БЕГЕМОТ':'begemot-trofey','ФЛАГ МАНЬЯКА':'flag-manyaka-trofey','МЫШКА ПОВЕСИЛАСЬ':'myshka-trofey','САМОВАР':'samovar-trofey','ОСТОРОЖНО СЛОН':'ostoro-no-slon-trofey','ЗОЛОТОЙ МИЛЛИАРД':'milliarder-trofey'}
entries=[]
for n in ['16','16-2']:
 u='https://zf.3dn.ru/publ/trofei/'+n;r=requests.get(u,timeout=20);r.raise_for_status();s=bs4.BeautifulSoup(r.content,'html.parser')
 entries += [(h.get_text(strip=True),urljoin(u,h['href'])) for h in s.select('h1 a')]
def fetch(entry):
 name,u=entry
 try:
  r=requests.get(u,timeout=20);r.raise_for_status();s=bs4.BeautifulSoup(r.content,'html.parser');d=s.select_one('td.eText');txt=d.get_text(' ',strip=True) if d else '';date=re.search(r'\(\d{2}\.\d{2}\.\d{4}\)',s.get_text(' ',strip=True));return name,u,txt,date.group(0)[1:-1] if date else 'дата публикации не найдена'
 except Exception as e:return name,u,'','ошибка: '+str(e)[:150]
count=0
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
 results=list(ex.map(fetch,entries))
for name,u,txt,date in results:
 if name not in mapping or not txt:print('skip',name,date);continue
 slug=mapping[name];x=by[slug];note='Изображения в источнике могут содержать дополнительную информацию, текст не описывает весь трофей; страница указывает связь с zombi-ferma.ru, независимость не доказана.'
 if name=='ЗОЛОТОЙ МИЛЛИАРД':note+=' Источник называет награду «Золотой миллиард», квест — «Миллиардер»; сопоставление с карточкой трофея предварительное. Утверждение о списании монет требует проверки.'
 if name=='ФОНТАН':note+=' В каталоге заголовок «Фонтан», в тексте — «Золотой фонтан»; сопоставление сделано по тексту.'
 if name=='МЫШКА ПОВЕСИЛАСЬ':note+=' Название в карточке сокращено; сопоставление предварительное.'
 rid='zf3dn-trophy-'+slug
 rec={'original_id':rid,'original_category':'Трофеи','version':'браузерная игра, платформа не указана','date':date+' — дата публикации; дата редакции неизвестна','fields':{'Текст статьи':txt},'confidence':note+' Условия и советы исторические, могут измениться в других версиях.'}
 if not any(s['url']==u for s in x['sources']):x['sources'].append({'url':u,'label':'ZF.3dn: отдельная страница трофея'})
 x.setdefault('prior_records',[]);x['prior_records']=[r for r in x['prior_records'] if r.get('original_id')!=rid]+[rec];count+=1
p.write_text(json.dumps(data,ensure_ascii=False,indent=2));print('catalog pages 2; checked',len(results),'added:',count)

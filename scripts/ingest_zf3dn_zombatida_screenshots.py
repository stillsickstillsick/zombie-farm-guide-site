#!/usr/bin/env python3
"""Fourteen screenshots: exact explicit quest mapping, original bytes, sha256 dedup."""
import requests,bs4,json,hashlib,concurrent.futures
from urllib.parse import urljoin
from pathlib import Path
P=Path(__file__).resolve().parents[1];p=P/'data/quests.json';a=json.loads(p.read_text());by={x['slug']:x for x in a};items=[]
mp={'CУВЕНИРЫ':'suveniry','ЗАГАДОЧНЫЙ ПРОФЕССОР':'zagadochnyy-professor','СОКРОВИЩЕ ЗОМБАТИДЫ':'sokrovishche-zombatidy','ХРАМ':'khram','СТИХИ':'stikhii','МЕХАНИЗМ':'mekhanizm','ВОДОРОСЛИ':'vodorosli','НА ДНЕ':'na-dne','ПОГРУЖЕНИЕ':'pogru-enie','ДРУЖНАЯ КОМАНДА':'dru-naya-komanda','ВЗАИМОПОМОЩЬ':'vzaimopomoshch','ЗАДАЧА ЭКСПЕДИЦИИ':'zadachi-ekspeditsii','ПРИЛЕЖНЫЙ УЧЕНИК':'prile-nyy-uchenik','УЧЕНЬЕ-СВЕТ':'uchene-svet'}
for pg in ('8','8-2'):
 u='https://zf.3dn.ru/publ/kvesty/'+pg;r=requests.get(u,timeout=20);r.raise_for_status();s=bs4.BeautifulSoup(r.content,'html.parser')
 for h in s.select('h1 a'):
  title=h.get_text(strip=True)
  if title in mp:items.append((title,urljoin(u,h['href']),mp[title]))
assert len(items)==14
known={hashlib.sha256(f.read_bytes()).hexdigest():f for f in (P/'img').rglob('*') if f.is_file()}
def get(item):
 name,u,slug=item
 try:
  r=requests.get(u,timeout=20);r.raise_for_status();s=bs4.BeautifulSoup(r.content,'html.parser');d=s.select_one('td.eText');im=next(i for i in d.find_all('img') if '/infa/kvest/zagad_zombatid/' in i.get('src','') and '/icon/' not in i.get('src',''));img=urljoin(u,im['src']);r=requests.get(img,timeout=20);r.raise_for_status();b=r.content;assert b.startswith(b'\x89PNG\r\n\x1a\n');return item,img,b,im.get('alt','')
 except Exception as e:return item,'',b'',str(e)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:out=list(ex.map(get,items))
count=0
for (name,u,slug),url,b,alt in out:
 if not b:print('failed',name,alt);continue
 h=hashlib.sha256(b).hexdigest();f=known.get(h)
 if f is None:
  f=P/'img/quests'/('zf3dn-'+slug+'-'+h[:12]+'.png');f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b);known[h]=f
 x=by[slug];note='Скриншот из статьи ZF.3dn; данные могут относиться к исторической версии, их необходимо сверять с другими версиями. На изображении присутствует водяной знак zombi-ferma.ru; независимость сайтов не подтверждена.'
 if name=='ВЗАИМОПОМОЩЬ':note+=' В alt изображения источник ошибочно указал «Задачи экспедиции»; на скриншоте прочитан заголовок «Взаимопомощь».'
 if name=='СТИХИ':note+=' Заголовок каталога «Стихи», подпись изображения и заголовок на скриншоте — «Стихии».'
 if name=='ЗАДАЧА ЭКСПЕДИЦИИ':note+=' В базе название во множественном числе; сопоставление предварительное.'
 image={'path':str(f.relative_to(P)),'retrieved_from':url,'attribution':url,'source_page':u,'note':note};g={'name':'Скриншот задания с ZF.3dn','url':u,'image':image}
 x.setdefault('gallery',[]);x['gallery']=[v for v in x['gallery'] if v.get('url')!=u]+[g]
 if not any(z['url']==u for z in x['sources']):x['sources'].append({'url':u,'label':'ZF.3dn: скриншот задания «Загадка Зомбатиды»'})
 rid='zf3dn-screen-'+slug;rec={'original_id':rid,'original_category':'Квесты','version':'историческая браузерная версия, площадка не уточнена','date':'дата страницы — 2014; дата редакции неизвестна','fields':{'Скриншот':'В разделе дополнительных изображений приведён оригинальный файл источника, включая текст целей и наград; нажмите для полного размера.'},'confidence':note};x.setdefault('prior_records',[]);x['prior_records']=[v for v in x['prior_records'] if v.get('original_id')!=rid]+[rec];count+=1
p.write_text(json.dumps(a,ensure_ascii=False,indent=2));print('added',count,'of 14')

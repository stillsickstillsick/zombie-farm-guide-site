#!/usr/bin/env python3
from pathlib import Path
import json,hashlib,requests,concurrent.futures
P=Path(__file__).resolve().parents[1];p=P/'data/locations.json';a=json.loads(p.read_text());by={x['slug']:x for x in a}
rows=[('zombicity-island-4638', '/blog/sentjabr/2016-12-23-4638', '/_ph/9/578558869.jpg', '23.12.2016', 'С Августа через пристань, квест «Не подарок»; Буй на Домашний. Пристань на Октябрь, уход с острова необратим. Строительство: 33 проволоки, 40 гвоздей, 39 досок; затем 39 бруса секвойи, 28 скотча, 32 каната. Проезд: по 3 зимних яблока, льда, снежка.', 'Фото подписано Сентябрь, но в закомментированном фрагменте; сопоставление предварительное.'), ('zombicity-island-4639', '/blog/oktjabr/2016-12-23-4639', '/_ph/9/758780030.jpg', '23.12.2016', 'С Сентября через пристань, квест «Воришка»; Буй на Домашний. Пристань на Ноябрь, уход с острова необратим. Строительство: 34 проволоки, 41 гвоздь, 38 досок; затем 40 бруса секвойи, 29 скотча, 33 каната. Проезд: по 3 зимней вишни, льда, снежка.', 'Фото подписано Октябрь, но в закомментированном фрагменте; сопоставление предварительное.'), ('zombicity-island-4640', '/blog/nojabr/2016-12-23-4640', '/_bl/46/68008453.jpg', '23.12.2016', 'С Октября через пристань, квест «Блюдо»; Буй на Домашний. Пристань на Декабрь, уход с острова необратим. Строительство: 35 проволоки, 42 гвоздя, 39 досок; затем 41 бруса секвойи, 30 скотча, 34 каната. Проезд: по 3 зимних мандарина, льда, снежка.', 'В статье подписано как фото острова Ноябрь.'), ('zombicity-island-4641', '/blog/dekabr/2016-12-23-4641', '/_bl/46/60201740.jpg', '23.12.2016', 'С Ноября через пристань, квест «Кролик»; выход на Домашний через пристань, уход необратим. Строительство: 36 проволоки, 43 гвоздя, 40 досок; затем 42 бруса секвойи, 31 скотча, 35 канатов. Проезд: по 3 зимних яблока, льда, снежка.', 'В статье подписано как фото острова Декабрь.')]
def download(row):
 try:
  r=requests.get('https://zombie-island.moy.su'+row[2],timeout=(6,20));r.raise_for_status();data=r.content
  ext='.png' if data.startswith(b'\x89PNG\r\n\x1a\n') else '.jpg' if data.startswith(b'\xff\xd8\xff') else None
  if not ext:raise ValueError('не изображение')
  return data,ext,None
 except Exception as e:return None,None,str(e)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(download,rows))
hashes={hashlib.sha256(f.read_bytes()).hexdigest():f for f in (P/'img').rglob('*') if f.is_file()}
for (slug,page,path,date,route,note),(data,ext,error) in zip(rows,results):
 x=by[slug];source='https://zombie-island.moy.su'+page;url='https://zombie-island.moy.su'+path
 if data:
  h=hashlib.sha256(data).hexdigest();dest=hashes.get(h,P/'img/locations'/('moy-photo-'+slug+'-'+h[:12]+ext));dest.parent.mkdir(parents=True,exist_ok=True)
  if h not in hashes:dest.write_bytes(data);hashes[h]=dest
  old=x.get('image');x.setdefault('gallery',[])
  if old and old['path']!=str(dest.relative_to(P)) and not any(g.get('image',{}).get('path')==old['path'] for g in x['gallery']):x['gallery'].append({'name':'Иллюстрация каталога','url':old.get('source_page',source),'image':old})
  x['image']={'path':str(dest.relative_to(P)),'retrieved_from':url,'attribution':'http://zombicity.info'+path,'source_page':source,'note':note+' Копия с moy.su по пути файла zombicity.info; побайтовое совпадение между хостами не проверено.'}
 else:print('image failed',slug,error)
 if not any(s['url']==source for s in x['sources']):x['sources'].append({'url':source,'label':'Zombie-island: отдельная историческая статья о локации'})
 rec={'original_id':'moy-island-detail-'+slug,'original_category':'Острова','version':'историческая браузерная «Зомби Ферма» / «Зомби Мания»','date':date+' — дата в URL; дата редакции неизвестна','fields':{'Маршруты и содержание':route},'confidence':'Фанатская страница, правила исторические, возможны отличия по платформе и версии; общность с ЗомбиСити не позволяет считать источники независимыми.'};x.setdefault('prior_records',[]);x['prior_records']=[r for r in x['prior_records'] if r.get('original_id')!=rec['original_id']]+[rec]
p.write_text(json.dumps(a,ensure_ascii=False,indent=2));print('updated',len(rows),'images fetched',sum(bool(t[0]) for t in results))

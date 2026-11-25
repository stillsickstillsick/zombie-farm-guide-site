#!/usr/bin/env python3
from pathlib import Path
import json,hashlib,requests,concurrent.futures
P=Path(__file__).resolve().parents[1];p=P/'data/locations.json';a=json.loads(p.read_text());by={x['slug']:x for x in a}
rows=[('zombicity-island-4633', '/blog/aprel/2016-12-23-4633', '/_bl/46/23268369.png', '23.12.2016', 'Март → Апрель через пристань, квест «Трое»; Буй на Домашний. С Апреля пристань на Май, уход через неё необратим. Постройка: 18 проволоки, 22 гвоздя, 23 доски; затем 28 бруса секвойи, 12 скотча, 17 канатов. Проезд: по 3 зимней вишни, льда и снежка.', 'Фото подписано Апрель, но находится в закомментированном фрагменте страницы; сопоставление предварительное.'), ('zombicity-island-4634', '/blog/maj/2016-12-23-4634', '/_bl/46/04713728.png', '23.12.2016', 'Апрель → Май через пристань, квест «Ответственность»; Буй на Домашний. Далее пристань на Июнь, уход через неё необратим. Постройка: 20 проволоки, 25 гвоздей, 24 доски; затем 30 бруса секвойи, 15 скотча, 19 канатов. Проезд: по 3 зимних мандарина, льда и снежка.', 'Фото подписано Май, но находится в закомментированном фрагменте страницы; сопоставление предварительное.'), ('zombicity-island-4635', '/blog/ijun/2016-12-23-4635', '/_bl/46/74730074.png', '23.12.2016', 'Май → Июнь через пристань, квест «Аппетит»; Буй на Домашний. Далее пристань на Июль, уход через неё необратим. Постройка: 22 проволоки, 28 гвоздей, 26 досок; затем 33 бруса секвойи, 18 скотча, 22 каната. Проезд: по 3 зимних яблока, льда и снежка.', 'Фото подписано Июнь, но находится в закомментированном фрагменте страницы; сопоставление предварительное.'), ('zombicity-island-4636', '/blog/ijul/2016-12-23-4636', '/_ph/9/616180325.jpg', '23.12.2016', 'Июнь → Июль через пристань, квест «Ёлка»; Буй на Домашний. Далее пристань на Август, уход через неё необратим. Постройка: 30 проволоки, 36 гвоздей, 34 доски; затем 35 бруса секвойи, 25 скотча, 28 канатов. Проезд: по 3 зимней вишни, льда и снежка.', 'Фото подписано Июль, но находится в закомментированном фрагменте страницы; сопоставление предварительное.'), ('zombicity-island-4637', '/blog/avgust/2016-12-23-4637', '/_ph/9/829725341.jpg', '23.12.2016', 'Июль → Август через пристань, квест «Лето»; Буй на Домашний. Далее пристань на Сентябрь, уход через неё необратим. Постройка: 32 проволоки, 39 гвоздей, 36 досок; затем 38 бруса секвойи, 27 скотча, 31 канат. Проезд: по 3 зимних мандарина, льда и снежка.', 'Фото подписано Август, но находится в закомментированном фрагменте страницы; сопоставление предварительное.')]
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

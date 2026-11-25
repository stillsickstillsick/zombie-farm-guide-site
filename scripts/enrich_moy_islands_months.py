#!/usr/bin/env python3
from pathlib import Path
import json,hashlib,requests,concurrent.futures
P=Path(__file__).resolve().parents[1];p=P/'data/locations.json';a=json.loads(p.read_text());by={x['slug']:x for x in a}
rows=[('zombicity-island-4630','/blog/janvar/2016-12-23-4630','/_bl/46/69214350.png','23.12.2016','Домашний → Новогодний камин → Январь (квест «Снеговик»); Буй на Домашний. Переход на Февраль через пристань, после него остров покидают навсегда. Постройка: 10 проволоки, 10 гвоздей, 15 досок; затем 20 бруса секвойи, 5 скотча, 10 канатов. Переезд: по 3 зимней вишни, льда и снежка.','Подпись статьи: фото острова Январь.'),('zombicity-island-4632','/blog/mart/2016-12-23-4632','/_bl/46/82282043.png','23.12.2016','С Февраля через пристань по квесту «Напиток»; Буй на Домашний. С Марта пристань ведёт на Апрель; источник предупреждает, что после перехода на Апрель вернуться на Март нельзя. Строительство: 15 проволоки, 20 гвоздей, 20 досок; затем 25 бруса секвойи, 10 скотча, 15 канатов. Переезд: по 3 зимних яблока, льда и снежка.','Источник подписывает изображение как фото Марта, но оно находится в закомментированном фрагменте страницы; сопоставление предварительное.'),('zombicity-island-4040','/blog/ostrov_pionerskiy_lager_zombie_farm_mania/2015-12-06-4040','/zombie-farm/2015/25/ostrov-pionerskiy-lager-zombie-farm-mania.png','06.12.2015','Построить Юбилейную яхту на Домашнем острове; источник указывает бесплатный переезд. Остров описан как домашний, появившийся 5 декабря 2015 к пятилетию игры. В статье упомянуты сокровища-кексы, Шапка-невидимка в восточном углу, рулетки и постройки; грядок указано 195.','Подпись статьи: фото острова Пионерский лагерь.')]
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

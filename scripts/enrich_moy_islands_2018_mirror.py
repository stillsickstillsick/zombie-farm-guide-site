#!/usr/bin/env python3
from pathlib import Path
import json,hashlib,requests,concurrent.futures
P=Path(__file__).resolve().parents[1];p=P/'data/locations.json';a=json.loads(p.read_text());by={x['slug']:x for x in a}
rows=[('zombicity-island-5685', '/blog/zazerkale/2018-07-06-5685', '/_ph/9/816615500.jpg', '06.07.2018', 'Вход из Приюта Призрака через Магическое зеркало: 3 Времени, 3 книги, 30 000 монет. Источник предупреждает: после возврата в Приют конкретное Зазеркалье исчезает, но в него можно снова войти через зеркало, пока не найден сундук с Мантией. Для расчистки — скипетр.', 'Первое из двух фото Зазеркалья, подписанных в статье.'), ('zombicity-island-5686', '/blog/peshhera_kapitana/2018-07-06-5686', '/_ph/9/936819209.jpg', '06.07.2018', 'Вход через Пещеру Капитана: 50 000 монет, 5 подземных фонарей, 5 скакалок. Местонахождение входа в этой статье отдельно не уточнено.', 'Подписанное фото Пещеры Капитана.'), ('zombicity-island-5599', '/blog/ostrova_voskhodjashhego_solnca/2018-06-01-5599', '/_ph/9/134774029.jpg', '01.06.2018', 'На Джонке за 1 Солнце (элемент Японской коллекции), 3 воды и 50 000 монет. Четыре части: Чайный остров, Сад камней, Долина Храмов (Вершина горы), Бамбуковый лес. Для очистки указан посох.', 'Подписанное фото Островов Восходящего Солнца.'), ('zombicity-island-5600', '/blog/serdce_gory/2018-06-01-5600', '/_ph/9/668459111.jpg', '01.06.2018', 'Горный проход с Островов Восходящего Солнца ведёт в Сердце Горы. Для очистки указан посох. Стоимость проезда в статье не указана.', 'Подписанное фото Сердца Горы.')]
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

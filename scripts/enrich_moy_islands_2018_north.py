#!/usr/bin/env python3
from pathlib import Path
import json,hashlib,requests,concurrent.futures
P=Path(__file__).resolve().parents[1];p=P/'data/locations.json';a=json.loads(p.read_text());by={x['slug']:x for x in a}
rows=[('zombicity-island-5954', '/blog/severnye_zemli/2018-10-09-5954', '/_ph/9/350859811.jpg', '09.10.2018', 'С Острова Изобретателей на Бочке Мастера за 5 досок, 3 слезы зомби и 30 000 монет. Радужный мост ведёт в подземелья Нифльхейм; для очистки указан скипетр.', 'Подписанное фото Северных Земель.'), ('zombicity-island-5955', '/blog/podzemelja_niflkhejm/2018-10-09-5955', '/_ph/9/449578449.jpg', '09.10.2018', 'С Северных Земель через Радужный мост за 5 синих сердец, 50 000 монет и 3 баклажадины. Статья называет скипетр средством очистки и перечисляет Валькирию и три цветные двери.', 'Подписанное фото Подземелий Нифльхейм.'), ('zombicity-island-5900', '/blog/ostrov_izobretatelej/2018-09-19-5900', '/_ph/9/82884810.jpg', '19.09.2018', 'На модернизированном Воздушном шаре, проезд бесплатный. Указаны кузница Мастера, Дельтакрыл, лаборатория, обсерватория и Махолёт; некоторые перечисленные объекты связаны с обновлениями 2019 года, то есть страница дополнялась.', 'Подписанное фото Острова Изобретателей.'), ('zombicity-island-5719', '/blog/zombinapur/2018-07-27-5719', '/_ph/9/60445193.jpg', '27.07.2018', 'Из Джунглей на Лодочке за 3 простыни, 3 компаса и 10 000 монет. Для очистки указан посох. Источник датирует появление острова 27 июля 2018.', 'Подписанное фото Зомбинапура.'), ('zombicity-island-5683', '/blog/prijut_prizraka/2018-07-06-5683', '/_ph/9/535707713.jpg', '06.07.2018', 'На Альбатросе за 3 компаса, 1 карту сокровищ (показан элемент Пиратской коллекции) и 50 000 монет. Указаны нож и супер-нож для очистки.', 'Подписанное фото Приюта Призрака.')]
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

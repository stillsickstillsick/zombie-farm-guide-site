#!/usr/bin/env python3
from pathlib import Path
import json,hashlib,requests,concurrent.futures
P=Path(__file__).resolve().parents[1];p=P/'data/locations.json';a=json.loads(p.read_text());by={x['slug']:x for x in a}
rows=[('zombicity-island-6045', '/blog/korallovyj_rif/2018-11-26-6045', '/_ph/9/164784573.jpg', '26.11.2018', 'Усовершенствованная Бочка Мастера ведёт на Коралловый риф; стоимость 5 компасов, 3 фонарика (пиктограмма из Японской коллекции), 30 000 монет. На рифе три спуска: к Багровым теням, Изумрудному дну и Лиловой бездне. Статья называет трезубец инструментом очистки; по её описанию, каждый якорь охраняет спрут, которого надо накормить.', 'Подписанное фото Кораллового рифа.'), ('zombicity-island-6046', '/blog/bagrovye_teni/2018-11-27-6046', '/_ph/8/782200712.jpg', '27.11.2018', 'Вход через Спуск к Багровым теням; проезд 5 стали, 5 красного пластилина, 30 000 монет; очистка трезубцем. Источник связывает локацию с обновлением «Художник» 2018 года.', 'Подписанное фото Багровых теней.'), ('zombicity-island-6047', '/blog/izumrudnoe_dno/2018-11-27-6047', '/_ph/8/204933445.jpg', '27.11.2018', 'Вход через Спуск на Изумрудное дно; проезд 5 стали, 5 зелёного пластилина, 30 000 монет; очистка трезубцем. Источник связывает локацию с обновлением «Художник» 2018 года.', 'Подписанное фото Изумрудного дна.'), ('zombicity-island-5997', '/blog/strana_mertvykh/2018-10-24-5997', '/_ph/9/987316709.jpg', '24.10.2018', 'Вход через Крипталифт за 5 Клеверхелл, 3 каната и 35 000 монет; Крипталифт Два ведёт в Лабиринты Памяти. Для очистки указан посох.', 'Подписанное фото Страны Мёртвых.'), ('zombicity-island-5998', '/blog/labirinty_pamjati/2018-10-24-5998', '/_ph/9/908130442.jpg', '24.10.2018', 'Из Страны Мёртвых через Крипталифт Два: 5 овощных бочек, 3 подземных фонаря и 35 000 монет. Для очистки указан посох; перечислены Ворота Памяти 1 и 2.', 'Подписанное фото Лабиринтов Памяти.')]
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

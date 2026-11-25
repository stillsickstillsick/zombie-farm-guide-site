#!/usr/bin/env python3
from pathlib import Path
import json,hashlib,requests,concurrent.futures
P=Path(__file__).resolve().parents[1];p=P/'data/locations.json';a=json.loads(p.read_text());by={x['slug']:x for x in a}
rows=[('zombicity-island-6188', '/blog/parjashhie_ostrova/2019-02-08-6188', '/_ph/9/733092320.jpg', '08.02.2019', 'С Острова Изобретателей на Махолёте; проезд 50 000 монет, 5 ваты и 5 подушек. Далее на Город Людей через Махолёт. Упомянуты Облачный улей, Большая скала, вертолёт Энни и скипетр для очистки.', 'Фото подписано Парящие острова.'), ('zombicity-island-6189', '/blog/gorod_ljudej/2019-02-08-6189', '/_ph/9/882362194.jpg', '08.02.2019', 'С Парящих островов на модернизированном Махолёте: 50 000 монет, 5 синих сердец, 3 баклажадины. Источник называет остров постоянным; перечисляет мэрию, полицейский участок, кафе, заправку и Атомиум.', 'Фото подписано Город Людей.'), ('zombicity-island-6078', '/blog/oranzhereja/2018-12-15-6078', '/_ph/9/112948495.jpg', '15.12.2018', 'С Острова Изобретателей на Дельтакрыле за 3 флюгера, 3 подушки и 30 000 монет. С Оранжереи пристань ведёт на Остров Засухи. Для очистки указан посох.', 'Фото подписано Оранжерея.'), ('zombicity-island-6079', '/blog/ostrov_zasukhi/2018-12-15-6079', '/_ph/9/983082742.jpg', '15.12.2018', 'С Оранжереи через пристань за 5 рогаток, 3 язя и 55 000 монет. Разрушенный механизм ведёт на Насосную станцию. Для очистки указан посох. Это отдельная локация обновления «Друиды», не автоматически тождественная Солнечному острову события засухи 2014 года.', 'Фото подписано Остров Засухи.'), ('zombicity-island-6080', '/blog/nasosnaja_stancija/2018-12-15-6080', '/_ph/9/861887438.jpg', '15.12.2018', 'С Острова Засухи через Разрушенный механизм за 3 угля, 5 огня и 35 000 монет. Для расчистки перечислены дровосеки и камнетёсы, включая варианты парами и с мозгами.', 'Фото подписано Насосная Станция.')]
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

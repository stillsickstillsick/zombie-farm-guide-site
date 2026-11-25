#!/usr/bin/env python3
from pathlib import Path
import json,hashlib,requests
P=Path(__file__).resolve().parents[1];p=P/'data/locations.json';a=json.loads(p.read_text());by={x['slug']:x for x in a}
rows=[('zombicity-island-3479','/home/user/grot.jpg','/zombie-farm/2015/8/svetlui-grot-zombie-mania.jpg','/blog/ostrov_svetlyj_grot_zombie_farm_mania/2015-03-25-3479','В источнике подписан как немного расчищенный Светлый грот. Скачана копия с moy.su по пути оригинального файла zombicity.info; побайтовое совпадение между хостами не проверено.','25.03.2015','Вход с Загадочного острова через Пасть, в ходе линейки об Упс, квест «В поисках». Обратный переход на Загадочный — через Летающую тарелку в гроте.'),('zombicity-island-4631','/home/user/fevral.png','/_bl/46/82927061.png','/blog/fevral/2016-12-23-4631','В исходном извлечённом тексте расположен после заголовка «Фото острова Февраль», но изображение было в закомментированном фрагменте страницы; сопоставление предварительное. Скачана копия с moy.su по пути zombicity.info; идентичность файлов разных хостов не проверена.','23.12.2016','Из Января через пристань по квесту «Февраль»; Буй возвращает на Домашний; пристань ведёт на Март. Источник предупреждает, что уход через пристань закрывает возврат на Февраль. Пристань на Март: 12 проволоки, 15 гвоздей, 18 досок; затем 22 бруса секвойи, 8 скотча, 12 канатов. Переезд: по 3 зимних мандарина, льда и снежка.')]
hashes={hashlib.sha256(f.read_bytes()).hexdigest():f for f in (P/'img').rglob('*') if f.is_file()}
for slug,local,path,page,note,date,route in rows:
 x=by[slug]; tmp=Path(local);
 if tmp.exists(): data=tmp.read_bytes()
 else:
  res=requests.get('https://zombie-island.moy.su'+path,timeout=(8,30));res.raise_for_status();data=res.content
 assert data.startswith(b'\x89PNG\r\n\x1a\n') or data.startswith(b'\xff\xd8\xff')
 h=hashlib.sha256(data).hexdigest();ext=Path(local).suffix;dest=hashes.get(h,P/'img/locations'/('moy-photo-'+slug+'-'+h[:12]+ext));dest.parent.mkdir(parents=True,exist_ok=True)
 if h not in hashes:dest.write_bytes(data);hashes[h]=dest
 source='https://zombie-island.moy.su'+page; original='http://zombicity.info'+path;url='https://zombie-island.moy.su'+path
 old=x.get('image');x.setdefault('gallery',[])
 if old and old['path']!=str(dest.relative_to(P)) and not any(g.get('image',{}).get('path')==old['path'] for g in x['gallery']):x['gallery'].append({'name':'Иллюстрация каталога','url':old.get('source_page',source),'image':old})
 x['image']={'path':str(dest.relative_to(P)),'retrieved_from':url,'attribution':original,'source_page':source,'note':note}
 if not any(s['url']==source for s in x['sources']):x['sources'].append({'url':source,'label':'Zombie-island: отдельная историческая статья о локации'})
 r={'original_id':'moy-island-detail-'+slug,'original_category':'Острова','version':'браузерная «Зомби Ферма» / «Зомби Мания», платформа не уточнена','date':date+' — дата в URL, дата последней редакции неизвестна','fields':{'Маршрут и условия':route},'confidence':'Один фанатский источник; сайт и ЗомбиСити могут быть связаны, независимым подтверждением не считаются. Условия исторические.'};x.setdefault('prior_records',[]);x['prior_records']=[z for z in x['prior_records'] if z.get('original_id')!=r['original_id']]+[r]
p.write_text(json.dumps(a,ensure_ascii=False,indent=2));print('updated islands',len(rows))

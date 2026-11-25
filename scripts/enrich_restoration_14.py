from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parents[1];p=P/'data/locations.json';a=json.loads(p.read_text());by={x['slug']:x for x in a}
rows=[('zombicity-island-4335','img/locations/map-reference-pogreb-c75d10f899f7.jpg','https://zombie-island.moy.su/blog/pogreb_prishelcev/2016-04-17-4335','/_ph/9/868035104.jpg','Фото Погреба пришельцев по подписи статьи; стадия расчистки и соответствие изначальной расстановке точно не установлены.'),('zombicity-island-4336','img/locations/map-reference-shakhta-f8e409fce5e0.jpg','https://zombie-island.moy.su/blog/serebrjanaja_shakhta/2016-04-17-4336','/_ph/9/632748096.jpg','Фото Серебряной шахты по подписи статьи; стадия расчистки и соответствие изначальной расстановке точно не установлены.'),('zombicity-island-3405','img/locations/map-reference-skazochny-de434596177b.jpg','https://zombie-island.moy.su/blog/skazochnyj_les_zombie_farm_ostrov_mania/2014-12-20-3405','/zombie-farm/2014/1/skazochnyi-ostrov-zombie-farm-mania.jpg','По подписи источника — Сказочный лес после превращения. Нельзя считать начальной расстановкой; часть объектов могла быть размещена игроком.')]
for slug,path,page,remote,note in rows:
 x=by[slug];x.setdefault('gallery',[]);old=x.get('image');im={'path':path,'retrieved_from':'https://zombie-island.moy.su'+remote,'attribution':'http://zombicity.info'+remote,'source_page':page,'note':note+' Файл получен с moy.su по пути zombicity.info, побайтовая идентичность с другим хостом не проверена; без перекодирования.'}
 if old and old['path']!=path and not any(z.get('image',{}).get('path')==old['path'] for z in x['gallery']):x['gallery'].append({'name':'Иллюстрация каталога','url':old.get('source_page',page),'image':old})
 x['image']=im;x.setdefault('sources',[])
 if not any(z.get('url')==page for z in x['sources']):x['sources'].append({'url':page,'label':'Zombie-island: статья и подписанная фотография'})
p.write_text(json.dumps(a,ensure_ascii=False,indent=2));print('updated',len(rows))

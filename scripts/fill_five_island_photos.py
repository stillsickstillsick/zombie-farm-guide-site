"""Curated screenshots on individually read island pages, saved byte-for-byte."""
import requests,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1];f=P/'data/locations.json';records=json.loads(f.read_text());base='https://zombie-island.moy.su';rows=[
('opushka-vremya-chudes-2015','/blog/opushka/2015-12-23-4114','/zombie-farm/2015/27/ostrov-opuska-zombie-farm-mania.png','Дата 23.12.2015 и новогоднее событие совпадают; автор и дата создания снимка неизвестны.'),
('solnechnyy-ostrov-zasukha','/blog/solnechnyj_ostrov_igry_zombie_farm_mania_kak_popast_na_ostrov/2014-08-02-3095','/zombie-farm/ZombiFermaMania/Ostrova-foto/ostrov_solnechnyj_zombi_ferma.jpg','Сопоставление предварительное: в обеих публикациях остров Солнечный и Терем при засухе, но условия срока доступа различаются; версия или редакция могут отличаться.'),
('lysaya-gora-2013','/blog/lysaja_gora_ostrov_island_zombie_farm/2013-11-01-2387','/zombie-farm/ZombiFermaMania/Ostrova-foto/ostrov-lysaya-gora-igry-zombi-ferma.jpg','Дата Хэллоуина 2013 и Чертовы ворота совпадают; автор снимка неизвестен.'),
('tumanny-asteroid','/blog/tumannyj_ostrov_zombie/2015-09-02-3837','/zombie-farm/2015/18/tumannuy-ostrov-asteroid-zombie-mania.jpg','Сопоставление: Туманный астероид, квест Усилитель и Жёлтая будка; возможны различия редакций.'),
('odinokiy-asteroid','/blog/odinokij_ostrov/2015-09-02-3841','/zombie-farm/2015/18/odinokiy-asteroid-zombie-mania-farm.png','Сопоставление: Одинокий астероид, квест К цели и пристань с Зомбикрона; возможны различия редакций.')]
hashes={hashlib.sha256(x.read_bytes()).hexdigest():x for x in (P/'img').rglob('*') if x.is_file()};added=[]
for slug,page,path,note in rows:
 e=next(x for x in records if x['slug']==slug)
 if e.get('image'):continue
 try:
  r=requests.get(base+path,timeout=30);r.raise_for_status();b=r.content;ext='png' if b.startswith(b'\x89PNG\r\n\x1a\n') else 'jpg' if b.startswith(b'\xff\xd8\xff') else None
  if not ext:raise ValueError('not an image')
  h=hashlib.sha256(b).hexdigest()
  if h not in hashes:
   out=P/'img'/'locations'/f'moy-photo-{slug}-{h[:12]}.{ext}';out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(b);hashes[h]=out
  e['image']={'path':str(hashes[h].relative_to(P)),'retrieved_from':r.url,'attribution':r.url,'source_page':base+page,'note':note+' Страница ссылается на файл zombicity.info по тому же пути; скачана копия moy.su, побайтовая идентичность не проверена.'}
  e['sources'].append({'url':base+page,'label':'Zombie-island.moy.su — историческая статья и снимок острова'});added.append(slug)
 except Exception as ex:print('error',slug,ex)
f.write_text(json.dumps(records,ensure_ascii=False,indent=2));print('added',added)

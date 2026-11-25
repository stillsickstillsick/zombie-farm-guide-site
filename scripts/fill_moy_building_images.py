"""Curated links on individually checked browser-game source pages."""
import json,requests,hashlib
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin,urlparse
P=Path(__file__).resolve().parents[1];f=P/'data/buildings.json';items=json.loads(f.read_text());base='https://zombie-island.moy.su';news=base+'/news/10_oktjabrja_bla_bla/2015-10-10-213';star=base+'/blog/zvezdnyj_pereval_zombie_farm_mania/2015-06-26-3739';alone=base+'/blog/odinokij_ostrov/2015-09-02-3841';hut=base+'/blog/kosmicheskaja_khizhina_na_raduzhnom/2015-07-02-3773';rows=[
('ekspeditor-2',base+'/blog/ehkspeditor_2_postrojka_zombie_farm_mania/2014-09-27-3201','/zombie-farm/ZombiFermaMania/Postroyka_1/ehkspeditor_2_postrojka_zombie_farm_mania.png'),
('batuty',base+'/blog/zombie_farm_nazad_v_nizhnee_dnishhe/2012-07-18-213','/zombie-farm/ZombiFermaMania/Postroyka/batut-postroyka-games-igra-zombie-farm-mania.png'),
('kosmicheskaya-pristan-kometa',base+'/blog/ostrov_kometa/2015-09-02-3839','/zombie-farm/2015/18/m_space_pier.png'),
('pristan-na-ostrov-lyubvi','https://officialgroupzf.ucoz.ru/publ/ostrov_ljubvi/1-1-0-25','/zombie-farm/igra-Ostrova/pristan-zombie-farm-mania-island.png'),
('nemosfera',base+'/blog/nemosfera_postrojka_zombie_farm_mania/2014-11-12-3281','/zombie-farm/ZombiFermaMania/Postroyka_1/nemosfera_postrojka_zombie_farm_mania.png'),
('rasshchelina-peshchera-istiny',base+'/blog/skalistyj_rif_igry_zombie_farm_mania_kak_popast_na_ostrov/2014-11-12-3289','/zombie-farm/ZombiFermaMania/Postroyka_1/rasshhelina_postrojka_zombie_farm_mania.png'),
('vrata-zombatidy',base+'/blog/skalistyj_rif_igry_zombie_farm_mania_kak_popast_na_ostrov/2014-11-12-3289','/zombie-farm/ZombiFermaMania/Postroyka_1/vrata_zombatidy_postrojka_zombie_farm_mania.png'),
('kolesnitsa-temnye-vody',base+'/blog/kolesnica_postrojka_zombie_farm_mania/2014-09-27-3210','/zombie-farm/ZombiFermaMania/Postroyka_1/kolesnica_postrojka_zombie_farm_mania.png'),
('telefonnaya-budka-raduzhnyy',base+'/blog/telefonnaja_budka_2_zombie_mania_farm/2015-06-25-3732','/zombie-farm/2015/12/telefonnaya-budka.png'),
('telefonnaya-budka-zvezdnyy-pereval',base+'/blog/telefonnaja_budka_2_zombie_mania_farm/2015-06-25-3732','/zombie-farm/2015/12/telefonnaya-budka.png'),
('zheltaya-budka',base+'/blog/tumannyj_ostrov_zombie/2015-09-02-3837','/zombie-farm/2015/18/zheltaya-budka-zombie.png'),
('mashina-vremeni-zvezdnyy-pereval',base+'/blog/mashina_vremeni/2015-09-03-3871','/zombie-farm/2015/18/mashina-vremeni.png'),
('kosmicheskaya-khizhina',hut,'/zombie-farm/2015/14/kosmicheskaya-hizhina-zombie.png'),
('lunokhod',star,'/zombie-farm/2015/14/lunohod-na-zvezdnom-perevale.png'),
('otrazhatel',news,'/zombie-farm/2015/21/reflector-otrazhatel-zombie-farm.png'),
('grob-na-kolesikah-zvezdnyy',star,'/zombie-farm/2015/21/grob-na-kolesikah.png'),
('kapsula-starzi-zvezdnyy',star,'/zombie-farm/2015/18/creocapsule-karsula.png'),
('kosmoport-zvezdnyy-pereval',star,'/zombie-farm/2015/18/spaceport.png'),
('kosmicheskaya-pristan-zombikron',alone,'/zombie-farm/2015/18/m_space_pier.png'),
('kosmicheskaya-pristan-odinokiy',alone,'/zombie-farm/2015/18/m_space_pier.png'),
('kosmicheskaya-pristan-kulichki',news,'/zombie-farm/2015/18/m_space_pier.png'),
('kosmicheskaya-pristan-lovushka',news,'/zombie-farm/2015/18/m_space_pier.png'),
('kosmicheskaya-pristan-planeta-zloki',news,'/zombie-farm/2015/18/m_space_pier.png')]
hashes={hashlib.sha256(p.read_bytes()).hexdigest():p for p in (P/'img').rglob('*') if p.is_file()};cache={};added=[];fail=[]
for slug,page,path in rows:
 e=next(v for v in items if v['slug']==slug)
 if e.get('image'):continue
 try:
  if page not in cache:
   r=requests.get(page,timeout=20);r.raise_for_status();cache[page]=BeautifulSoup(r.content,'html.parser')
  m=[i for i in cache[page].find_all('img',src=True) if urlparse(urljoin(page,i['src'])).path==path]
  if not m:raise ValueError('image not in source')
  url=base+path;r=requests.get(url,timeout=20);r.raise_for_status();b=r.content;ext='png' if b.startswith(b'\x89PNG\r\n\x1a\n') else 'jpg' if b.startswith(b'\xff\xd8\xff') else None
  if not ext:raise ValueError('not PNG or JPEG')
  h=hashlib.sha256(b).hexdigest()
  if h not in hashes:
   out=P/'img'/'buildings'/f'moy-{slug}-{h[:12]}.{ext}';out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(b);hashes[h]=out
  e['image']={'path':str(hashes[h].relative_to(P)),'retrieved_from':r.url,'attribution':url,'source_page':page,'note':'Иллюстрация объекта в исторической браузерной версии; исходная страница ссылается на zombicity.info, скачан файл по тому же пути на moy.su — побайтовое совпадение не проверено. Некоторые варианты пристаней, батутов и телефонных будок имеют общие иллюстрации в источнике; совпадение изображения не подтверждает тождественность объектов.'}
  if not any(x['url']==page for x in e['sources']):e['sources'].append({'url':page,'label':'Zombie-island.moy.su: иллюстрация постройки'})
  added.append(slug)
 except Exception as ex:fail.append((slug,str(ex)[:120]))
f.write_text(json.dumps(items,ensure_ascii=False,indent=2));print('added',len(added),added,'failed',fail)

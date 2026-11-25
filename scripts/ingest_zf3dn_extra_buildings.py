#!/usr/bin/env python3
import requests,bs4,json,re,hashlib
from pathlib import Path
from urllib.parse import urlparse,unquote
P=Path(__file__).resolve().parents[1];f=P/'data/buildings.json';a=json.loads(f.read_text());by={x['slug']:x for x in a}
rows=[('vesenniy-fontan','Весенний фонтан','https://zf.3dn.ru/publ/postrojki/vesennij_fontan/1-1-0-404'),('suvenirnaya-lavka','Сувенирная лавка','https://zf.3dn.ru/publ/postrojki/suvenirnaja_lavka/1-1-0-221'),('kitayskaya-stena-1','Китайская стена, №1','https://zf.3dn.ru/publ/postrojki/kitajskaja_bashnja_1/1-1-0-32'),('kitayskaya-stena-2','Китайская стена, №2','https://zf.3dn.ru/publ/postrojki/kitajskaja_stena_2/1-1-0-33')]
for slug,name,u in rows:
 r=requests.get(u,timeout=20);r.raise_for_status();s=bs4.BeautifulSoup(r.content,'html.parser');e=s.select_one('td.eText');assert e
 for t in e(['script','style']):t.decompose()
 for im in e.find_all('img'):
  fname=unquote(Path(urlparse(im.get('src','')).path).name);alt=im.get('alt','').strip();im.replace_with('[изображение: '+(alt+'; ' if alt else '')+fname+']')
 txt=e.get_text('\n',strip=True);dt=re.search(r'\(\d{2}\.\d{2}\.\d{4}\)',s.get_text(' ',strip=True));date=dt.group()[1:-1] if dt else 'не найдена'
 x=by.get(slug)
 if not x:
  x={'slug':slug,'name':name,'category':'buildings','type':'Постройка','purchase':'нет данных','sale':'нет данных','obtain':'нет данных','use':'нет данных','features':'нет данных','versions':'историческая браузерная версия; площадка не установлена','sources':[],'image':None,'links':[],'prior_records':[]};a.append(x);by[slug]=x
 if not any(z['url']==u for z in x['sources']):x['sources'].append({'url':u,'label':'ZF.3dn: историческая карточка постройки'})
 rid='zf3dn-building-'+slug;rec={'original_id':rid,'original_category':'Постройки','version':'историческая браузерная игра, площадка не указана','date':date+' — дата публикации; дата редакции неизвестна','fields':{'Текст и пиктограммы источника':txt},'confidence':'Названия файлов и alt сохранены как подписи, не заменяют проверенную расшифровку пиктограмм; дата редакции и независимость сайтов неизвестны. Исторические значения требуют сверки.'};x.setdefault('prior_records',[]);x['prior_records']=[v for v in x['prior_records'] if v.get('original_id')!=rid]+[rec]
x=by['vesenniy-fontan'];u='https://zombie-island.moy.su/blog/vesennij_fontan_prazdnichnaja_postrojka_zombie_farm_mania/2013-03-05-1785';orig='http://zombicity.info/zombie-farm/ZombiFermaMania/Postroyka/vesennij-fontan-postrojka-zombie-farm-mania-island.png';img=orig.replace('http://zombicity.info','https://zombie-island.moy.su');r=requests.get(img,timeout=20);r.raise_for_status();b=r.content;assert b.startswith(b'\x89PNG\r\n\x1a\n');h=hashlib.sha256(b).hexdigest();known={hashlib.sha256(z.read_bytes()).hexdigest():z for z in (P/'img').rglob('*') if z.is_file()};dest=known.get(h,P/'img/buildings'/('vesenniy-fontan-'+h[:12]+'.png'));dest.parent.mkdir(parents=True,exist_ok=True)
if h not in known:dest.write_bytes(b)
x['image']={'path':str(dest.relative_to(P)),'retrieved_from':img,'attribution':orig,'source_page':u,'note':'Пиктограмма подписана в статье; файл скачан с moy.su по тому же пути, на который источник ссылается на zombicity.info. Побайтовая идентичность с исходным хостом не проверена.'}
if not any(z['url']==u for z in x['sources']):x['sources'].append({'url':u,'label':'Zombie-island: Весенний фонтан'})
rid='moy-spring-fountain';record={'original_id':rid,'original_category':'Постройки','version':'историческая браузерная версия Зомби Ферма / Мания','date':'05.03.2013 — дата в адресе; дата редакции неизвестна','fields':{'Покупка и продажа':'По странице: 150 000 монет покупка, 1 500 монет продажа, 500 опыта за покупку.','Стадии':'Свет: 10, 50, 200, 500, 1000; всего 1760.','Взаимодействие':'Источник описывает помощь друзей: один Свет в сутки бесплатно, дополнительные — за зомбаксы; лимит 100 фонтанов друзей в день.','Награды':'Перечислены возможные находки после превращения: коллекции, удобрения, материалы и другие предметы; вероятности не приведены.'},'confidence':'Историческая фанатская статья; данные на разных площадках и в разные периоды могут отличаться. Зависимость от ZF.3dn и ЗомбиСити не установлена.'};x['prior_records']=[r for r in x['prior_records'] if r.get('original_id')!=rid]+[record]
f.write_text(json.dumps(a,ensure_ascii=False,indent=2));print('two cards, two Chinese wall variants and fountain image saved')

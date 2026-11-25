from pathlib import Path
import json,hashlib,requests
P=Path(__file__).resolve().parents[1];p=P/'data/locations.json';a=json.loads(p.read_text());x=next(z for z in a if z['slug']=='zombicity-island-5643');u='https://pp.userapi.com/c824601/v824601563/165dd7/xm4aLlsmH-Y.jpg';page='https://zombie-island.moy.su/blog/ostrov_futbola/2018-06-14-5643';tmp=Path('/home/user/football2018.jpg')
if tmp.exists():b=tmp.read_bytes()
else:
 r=requests.get(u,timeout=(8,30));r.raise_for_status();b=r.content
assert b.startswith(b'\xff\xd8\xff');h=hashlib.sha256(b).hexdigest();known={hashlib.sha256(f.read_bytes()).hexdigest():f for f in (P/'img').rglob('*') if f.is_file()};dest=known.get(h,P/'img/locations'/('football-2018-'+h[:12]+'.jpg'));dest.parent.mkdir(parents=True,exist_ok=True)
if h not in known:dest.write_bytes(b)
old=x.get('image');x.setdefault('gallery',[])
if old and old['path']!=str(dest.relative_to(P)) and not any(g.get('image',{}).get('path')==old['path'] for g in x['gallery']):x['gallery'].append({'name':'Иллюстрация каталога','url':old.get('source_page',page),'image':old})
x['image']={'path':str(dest.relative_to(P)),'retrieved_from':u,'attribution':u,'source_page':page,'note':'Оригинальный файл опубликован на userapi и показан страницей moy.su как фото острова. Это размеченная автором карта; авторство и права не установлены, надписи сохранены без изменений.'}
if not any(s['url']==page for s in x['sources']):x['sources'].append({'url':page,'label':'Zombie-island: Остров Футбола 2018'})
r={'original_id':'moy-island-detail-football-2018','original_category':'Острова','version':'браузерная Зомби Ферма / Зомби Мания','date':'14.06.2018 — дата в URL; дата редакции неизвестна','fields':{'Доступ':'На отремонтированном Вседорожнике: 3 кварца, 3 овощные бочки, 35 000 монет. По источнику посещение возможно 14 дней после первой поездки.','Что на острове':'Кубок мира, тележка с хот-догами, Сувенирная лавка, три ворот и флаги. Для расчистки указан нож.'},'confidence':'Фанатская статья, исторические условия; не отождествлять автоматически с футбольными событиями других лет.'};x.setdefault('prior_records',[]);x['prior_records']=[z for z in x['prior_records'] if z.get('original_id')!=r['original_id']]+[r];p.write_text(json.dumps(a,ensure_ascii=False,indent=2));print('football updated')

import json
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'data/quests.json';a=json.loads(p.read_text())
rows=[('wind',2667,'tolko-nachalo','Только начало','Унесенные ветром','Найти и развести Кострище в Зимнем лесу; согреть там Гнома-шутника.','5 зомбаксов, 15 соли','Зимний лес','Предостережение',''),('wind',2668,'predosterezhenie','Предостережение','Унесенные ветром','Выиграть 5 000 опыта в рулетках; собрать 120 чеснока; приготовить 30 Палочек-выручалочек.','5 Железных сердец, 1 000 опыта, 5 йодированной соли','Только начало','Слухи','Гном говорит, что буря унесла остальных гномов на север.'),('wind',2669,'sluhi','Слухи','Унесенные ветром','Раздобыть 10 компасов; найти 20 любых предметов Ёлочной коллекции (пропуск за 15 зб); сделать 30 Огня.','5 льда, 15 шерсти, 2 000 опыта','Предостережение','Подготовка','История называет опасность Королевства Льда слухом; фактическая механика не подтверждена.'),('wind',2670,'podgotovka','Подготовка','Унесенные ветром','Подготовить 10 Валенков и 30 Глазного супа; найти 15 лунных камней (пропуск за 7 зб).','5 лепестков розы, 15 Изумрудных сердец, 25 Палочек-выручалочек','Слухи','В путь','')]

for group,id,slug,name,line,goals,reward,prev,nxt,note in rows:
 slug=f'{group}-{slug}-{id}';e=next((x for x in a if x['slug']==slug),None)
 if not e:e={'slug':slug,'name':name+' — «'+line+'»','category':'quests','type':'Задание линейки «'+line+'»','purchase':'нет данных','sale':'нет данных','obtain':'нет данных','use':'нет данных','features':'нет данных','versions':'историческая версия ВКонтакте; редакция неизвестна','sources':[],'image':None,'links':[],'event':line,'prior_records':[]};a.append(e)
 path=f'q_5year_{id-2655}' if group=='birthday5' else f'q_wwind_{id-2662}';url=f'https://viver.my1.ru/publ/gamemission/{path}/11-1-0-{id}'
 fields={'Цели':goals,'Награда':reward,'Соседние задания':(f'Предыдущее: «{prev}»; ' if prev else 'Предыдущее на странице не указано; ')+(f'следующее: «{nxt}». ' if nxt else 'следующее на странице не указано. ')+'Порядок по источнику; условия разблокировки не проверены.'}
 if note:fields['Примечание']=note
 r={'original_id':f'viver-quests-{id}','original_category':'Задания','version':'историческая социальная версия VK; дата редакции неизвестна','date':'21.10.2018 — публикация; дата последующей редакции неизвестна','fields':fields,'confidence':'Фанатский справочник; актуальность и независимость не установлены.'};e['prior_records']=[x for x in e['prior_records'] if x.get('original_id')!=r['original_id']]+[r]
 if not any(x['url']==url for x in e['sources']):e['sources'].append({'url':url,'label':'ViveR_9: отдельная статья задания'})
for group,id,slug,name,line,goals,reward,prev,nxt,note in rows:
 by={x['name'].split(' — «')[0]:x for x in a if x['slug'].startswith(group+'-') and x['name'].endswith(' — «'+line+'»')}
 for left,right in [(prev,name),(name,nxt)]:
  if left in by and right in by:
   for start,end,rel in [(left,right,'следующее задание по источнику'),(right,left,'предыдущее задание по источнику')]:
    e,t=by[start],by[end];o={'category':'quests','slug':t['slug'],'name':t['name'],'relation':rel}
    if o not in e['links']:e['links'].append(o)
p.write_text(json.dumps(a,ensure_ascii=False,indent=2));print('6 заданий двух линеек')

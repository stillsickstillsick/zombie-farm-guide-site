import json
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'data/quests.json';a=json.loads(p.read_text())
rows=[
(2689,'podgotovka','Подготовка','Получить в Сфинксе 50 кирпичей; найти Бозон Хиггса (пропуск 15 зб); сделать 100 гвоздей.','1 Бочка повара','Количество Бозонов Хиггса не указано. Отличается от одноимённых заданий №2670, №2678 и №2691.'),
(2690,'stroymaterialy','Стройматериалы','Сделать в Мельнице 100 цемента из камней (пропуск 10 зб); сделать в Японском храме 25 Бруса секвойи; подарить друзьям 35 Снежков.','1 Мозги','Тип награды записан по источнику, подробнее не уточнён.'),
(2691,'podgotovka','Подготовка','Раздобыть 55 факелов; найти 35 подземных фонарей (пропуск 10 зб); попросить Звездочётов принести 20 Лучей добра.','10 Золиан, 1 Шоколадная','Одноимённое задание №2689 непосредственно предшествует №2690.'),
(2692,'zaval','Завал','Разгрести завал в Сырую темницу и спуститься в неё.','150 опыта, 1 Карамелька, 20 Палочек-выручалочек','Исторический сюжет; условия возвращения из локации здесь не указаны.')]

for id,slug,name,goals,reward,note in rows:
 slug=f'wind-{slug}-{id}';e=next((x for x in a if x['slug']==slug),None)
 if not e:e={'slug':slug,'name':name+f' — «Унесенные ветром», №{id}','category':'quests','type':'Задание линейки «Унесенные ветром»','purchase':'нет данных','sale':'нет данных','obtain':'нет данных','use':'нет данных','features':'нет данных','versions':'историческая версия ВКонтакте; редакция неизвестна','sources':[],'image':None,'links':[],'event':'Унесенные ветром','prior_records':[]};a.append(e)
 url=f'https://viver.my1.ru/publ/gamemission/q_wwind_{id-2662}/11-1-0-{id}';fields={'Цели':goals,'Награда':reward,'Соседние задания':f'Предыдущее: №{id-1}; следующее: №{id+1} — порядок по источнику, условия разблокировки не проверены.','Примечание':note};r={'original_id':f'viver-quests-{id}','original_category':'Задания','version':'историческая социальная версия VK; дата редакции неизвестна','date':'21.10.2018 — публикация; дата последующей редакции неизвестна','fields':fields,'confidence':'Фанатский справочник; актуальность и независимость не установлены.'};e['prior_records']=[x for x in e['prior_records'] if x.get('original_id')!=r['original_id']]+[r]
 if not any(x['url']==url for x in e['sources']):e['sources'].append({'url':url,'label':'ViveR_9: отдельная статья задания'})
by={int(x['slug'].rsplit('-',1)[-1]):x for x in a if x['slug'].startswith('wind-') and x['slug'].rsplit('-',1)[-1].isdigit()}
for i in range(2688,2692):
 l,r=by[i],by[i+1]
 for e,t,rel in [(l,r,'следующее задание по источнику'),(r,l,'предыдущее задание по источнику')]:
  obj={'category':'quests','slug':t['slug'],'name':t['name'],'relation':rel}
  if obj not in e['links']:e['links'].append(obj)
p.write_text(json.dumps(a,ensure_ascii=False,indent=2));print('4 задания; соседние связи по идентификаторам')

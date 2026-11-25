import json
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'data/quests.json';a=json.loads(p.read_text())
rows=[
(2699,'po-instrukcii','По инструкции','Найти 20 Гармошек из Весенней коллекции, 40 Тапков из Обувной коллекции (пропуск 15 зб); откопать 25 Аптечек из Военной коллекции.','3 Носка зомби, 111 000 монет','Первый пункт инструкции Даниэллы.'),
(2700,'chto-k-chemu','Что к чему?','Приготовить 30 Вишнёвого джема, выиграть Пингвин-яйцо во фруктовых автоматах и приготовить 25 Волчиума.','7 Вишнёвого цвета, 3 Сюрприза повара','Количество Пингвин-яиц в тексте источника не указано.'),
(2701,'moment-istiny','Момент истины','Разморозить 2 гномов в Сырой темнице.','1 Чёрный ящик','Источник указывает участие задания в создании Гнома-плаксы и Гнома-умника.'),
(2702,'uspeh','Успех','Угостить гномов 20 Грибной текилой, отдать 25 Острой росянки и подарить 15 Лучей добра.','2 000 опыта, 25 Стрел Купидона, 10 Компасов','После спасения Плакса и Умник радуются освобождению.')]

for id,slug,name,goals,reward,note in rows:
 slug=f'wind-{slug}-{id}';e=next((x for x in a if x['slug']==slug),None)
 if not e:e={'slug':slug,'name':name+f' — «Унесенные ветром», №{id}','category':'quests','type':'Задание линейки «Унесенные ветром»','purchase':'нет данных','sale':'нет данных','obtain':'нет данных','use':'нет данных','features':'нет данных','versions':'историческая версия ВКонтакте; редакция неизвестна','sources':[],'image':None,'links':[],'event':'Унесенные ветром','prior_records':[]};a.append(e)
 url=f'https://viver.my1.ru/publ/gamemission/q_wwind_{id-2662}/11-1-0-{id}';fields={'Цели':goals,'Награда':reward,'Соседние задания':f'Предыдущее: №{id-1}; следующее: №{id+1} — порядок по источнику, условия разблокировки не проверены.','Примечание':note};r={'original_id':f'viver-quests-{id}','original_category':'Задания','version':'историческая социальная версия VK; дата редакции неизвестна','date':'21.10.2018 — публикация; дата последующей редакции неизвестна','fields':fields,'confidence':'Фанатский справочник; актуальность и независимость не установлены.'};e['prior_records']=[x for x in e['prior_records'] if x.get('original_id')!=r['original_id']]+[r]
 if not any(x['url']==url for x in e['sources']):e['sources'].append({'url':url,'label':'ViveR_9: отдельная статья задания'})
by={int(x['slug'].rsplit('-',1)[-1]):x for x in a if x['slug'].startswith('wind-') and x['slug'].rsplit('-',1)[-1].isdigit()}
for i in range(2698,2702):
 l,r=by[i],by[i+1]
 for e,t,rel in [(l,r,'следующее задание по источнику'),(r,l,'предыдущее задание по источнику')]:
  obj={'category':'quests','slug':t['slug'],'name':t['name'],'relation':rel}
  if obj not in e['links']:e['links'].append(obj)
p.write_text(json.dumps(a,ensure_ascii=False,indent=2));print('4 задания; соседние связи по идентификаторам')

import json
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'data/quests.json';a=json.loads(p.read_text())
rows=[(2703,'dom-mily-dom','Дом милый дом','Вернуться на Снежный пик (пропуск 1 зб), затем на Санках слона вернуться на Домашний и забрать награду.','3 зомбакса, 3 Носка зомби','Последнее задание по странице источника: следующего задания там не указано.')]

for id,slug,name,goals,reward,note in rows:
 slug=f'wind-{slug}-{id}';e=next((x for x in a if x['slug']==slug),None)
 if not e:e={'slug':slug,'name':name+f' — «Унесенные ветром», №{id}','category':'quests','type':'Задание линейки «Унесенные ветром»','purchase':'нет данных','sale':'нет данных','obtain':'нет данных','use':'нет данных','features':'нет данных','versions':'историческая версия ВКонтакте; редакция неизвестна','sources':[],'image':None,'links':[],'event':'Унесенные ветром','prior_records':[]};a.append(e)
 url=f'https://viver.my1.ru/publ/gamemission/q_wwind_{id-2662}/11-1-0-{id}';fields={'Цели':goals,'Награда':reward,'Соседние задания':f'Предыдущее: №{id-1}; следующее задание на странице не указано. Условия разблокировки не проверены.','Примечание':note};r={'original_id':f'viver-quests-{id}','original_category':'Задания','version':'историческая социальная версия VK; дата редакции неизвестна','date':'21.10.2018 — публикация; дата последующей редакции неизвестна','fields':fields,'confidence':'Фанатский справочник; актуальность и независимость не установлены.'};e['prior_records']=[x for x in e['prior_records'] if x.get('original_id')!=r['original_id']]+[r]
 if not any(x['url']==url for x in e['sources']):e['sources'].append({'url':url,'label':'ViveR_9: отдельная статья задания'})
by={int(x['slug'].rsplit('-',1)[-1]):x for x in a if x['slug'].startswith('wind-') and x['slug'].rsplit('-',1)[-1].isdigit()}
for i in range(2702,2703):
 l,r=by[i],by[i+1]
 for e,t,rel in [(l,r,'следующее задание по источнику'),(r,l,'предыдущее задание по источнику')]:
  obj={'category':'quests','slug':t['slug'],'name':t['name'],'relation':rel}
  if obj not in e['links']:e['links'].append(obj)
p.write_text(json.dumps(a,ensure_ascii=False,indent=2));print('1 задание; соседние связи по идентификаторам')

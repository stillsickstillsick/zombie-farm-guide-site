import json
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'data/quests.json';a=json.loads(p.read_text())
rows=[
(2709,'zabytyy','Забытый','Достроить Лодку Странника и отправиться на Забытый остров.','15 Мачете, 15 Кирок, 15 Топоров','Условия возвращения на странице не указаны.'),
(2710,'proseka','Просека','Вырубить 15 таких пальм и 10 любых лиан; убрать 10 таких камней (пропуск 10 зб).','1 Коллекционер 2','Задание Забытого острова; виды пальм и камней текстом не определены.'),
(2711,'na-start','На старт','Отремонтировать Старую ракету.','1 Минутка на день','Задание Забытого острова; стоимость ремонта в этой статье не указана.'),
(2712,'prizemlenie','Приземление','Заправить Старую ракету и отправиться на Космический хутор.','30 Ножей','Источник относит задание к Забытому острову; стоимость заправки не указана.')]

for id,slug,name,goals,reward,note in rows:
 slug=f'star-harvest-{slug}-{id}';e=next((x for x in a if x['slug']==slug),None)
 if not e:e={'slug':slug,'name':name+f' — «Звездный урожай», №{id}','category':'quests','type':'Задание линейки «Звездный урожай»','purchase':'нет данных','sale':'нет данных','obtain':'нет данных','use':'нет данных','features':'нет данных','versions':'историческая версия ВКонтакте; редакция неизвестна','sources':[],'image':None,'links':[],'event':'Звездный урожай','prior_records':[]};a.append(e)
 url=f'https://viver.my1.ru/publ/gamemission/q_starh_{id-2703}/11-1-0-{id}'
 neighbours=(f'Предыдущее: №{id-1}; ' if id>2704 else 'Предыдущее на странице не указано; ')+f'следующее: №{id+1}. Порядок по источнику, условия разблокировки не проверены.'
 r={'original_id':f'viver-quests-{id}','original_category':'Задания','version':'историческая социальная версия VK; дата редакции неизвестна','date':'21.10.2018 — публикация; дата последующей редакции неизвестна','fields':{'Цели':goals,'Награда':reward,'Соседние задания':neighbours,'Примечание':note},'confidence':'Фанатский справочник; актуальность и независимость не установлены.'};e['prior_records']=[x for x in e['prior_records'] if x.get('original_id')!=r['original_id']]+[r]
 if not any(x['url']==url for x in e['sources']):e['sources'].append({'url':url,'label':'ViveR_9: отдельная статья задания'})
by={int(x['slug'].rsplit('-',1)[-1]):x for x in a if x['slug'].startswith('star-harvest-') and x['slug'].rsplit('-',1)[-1].isdigit()}
for i in range(2708,2712):
 l,r=by[i],by[i+1]
 for e,t,rel in [(l,r,'следующее задание по источнику'),(r,l,'предыдущее задание по источнику')]:
  obj={'category':'quests','slug':t['slug'],'name':t['name'],'relation':rel}
  if obj not in e['links']:e['links'].append(obj)
p.write_text(json.dumps(a,ensure_ascii=False,indent=2));print('4 задания; соседние связи по идентификаторам')

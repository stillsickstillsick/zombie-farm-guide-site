import json
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'data/quests.json';a=json.loads(p.read_text())
rows=[
(2723,'proshchanie','Прощание','Вернуться на Домашний остров; купить и установить Заводного жука; открыть 8 чемоданов туристов (пропуск за 5 зб).','1 Золотой орех, 1 Соломинка','Источник связывает обе награды с одной общей страницей; разновидность наград не уточнена.'),
(2724,'zhuk','Жук','Начать собирать Заводного жука; удобрить 30 фруктовых деревьев друзей (10 зб); заглянуть в 20 вёдер Рыбаков (7 зб).','15 Пряников, 15 Колокольчиков, 15 Изумрудных сердец','Стоимость пропуска приведена для соответствующих целей.'),
(2725,'taynoe-ushchele','Тайное ущелье','Закончить Заводного жука; отправиться в Тайное ущелье; провести там 24 часа (пропуск 15 зб).','3 Бозона Хиггса','Источник упоминает выращивание растений из Железных семечек; их способ получения здесь не указан.'),
(2726,'nevidannaya-ferma','Невиданная ферма','Собрать 5 Огурцов (5 зб); вырастить 10 Шестерени (10 зб); заказать у поваров 5 Серебряной пудры (15 зб).','5 Зомбаксов и 1500 опыта','Шестерень — растение. На странице нет следующего задания, хотя текст говорит «Продолжение следует».')]


for id,slug,name,goals,reward,note in rows:
 slug=f'star-harvest-{slug}-{id}';e=next((x for x in a if x['slug']==slug),None)
 if not e:e={'slug':slug,'name':name+f' — «Звездный урожай», №{id}','category':'quests','type':'Задание линейки «Звездный урожай»','purchase':'нет данных','sale':'нет данных','obtain':'нет данных','use':'нет данных','features':'нет данных','versions':'историческая версия ВКонтакте; редакция неизвестна','sources':[],'image':None,'links':[],'event':'Звездный урожай','prior_records':[]};a.append(e)
 url=f'https://viver.my1.ru/publ/gamemission/q_starh_{id-2703}/11-1-0-{id}'
 neighbours=(f'Предыдущее: №{id-1}; ' if id>2704 else 'Предыдущее на странице не указано; ')+(f'следующее: №{id+1}.' if id<2726 else 'Следующее задание на странице не указано.')+' Порядок по источнику, условия разблокировки не проверены.'
 r={'original_id':f'viver-quests-{id}','original_category':'Задания','version':'историческая социальная версия VK; дата редакции неизвестна','date':('21.10.2018' if id==2723 else '24.10.2018')+' — публикация; дата последующей редакции неизвестна','fields':{'Цели':goals,'Награда':reward,'Соседние задания':neighbours,'Примечание':note},'confidence':'Фанатский справочник; актуальность и независимость не установлены.'};e['prior_records']=[x for x in e['prior_records'] if x.get('original_id')!=r['original_id']]+[r]
 if not any(x['url']==url for x in e['sources']):e['sources'].append({'url':url,'label':'ViveR_9: отдельная статья задания'})
by={int(x['slug'].rsplit('-',1)[-1]):x for x in a if x['slug'].startswith('star-harvest-') and x['slug'].rsplit('-',1)[-1].isdigit()}
for i in range(2722,2726):
 l,r=by[i],by[i+1]
 for e,t,rel in [(l,r,'следующее задание по источнику'),(r,l,'предыдущее задание по источнику')]:
  obj={'category':'quests','slug':t['slug'],'name':t['name'],'relation':rel}
  if obj not in e['links']:e['links'].append(obj)
p.write_text(json.dumps(a,ensure_ascii=False,indent=2));print('4 задания; связаны с предыдущими по идентификаторам')

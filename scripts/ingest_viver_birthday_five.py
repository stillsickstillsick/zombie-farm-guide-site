import json
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'data/quests.json';a=json.loads(p.read_text())
rows=[(2656,'predchuvstvie','Предчувствие','Приготовить 15 Глазной настойки, 20 Кукурузных палочек и 15 шоколада.','10 лунных камней, 1 000 опыта','','Сюрприз','По сюжету Зомби отмечает пятилетие.'),(2657,'syurpriz','Сюрприз','Дать почтальону 20 Огня, 20 Японского гороха и 20 Глазной настойки.','1 Посылка, 1 Приглашение','Предчувствие','Собираемся в путь','В посылке — открытки и приглашение в Пионерский лагерь.'),(2658,'sobiraemsya-v-put','Собираемся в путь','Купить и достроить Юбилейную яхту; отправиться в Пионерский лагерь.','5 «Ба-бах!», 5 Изумрудных сердец','Сюрприз','Пионерский',''),(2659,'pionerskiy','Пионерский','Найти кекс у Гнома-шутника под шапкой-невидимкой; найти другой кекс в сундуке, срубив нужное дерево. Вид дерева источник не уточняет.','10 соли, 100 опыта, 10 йодированной соли','Собираемся в путь','Наводим порядок',''),(2660,'navodim-poryadok','Наводим порядок','Отремонтировать Бунгало в Пионерском лагере; создать Кекс PP в Бунгало.','10 золотой пыли, 5 метеоритов, 10 удобрений для деревьев 100%','Пионерский','Перерыв','В разделе превращения перечислены два Бунгало №857 и №858; направление превращения по тексту неясно.')]
for id,slug,name,goals,reward,prev,nxt,note in rows:
 slug=f'birthday5-{slug}-{id}';e=next((x for x in a if x['slug']==slug),None)
 if not e:e={'slug':slug,'name':name+' — «День Рождения Зомби»','category':'quests','type':'Задание пятилетия','purchase':'нет данных','sale':'нет данных','obtain':'нет данных','use':'нет данных','features':'нет данных','versions':'историческая версия ВКонтакте; редакция неизвестна','sources':[],'image':None,'links':[],'event':'День Рождения Зомби','prior_records':[]};a.append(e)
 url=f'https://viver.my1.ru/publ/gamemission/q_5year_{id-2655}/11-1-0-{id}';fields={'Цели':goals,'Награда':reward,'Соседние задания':(f'Предыдущее: «{prev}»; ' if prev else 'Предыдущее на странице не указано; ')+f'следующее: «{nxt}». Порядок по источнику, условия разблокировки не проверены.'}
 if note:fields['Примечание']=note
 r={'original_id':f'viver-quests-{id}','original_category':'Задания','version':'историческая социальная версия VK; дата редакции неизвестна','date':'21.10.2018 — публикация, дата последующей редакции неизвестна','fields':fields,'confidence':'Фанатский справочник; актуальность и независимость не установлены.'};e['prior_records']=[x for x in e['prior_records'] if x.get('original_id')!=r['original_id']]+[r]
 if not any(x['url']==url for x in e['sources']):e['sources'].append({'url':url,'label':'ViveR_9: отдельная статья задания'})
by={x['name'].split(' — «День Рождения Зомби»')[0]:x for x in a if x['slug'].startswith('birthday5-')}
for id,slug,name,goals,reward,prev,nxt,note in rows:
 for left,right in [(prev,name),(name,nxt)]:
  if left in by and right in by:
   for start,end,rel in [(left,right,'следующее задание по источнику'),(right,left,'предыдущее задание по источнику')]:
    e,t=by[start],by[end];o={'category':'quests','slug':t['slug'],'name':t['name'],'relation':rel}
    if o not in e['links']:e['links'].append(o)
p.write_text(json.dumps(a,ensure_ascii=False,indent=2));print('5 заданий пятилетия')
p=p.parent/'locations.json';a=json.loads(p.read_text())
for slug,id,short in [('planeta-zloki',2654,'Планета Злоки'),('zvezdnyy-pereval',2655,'Звёздный перевал')]:
 matches=[x for x in a if x['slug']==slug]
 if not matches:
  matches=[x for x in a if x['name']==short]
 if len(matches)!=1:print('Не добавлено предупреждение:',short,len(matches));continue
 e=matches[0];url=f'https://viver.my1.ru/publ/gamemission/q_spaceadv_{id-2590}/11-1-0-{id}';r={'original_id':f'viver-warning-{id}','original_category':'Задания','version':'историческая VK; редакция не установлена','date':'21.10.2018 — публикация; дата редакции неизвестна','fields':{'Предупреждение':f'Задание «{"Просчет" if id==2654 else "Бесконечность"}» описывает выход из локации навсегда. Механизм и возможность возвращения в современной версии не проверены.'},'confidence':'Историческое предупреждение фанатского источника.'};e['prior_records']=[x for x in e.get('prior_records',[]) if x.get('original_id')!=r['original_id']]+[r]
 if not any(x['url']==url for x in e['sources']):e['sources'].append({'url':url,'label':'ViveR_9: предупреждение в задании'})
p.write_text(json.dumps(a,ensure_ascii=False,indent=2))

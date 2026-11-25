import json
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'data/quests.json';a=json.loads(p.read_text())
rows=[(2651,'epitsentr','Эпицентр','Планета Злоки','Изготовить 10 болтов в Эйфелевой башне; получить 5 гаек; начать строить Отражатель.','5 Бабочек, 5 Китти, 5 пряников','Паника','Непонятки',''),(2652,'neponyatki','Непонятки','Планета Злоки','Создать 10 гвоздей (пропуск за 10 зб); создать 5 скотча; завершить Отражатель.','1 Чёрный ящик','Эпицентр','Напряжение',''),(2653,'napryazhenie','Напряжение','Планета Злоки','Создать Палочку в Отражателе, чтобы отразить луч.','1 Супер-урожай на день','Непонятки','Просчет',''),(2654,'proschet','Просчет','Планета Злоки','Отремонтировать Космическую пристань; навсегда покинуть Планету Злоки.','1 Подарок строителю','Напряжение','Бесконечность','Исторический текст говорит о выходе навсегда; современная возможность возврата не проверена.'),(2655,'beskonechnost','Бесконечность','Звёздный перевал','Вернуться домой на Машине времени и открыть сундук на месте Телефонной будки.','Золиан ×5, Радужный ×5, Бозон Хиггса ×1; «Радужный» ссылается на коллекцию, тип награды требует проверки.','Просчет','','Профессор предупреждает о выходе со Звёздного перевала навсегда; современная возможность возврата не проверена.')]

for id,slug,name,island,goals,reward,prev,nxt,note in rows:
 slug=f'cosmos-{slug}-{id}';e=next((x for x in a if x['slug']==slug),None)
 if not e:e={'slug':slug,'name':name+' — линейка «Космос»','category':'quests','type':'Задание линейки «Космос»','purchase':'нет данных','sale':'нет данных','obtain':'нет данных','use':'нет данных','features':'нет данных','versions':'историческая версия ВКонтакте; редакция неизвестна','sources':[],'image':None,'links':[],'event':'нет данных','prior_records':[]};a.append(e)
 url=f'https://viver.my1.ru/publ/gamemission/q_spaceadv_{id-2590}/11-1-0-{id}';fields={'Локация':island,'Цели':goals,'Награда':reward,'Соседние задания':f'Предыдущее: «{prev}»; '+(f'следующее: «{nxt}». ' if nxt else 'следующего задания на странице не указано. ')+'Порядок указан источником; разблокировка не проверена.'}
 if note:fields['Сюжет']=note
 r={'original_id':f'viver-quests-{id}','original_category':'Задания','version':'историческая социальная версия VK; дата редакции неизвестна','date':'21.10.2018 — публикация, дата последующей редакции неизвестна','fields':fields,'confidence':'Фанатский справочник; актуальность и независимость не установлены.'};e['prior_records']=[x for x in e['prior_records'] if x.get('original_id')!=r['original_id']]+[r]
 if not any(x['url']==url for x in e['sources']):e['sources'].append({'url':url,'label':'ViveR_9: отдельная статья задания'})
by={x['name'].split(' — линейка')[0]:x for x in a if x['slug'].startswith('cosmos-') and ' — линейка «Космос»' in x['name']}
for id,slug,name,island,goals,reward,prev,nxt,note in rows:
 for left,right in [(prev,name),(name,nxt)]:
  if left in by and right in by:
   for start,end,rel in [(left,right,'следующее задание по источнику'),(right,left,'предыдущее задание по источнику')]:
    e,t=by[start],by[end];o={'category':'quests','slug':t['slug'],'name':t['name'],'relation':rel}
    if o not in e['links']:e['links'].append(o)
p.write_text(json.dumps(a,ensure_ascii=False,indent=2));print('5 заданий')

#!/usr/bin/env python3
"""Проверенная линейка Засуха и механизмы Солнечного острова."""
import json,requests,hashlib
from pathlib import Path
from io import BytesIO
from PIL import Image
P=Path(__file__).resolve().parents[1];cs=['quests','buildings','materials','locations'];D={c:json.loads((P/'data'/f'{c}.json').read_text()) for c in cs};I={(c,x['slug']):x for c,arr in D.items() for x in arr};B='https://zombie-island.moy.su/';H={}
for p in (P/'img').rglob('*'):
 if p.is_file():H.setdefault(hashlib.sha256(p.read_bytes()).hexdigest(),str(p.relative_to(P)))
def add(cat,slug,name,url,pic,typ,fields):
 if (cat,slug) in I:return
 imageurl=B+'zombie-farm/ZombiFermaMania/'+pic;r=requests.get(imageurl,timeout=30);r.raise_for_status();im=Image.open(BytesIO(r.content));im.verify();h=hashlib.sha256(r.content).hexdigest();ext={'PNG':'.png','JPEG':'.jpg','GIF':'.gif'}[im.format];path=H.get(h)
 if not path:path=f'img/archive/drought-{slug}-{h[:12]}'+ext;(P/path).write_bytes(r.content);H[h]=path
 x={'slug':slug,'name':name,'category':cat,'type':typ,'purchase':'нет данных','sale':'нет данных','obtain':'нет данных','use':'нет данных','features':'нет данных','versions':'историческая браузерная социальная игра; платформа и редакция уточняются','sources':[{'url':B+url,'label':'Zombie-island: историческая статья'},{'url':B+'news/1_avgusta_zasukha_v_igre_zombi_ferma/2014-08-02-168','label':'Zombie-island: новость о линейке «Засуха»'}], 'image':{'path':path,'retrieved_from':imageurl,'attribution':'http://zombicity.info/zombie-farm/ZombiFermaMania/'+pic,'source_page':B+url,'note':'Файл без перекодирования с альтернативного хоста; побайтовое совпадение оригинальной ссылки не проверено.'},'links':[],'event':'Засуха — 2014','prior_records':[{'original_id':'drought-2014-'+slug,'original_category':typ,'version':'браузерная социальная игра; платформа не уточнена','date':'02.08.2014 — дата статьи, дальнейшие правки не датированы','fields':fields,'confidence':'Фанатский источник; возможны ошибки и отличия исторических версий.'}]};D[cat].append(x);I[cat,slug]=x
def link(a,b,r):
 x=I[a]; y=I[b]
 if not any(z.get('category')==b[0] and z.get('slug')==b[1] for z in x['links']):x['links'].append({'category':b[0],'slug':b[1],'name':y['name'],'relation':r})
quests=[
('redkaya-nakhodka','Редкая находка','redkaja_nakhodka','Найти 5 Ломов Строительной коллекции (пропуск 3); выиграть 5 Фанер в рулетках (10); подарить друзьям 100 досок с сообщением «Всё пригодится!» (3).','По 2 Колпака, Метлы и Палочки.'),
('vazhnaya-missiya','Важная миссия','vazhnaja_missija','Накопать 10 кафеля (пропуск 10); положить 200 пряников под Новогодние ёлки друзей (15); получить от друзей 15 Воды (5).','1 Сундук с Берега.'),
('puteshestvie','Путешествие','puteshestvie','Найти на складе и открыть Сундук; найти и достроить Дельтаплан; долететь до Солнечного острова. Все цели нельзя пропустить.','1 Изумрудная башня.'),
('chistka-territorii','Чистка территории','chistka_territorii','Убрать 15 камней (пропуск 15); убрать 20 деревьев (15); найти и достроить все 26 мостиков на острове (нельзя пропустить).','1 Опыт Волшебника.'),
('drevnie-mastera','Древние мастера','drevnie_mastera','Сделать в Тереме на Солнечном 5 прямых и 5 угловых деталей канала; достать 10 деталей со Склада и соединить с мостиками. Цели нельзя пропустить.','1 Коллекционер 2.'),
('pomoshch-gnomov','Помощь гномов','pomoshh_gnomov','Раздобудь 10 Слёз зомби (пропуск 5); сделать на Нефтяной вышке 15 чёрных сердец (5); заказать у поваров 15 Голов-гриб (3).','1 Подарок строителю.'),
('fontan-molodosti','Фонтан молодости','fontan_molodosti','Построить водный канал и проверить на протечки в Башне; нельзя пропустить. Канал по статье должен проходить через все мостики.','20 зомбаксов.'),
('dovolnye-gnomy','Довольные гномы','dovolnye_gnomy','Открыть сундук на Солнечном острове на месте Терема; нельзя пропустить.','1 Фемида.')]
for n,(sl,name,word,goal,reward) in enumerate(quests):
 url=f'blog/{word}_zombie_farm_mania_prokhozhdenie_zadaniya/2014-08-02-{3079+n}';pic=f'Zadaniya/39_zasuha/{word}_kvesty_zombie_farm_mania.png';add('quests','zasukha-'+sl+'-2014',name+' — «Засуха»',url,pic,'Задание линейки «Засуха»',{'Цели':goal,'Награда':reward,'Пропуски':'Числа в скобках — цена пропуска в зомбаксах по значкам источника; если цена не указана, она не установлена.'})
add('buildings','deltaplan-solnechnyy-2014','Дельтаплан — Солнечный остров','blog/deltaplan_postrojka_zombie_farm_mania/2014-08-02-3092','Postroyka_1/deltaplan_postrojka_zombie_farm.png','Телепорт',{'Получение':'Сундук с Берега — награда за «Важную миссию»; по «Путешествию» сундук нужно открыть на складе и достроить Дельтаплан. Купить и продать нельзя.','Строительство':'1: 15 синего пластилина, 10 стеклянных труб, 45 пружин — 170 опыта. 2: 15 фанеры, 20 воды, 5 лестниц — 120 опыта.','Цена и разногласие':'В статье Дельтаплана показаны 5 компасов, 50 000 монет и 3 Луча добра, без чёткого разделения направления. Статья острова для возвращения на Домашний указывает 5 компасов, 50 000 монет и 7 Лучей добра. Возможна разная цена направлений или ошибка; считать одинаковыми цены нельзя. После возвращения Дельтаплан превращается в сундук.'})
add('buildings','bashnya-solnechnyy-2014','Башня — Солнечный остров','blog/bashnja_postrojka_zombie_farm_mania/2014-08-02-3093','Postroyka_1/bashnja_postrojka_zombie_farm.png','Постройка острова',{'Место и функция':'На Солнечном острове, нельзя купить или продать. В Башне проверяется правильность построения водного канала; после правильной проверки он запускается.'})
add('buildings','terem-solnechnyy-2014','Терем — Солнечный остров','blog/terem_postrojka_zombie_farm_mania/2014-08-02-3094','Postroyka_1/terem_postrojka_zombie_farm.png','Постройка острова',{'Место и функция':'На Солнечном острове, нельзя купить или продать. Изготавливает 6 типов деталей водного канала. Не объединять с обычным Теремом только по одинаковому имени или картинке.','Рецепты':'№1 и №2: 15 блоков и 5 бруса секвойи; №3: 10 чёрных сердец и 10 Сонных качанов; №4: 10 фольги и 10 Глазных росянок; №5: 10 кафеля и 10 Голов-гриб; №6: 10 мела и 10 Слёз зомби.','Расхождение изображений':'В статье Терема иллюстрации №4 и №5 перепутаны относительно отдельных статей и новости. Рецепты переданы по текстовой подписи; отдельные карточки используют изображения из собственных статей.'})
for n in (1,2):
 id=3091 if n==1 else 3090;pic='mostik_2_dekoracija_zombie_farm.png' if n==1 else 'mostik_dekoracija_zombie_farm.png'
 add('buildings',f'mostik-{n}-solnechnyy-2014',f'Мостик {n} — Солнечный остров',f'blog/mostik_decorations_zombie_farm_mania/2014-08-02-{id}','Dekoraciya/Zasuha/'+pic,'Декорация острова',{'Место и строительство':'На Солнечном острове; для одного мостика 3 супер-клея, 25 блоков и 25 дров. Задание требует достроить все 26.','Сумма':'При одинаковой стоимости всех 26 мостиков: 78 супер-клея, 650 блоков и 650 дров. Эта сумма вычислена, а не приведена источником.'})
recipes=['15 блоков + 5 бруса секвойи','15 блоков + 5 бруса секвойи','10 чёрных сердец + 10 Сонных качанов','10 фольги + 10 Глазных росянок','10 кафеля + 10 Голов-гриб','10 мела + 10 Слёз зомби']
for i,rec in enumerate(recipes,1):
 fields={'Создание':f'В Тереме на Солнечном острове: {rec}. Купить и продать нельзя.','Применение':'Соединительные элементы водного канала; задача «Фонтан молодости» требует канал через все мостики. По новости для решения использовалось '+('27 деталей №1' if i==1 else '25 деталей №2' if i==2 else 'по 8 деталей каждого типа №3–№6')+'. Размещение зависит от схемы.'}
 if i in (4,5):fields['Оговорка изображения']='Номера картинок №4 и №5 в статье Терема поменяны местами относительно отдельной статьи и новости; для карточки использована картинка отдельной статьи.'
 add('materials',f'detal-{i}-kanala-solnechnyy-2014',f'Деталь №{i} водного канала',f'blog/detal_1_decorations_zombie_farm_mania/2014-08-02-{3095+i}',f'Dekoraciya/Zasuha/detal{i}_zombie_farm_mania.png','Декорация канала',fields)
for n,row in enumerate(quests):
 k=('quests','zasukha-'+row[0]+'-2014')
 if n:link(k,('quests','zasukha-'+quests[n-1][0]+'-2014'),'предыдущее задание')
 if n<len(quests)-1:link(k,('quests','zasukha-'+quests[n+1][0]+'-2014'),'следующее задание')
 if n>=2:link(k,('locations','solnechnyy-ostrov-zasukha'),'связанная локация')
for slug in ['deltaplan-solnechnyy-2014','bashnya-solnechnyy-2014','terem-solnechnyy-2014','mostik-1-solnechnyy-2014','mostik-2-solnechnyy-2014']:link(('buildings',slug),('locations','solnechnyy-ostrov-zasukha'),'связана с локацией')
for i in range(1,7):link(('buildings','terem-solnechnyy-2014'),('materials',f'detal-{i}-kanala-solnechnyy-2014'),'создаваемая деталь')
for c in cs:(P/'data'/f'{c}.json').write_text(json.dumps(D[c],ensure_ascii=False,indent=2)+'\n')
print('8 квестов, 5 построек и 6 деталей')

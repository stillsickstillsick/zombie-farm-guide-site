from pathlib import Path
import json
p=Path(__file__).resolve().parents[1]; f=p/'data/buildings.json'; a=json.loads(f.read_text()); by={x['slug']:x for x in a}
rows=[
('kukolnyy-teatr','https://zombi.at.ua/board/postrojki/sdelaj_sam/kukolnyj_teatr/23-1-0-1257','https://zombie-island.moy.su/blog/kukolnyj_teatr_postrojka_zombie_farm_mania/2014-07-17-3060','Отдельная статья ZOMBIA размещена 07.05.2015; дата последней редакции неизвестна. В подписи иконок источника есть ошибки: например, иконка циркового шара подписана «Подушка». Связанная статья ЗомбиСити называет 25 цирковых шаров, 3 веера и 10 огненных обручей; затем 25 фантиков, 10 бигуди и 20 газет. Цена 2 500 000 монет, продажа 250 000, 24 часа и 30 прокруток — сведения статьи, а не подтверждение механизма первоначальной выдачи. Она одновременно пишет о покупке после квеста «Мечты» и о выдаче за этот квест; сам квест требует достроить театр, уже находящийся на складе. Этот вопрос остаётся открытым.'),
('karavella','https://zombi.at.ua/board/postrojki/ostrova_zombi_ferma/karavella/10-1-0-1254','https://zombie-island.moy.su/blog/piratskaja_karavella_zombie_farm_ostrov_piratov/2013-10-28-2288','Отдельная страница ZOMBIA размещена 07.05.2015, дата редакции неизвестна. ЗомбиСити указывает 250 дублонов, трюм 1000, 7 мест плюс капитан, разовое путешествие на Жуткий остров и необходимость Пиратского сундука. Стадии: 40 брёвен пальмы, 10 стали и 5 синих сердец; затем 30 досок, 5 резины и 5 болтов. Названия ресурсов на ZOMBIA как alt-тексты неверны; сравнение выполнено по файлам и подписанным изображениям ЗомбиСити.'),
('shkhuna','https://zombi.at.ua/board/postrojki/ostrova_zombi_ferma/shkhuna/10-1-0-1253','https://zombie-island.moy.su/blog/piratskij_korabl_zombie_farm_ostrov_piratov/2013-10-29-2286','Отдельная страница ZOMBIA размещена 07.05.2015, дата редакции неизвестна. ЗомбиСити указывает 100 дублонов, трюм 450, 5 мест плюс капитан и путешествие на Таинственный остров; нужен Пиратский сундук. Стадии: 30 брёвен пальмы, 10 лент и 5 канатов; затем 10 секвойи, 5 бумаги и 5 флюгеров. ZombiTime в поисковом индексе противоречиво пишет «5 с капитаном» и «остров Сокровищ»; сама страница при проверке не загрузилась, поэтому эти сведения считаются неподтверждёнными и могут быть ошибкой или другой редакцией.'),
('lodka','https://zombi.at.ua/board/postrojki/ostrova_zombi_ferma/lodka/10-1-0-1252','https://zombie-island.moy.su/news/25_oktjabrja_2013_dolgozhdannoe_piratskoe_obnovlenie/2013-10-26-125','Отдельная страница ZOMBIA размещена 07.05.2015, дата редакции неизвестна: 25 дублонов, грузоподъёмность 150, 5 мест плюс капитан, разовое путешествие на остров Сокровищ. В новости о пиратском обновлении указаны трюм 150 и отдельный сундук на 50 единиц; это исторические условия, возможны изменения. Подписи alt у иконок ZOMBIA ошибочны, стадии требуют сверки по подписанному источнику.'),
('vetryanoy-generator','https://zombi.at.ua/board/postrojki/srednij_uroven/vetrjanoj_generator/12-1-0-1256',None,'Отдельная карточка ZOMBIA размещена 07.05.2015, дата последней редакции неизвестна: 57 уровень, 1 700 000 монет, 300 опыта; генератор преобразует инвентарь с помощью Лучей добра. Подписи alt ресурсов ошибочны или отсутствуют, поэтому ингредиенты по одним этим подписям не устанавливаются.'),
]
for slug,u,v,desc in rows:
 x=by[slug]
 for s in x['sources']:
  if s['url']==u:s['label']='ZOMBIA: отдельная карточка прочитана; размещена 07.05.2015'
 if not any(s['url']==u for s in x['sources']):x['sources'].append({'url':u,'label':'ZOMBIA: отдельная карточка, размещена 07.05.2015'})
 if v and not any(s['url']==v for s in x['sources']):x['sources'].append({'url':v,'label':'Zombie-island: отдельная статья; связана с ЗомбиСити'})
 rid='individually-verified-zombia-2015-'+slug
 if not any(r.get('original_id')==rid for r in x['prior_records']):x['prior_records'].append({'original_id':rid,'original_category':'Проверка отдельной статьи и расхождений','version':'браузерная социальная версия; редакция и возможные изменения неизвестны','date':'07.05.2015 — дата размещения страницы ZOMBIA, не дата последней правки','fields':{'Проверка и сравнение':desc},'confidence':'Фанатские источники; возможна зависимость между ними. В ZOMBIA alt-тексты ряда иконок недостоверны; ZombiTime не удалось прочитать напрямую.'})
z=by['shkhuna']; zurl='http://zombitime.com/shhuna'
if not any(x['url']==zurl for x in z['sources']): z['sources'].append({'url':zurl,'label':'ZombiTime: расхождения по поисковому индексу; страница не открылась'})
f.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n')
s=p/'data/sources.json'; data=json.loads(s.read_text())
for x in data:
 if x['number']==5:
  t=' Отдельно прочитаны карточки Лодки, Шхуны, Каравеллы, Кукольного театра и Ветряного генератора: дата размещения 07.05.2015, дата редакции неизвестна; alt-подписи материалов часто ошибочны.'
  if t not in x['summary']:x['summary']+=t
s.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')

#!/usr/bin/env python3
"""Одиннадцать исторических заданий цепочки «Спасти праздник» (не путать с одноимёнными квестами других серий)."""
from pathlib import Path
from io import BytesIO
import json, hashlib, requests
from PIL import Image
P=Path(__file__).resolve().parents[1]; cats=['quests','locations','buildings']; D={c:json.loads((P/'data'/f'{c}.json').read_text()) for c in cats}; I={(c,x['slug']):x for c,items in D.items() for x in items}; base='https://zombie-island.moy.su/'; H={}
for f in (P/'img').rglob('*'):
 if f.is_file():H.setdefault(hashlib.sha256(f.read_bytes()).hexdigest(),str(f.relative_to(P)))
# Нумерация статей и имена изображений перепроверены по списку линейки и отдельным страницам.
rows=[
('nachalo-istorii','Начало истории','nachalo_istorii','kvesty_nachalo_istorii.png','Обменять 25 коллекций Деда Мороза (пропуск 5 зомбаксов); найти 15 любых предметов Ёлочной коллекции (5); накопать 50 секретных кладов у друзей (5).','1 Камин.'),
('kamin','Камин','kamin','kvesty_kamin.png','Найти Камин на Складе и поставить на Домашнем; начать строить Камин. Обе цели нельзя пропустить.','По 1 Колпаку, Метле и Палочке.'),
('strannosti-raz','Странности раз','strannosti_raz','kvesty_strannost_raz.png','Приготовить 15 Глазных супов (пропуск 7); 25 Вишнёвых джемов (5); посолить 35 бочек поварам (5). Валюта пропуска — зомбаксы по значкам источника.','1 Подарок строителю.'),
('gostya','Гостья','gostja','kvesty_gostya.png','Накопать 7 Хреней коллекции Майя (пропуск 10); собрать 25 находок у Звездочёта (3); раздобыть 55 Любви (7).','550 опыта, 5 дублонов, 10 Быстрых фруктов.'),
('mozgi','Мозги','mozgi','kvesty_mozgi.png','Закопать 20 друзей (пропуск 10); надеть костюм «Мозги» (нельзя пропустить); создать 15 мозгов в Останкино, Японском храме или Свободе (15).','7 Мозгов.'),
('v-zalozhnikakh','В заложниках','v_zalozhnikakh','kvesty_v_zalozhnikah.png','Достроить Камин и попасть в Сказочный лес. Обе цели нельзя пропустить.','15 соли, 15 йодированной соли, 500 опыта.'),
('v-skazochnom-lesu','В сказочном лесу','v_skazochnom_lesu','kvesty_v_skazochnom_lesu.png','Вырубить 15 бумажных елей (пропуск 10); убрать 10 шишек (7) и 10 варежек (7).','1 Носок зомби.'),
('ideya-snegurochki','Идея Снегурочки','ideja_snegurochki','kvesty_ideya_snegurochki.png','Сделать в Бумажном замке 5 прямых и 5 угловых дорожек; достать 10 дорожек со Склада и соединить. Все цели нельзя пропустить.','По 25 Бабочек, Барабашек и Тыкв Z.'),
('strannosti-dva','Странности два','strannosti_dva','kvesty_strannost_dva.png','Найти снежные кучи и слепить 3 снеговика; выманить 3 Админов; вовремя выполнить их задания и удивить 3 Админов. Все цели нельзя пропустить.','5 зомбаксов.'),
('po-planu','По плану','po_planu','kvesty_po_planu.png','Найти и восстановить 3 основания Праздничных елей; проложить ко всем дорожки и проверить цепь на разрывы. Обе цели нельзя пропустить.','По одному Санте в голубой, оранжевой и зелёной шапке.'),
('proshchanie','Прощание','proshhanie','kvesty_proshhanie.png','Установить на острове одну новую праздничную декорацию (пропуск 5 зомбаксов).','1 Полярный носок.')]
def link(a,b,r):
 x=I[a]; y=I[b]
 if not any(i.get('category')==b[0] and i.get('slug')==b[1] for i in x['links']):x['links'].append({'category':b[0],'slug':b[1],'name':y['name'],'relation':r})
for n,(short,name,word,pic,goals,reward) in enumerate(rows):
 slug='spasti-prazdnik-'+short+'-2014'; k=('quests',slug)
 if k in I:continue
 article=f'blog/{word}_zombie_farm_prokhozhdenie_kvestov_zombie_mania/2014-12-20-{3391+n}'; ip='zombie-farm/2014/1/'+pic; r=requests.get(base+ip,timeout=25);r.raise_for_status(); img=Image.open(BytesIO(r.content));img.verify();h=hashlib.sha256(r.content).hexdigest(); ext={'PNG':'.png','JPEG':'.jpg','GIF':'.gif'}[img.format];path=H.get(h)
 if not path:path='img/archive/fairy-quest-'+short+'-'+h[:12]+ext;(P/path).write_bytes(r.content);H[h]=path
 x={'slug':slug,'name':name+' — «Спасти праздник»','category':'quests','type':'Задание линейки «Спасти праздник»','purchase':'нет данных','sale':'нет данных','obtain':'нет данных','use':'нет данных','features':'нет данных','versions':'историческая браузерная социальная игра; платформа и редакция уточняются','sources':[{'url':base+article,'label':'Zombie-island: отдельная статья задания'},{'url':base+'blog/spasti_prazdnik_zombie_farm_prokhozhdenie_kvestov_zombi_mania/2014-12-20-3390','label':'Zombie-island: список последовательности линейки'}], 'image':{'path':path,'retrieved_from':base+ip,'attribution':'http://zombicity.info/'+ip,'source_page':base+article,'note':'Подписанное изображение с альтернативного хоста, сохранено без перекодирования; совпадение с оригинальной ссылкой не проверено.'},'links':[],'event':'Спасти праздник — 2014','prior_records':[{'original_id':f'fairy-quest-{3391+n}','original_category':'Квесты','version':'браузерная игра; платформа не уточнена','date':'20.12.2014 — дата статьи; поздние правки не датированы','fields':{'Цели':goals,'Награда':reward,'Обозначение':'Числа пропуска в скобках обозначают зомбаксы по значкам источника. Независимое подтверждение условий и платформ не установлено.'},'confidence':'Фанатский источник, возможны опечатки, изменения версии и поздние правки.'}]};D['quests'].append(x);I[k]=x
for n,row in enumerate(rows):
 a=('quests','spasti-prazdnik-'+row[0]+'-2014')
 if n:link(a,('quests','spasti-prazdnik-'+rows[n-1][0]+'-2014'),'предыдущее задание по источнику')
 if n<len(rows)-1:link(a,('quests','spasti-prazdnik-'+rows[n+1][0]+'-2014'),'следующее задание по источнику')
 if n>=5:link(a,('locations','zombicity-island-3405'),'место действия линейки')
for q,b in [('nachalo-istorii','kamin-skazochnyy-les-2014'),('kamin','kamin-skazochnyy-les-2014'),('v-zalozhnikakh','kamin-skazochnyy-les-2014'),('ideya-snegurochki','bumazhnyy-zamok-2014'),('po-planu','prazdnichnaya-el-2014')]:link(('quests','spasti-prazdnik-'+q+'-2014'),('buildings',b),'объект задания')
link(('quests','spasti-prazdnik-strannosti-dva-2014'),('quests','usloviya-pobedy-skazochnyy-les-2014'),'случайные мини-задания Админов')
for c in cats:(P/'data'/f'{c}.json').write_text(json.dumps(D[c],ensure_ascii=False,indent=2)+'\n')
print('Обработаны',len(rows),'квестов линейки «Спасти праздник»')

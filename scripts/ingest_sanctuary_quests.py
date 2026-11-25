#!/usr/bin/env python3
from pathlib import Path
from io import BytesIO
import requests,hashlib,json
from PIL import Image
P=Path(__file__).resolve().parents[1]; cs=['quests','locations','buildings'];D={c:json.loads((P/'data'/f'{c}.json').read_text()) for c in cs};I={(c,x['slug']):x for c,a in D.items() for x in a};base='https://zombie-island.moy.su/';H={}
for p in (P/'img').rglob('*'):
 if p.is_file():H.setdefault(hashlib.sha256(p.read_bytes()).hexdigest(),str(p.relative_to(P)))
rows=[('plan-b-svyatilishche-2015','План Б — Космос',3751,'plan_b',11,{'Цели':'Достроить Луноход; отправиться в Святилище. По одному разу.','Награда':'1 Чёрный ящик.'}),('taynoe-zele-svyatilishche-2015','Тайное зелье — Космос',3752,'tajnoe_zele',12,{'Цели':'Найти в ящиках 4 осколка древней Скрижали; восстановить Скрижаль; отремонтировать Стекольную печь.','Награда':'15 Бабочек, 15 Чмоков, 15 Барабашек.','Архивная подсказка':'Статья ZombieTime в архивном снимке 03.09.2016 подписывает изображение как расположение печи, Скрижали и ящиков. Сам файл при проверке не найден в Wayback; положение объектов не установлено.'}),('bezyskhodnost-svyatilishche-2015','Безысходность — Космос',3753,'bezyskhodnost',13,{'Цели':'Отремонтировать 8 насосов; сделать 20 труб в Стекольной печи; решить головоломку и запустить механизм.','Награда':'По 2 элемента Колпак, Метла и Палочка.','Уточнение':'В справочнике отдельно описаны два типа насоса, но число объектов, которые нужно отремонтировать по квесту, равно восьми; точная схема соединения не установлена.'}),('na-grani-svyatilishche-2015','На грани — Космос',3754,'na_grani',14,{'Цель':'Вырастить 5 Сахарик в Святилище.','Награда':'Мозги на 7 дней — 1.'}),('povorot-svyatilishche-2015','Поворот — Космос',3755,'povorot',15,{'Цель':'Навсегда покинуть Святилище на Луноходе — 1 раз. Внимание: по формулировке источника действие необратимо.','Награда':'5 зомбаксов.'})]
def link(a,b,r):
 x=I[a];y=I[b]
 if not any(j.get('category')==b[0] and j.get('slug')==b[1] for j in x['links']):x['links'].append({'category':b[0],'slug':b[1],'name':y['name'],'relation':r})
for slug,name,num,word,pic,fields in rows:
 if ('quests',slug) in I:continue
 a=f'blog/{word}_zombie_farm_prokhozhdenie_kvesta/2015-06-26-{num}';ip=f'zombie-farm/2015/14/{pic}.png';r=requests.get(base+ip,timeout=20);r.raise_for_status();Image.open(BytesIO(r.content)).verify();h=hashlib.sha256(r.content).hexdigest();path=H.get(h)
 if not path:path=f'img/archive/cosmic-quest-{slug}-{h[:12]}.png';(P/path).write_bytes(r.content);H[h]=path
 x={'slug':slug,'name':name,'category':'quests','type':'Космическая линейка','purchase':'нет данных','sale':'нет данных','obtain':'нет данных','use':'нет данных','features':'нет данных','versions':'историческая браузерная социальная игра; платформа и редакция уточняются','sources':[{'url':base+a,'label':'Zombie-island: отдельная статья квеста'}],'image':{'path':path,'retrieved_from':base+ip,'attribution':'http://zombicity.info/'+ip,'source_page':base+a,'note':'Исходный файл без перекодирования с альтернативного хоста; идентичность оригинальной ссылке не проверена.'},'links':[],'event':'Космос — Святилище 2015','prior_records':[{'original_id':'sanctuary-quest-'+str(num),'original_category':'Задания','version':'браузерная игра; платформа неизвестна','date':'26.06.2015 — дата статьи, дальнейшие правки не датированы','fields':fields,'confidence':'Фанатское прохождение, редакция и независимая проверка не установлены.'}]}
 if num==3752:x['sources'].append({'url':'https://web.archive.org/web/20160903104440/http://zombitime.com/tajnoe-zele','label':'ZombieTime, архивная страница от 03.09.2016; файл карты не извлечён'})
 D['quests'].append(x);I['quests',slug]=x
 link(('quests',slug),('locations','svyatilishche'),'место события')
for a,b in zip(rows,rows[1:]):link(('quests',a[0]),('quests',b[0]),'следующее задание по источнику');link(('quests',b[0]),('quests',a[0]),'предыдущее задание по источнику')
for b in ['skrizhal-svyatilishche','stekolnaya-pech-svyatilishche']:link(('quests','taynoe-zele-svyatilishche-2015'),('buildings',b),'объект задания')
for b in ['nasos-1-svyatilishche','nasos-2-svyatilishche','stekolnaya-pech-svyatilishche']:link(('quests','bezyskhodnost-svyatilishche-2015'),('buildings',b),'объект задания')
link(('quests','plan-b-svyatilishche-2015'),('buildings','lunokhod'),'объект задания')
for c in cs:(P/'data'/f'{c}.json').write_text(json.dumps(D[c],ensure_ascii=False,indent=2)+'\n')

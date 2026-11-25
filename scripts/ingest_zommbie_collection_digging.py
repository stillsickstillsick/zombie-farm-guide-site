#!/usr/bin/env python3
"""Исторический список мест раскопок: явное сопоставление заголовков, без слияния похожих коллекций."""
import json,re,requests
from bs4 import BeautifulSoup
from pathlib import Path
P=Path(__file__).resolve().parents[1]
url='https://zommbie.at.ua/load/dopolnitelnoe_menju/gde_kopat_kollekciie/gde_kopajutsja_koll/9-1-0-11'
r=requests.get(url,timeout=25);r.raise_for_status();t=BeautifulSoup(r.content,'html.parser').get_text('\n',strip=True)
start=t.index('Где копать звездную коллекцию:');end=t.index('\nКатегория',start);text=t[start:end]
pairs=re.findall(r'Где копать ([^\n:?!]+)[\s:?!]*\n([^\n]+)',text,re.I)
lookup={re.sub(r'\s+',' ',a.strip().lower()):b.strip() for a,b in pairs}
mapping={'звездную коллекцию':'zvyozdnaya-kollektsiya','луксорскую коллекцию':'luksorskaya-kollektsiya','байкерскую коллекцию':'baykerskaya-kollektsiya','коллекцию знаков':'kollektsiya-znakov','ручную коллекцию':'ruchnaya-kollektsiya','обувную коллекцию':'obuvnaya-kollektsiya','очень страшную коллекцию':'ochen-strashnaya-kollektsiya','строительную коллекцию':'stroitelnaya-kollektsiya','столовую коллекцию':'stolovaya-kollektsiya','редкую коллекцию':'redkaya-kollektsiya','автомобильную коллекцию':'avtomobilnaya-kollektsiya','туристическую коллекцию':'turisticheskaya-kollektsiya','домашнюю коллекцию':'domashnyaya-kollektsiya','коллекцию игрушек':'kollektsiya-igrushek','елочную коллекцию':'yolochnaya-kollektsiya','коллекцию белого кролика':'kollektsiya-belogo-krolika','коллекцию цветов':'kollektsiya-tsvetov','коллекцию деда мороза':'kollektsiya-deda-moroza','коллекцию анти-зомби':'kollektsiya-anti-zombi','коллекцию брендов':'kollektsiya-brendov','весеннюю коллекцию':'vesennyaya-kollektsiya','тинейджерскую коллекцию':'tineyd-erskaya-kollektsiya','коллекцию компа':'kollektsiya-kompa','морскую коллекцию':'morskaya-kollektsiya','пляжную коллекцию':'plya-naya-kollektsiya','коллекцию майя':'kollektsiya-mayya','секретную коллекцию':'sekretnaya-kollektsiya','гипер-коллекцию':'giper-kollektsiya','коллекцию хеллоуина':'kollektsiya-khellouina','президентскую коллекцию':'prezidentskaya-kollektsiya','зимнюю коллекцию':'zimnyaya-kollektsiya','школьную коллекцию':'shkolnaya-kollektsiya','райскую коллекцию':'rayskaya-kollektsiya','японскую коллекцию':'yaponskaya-kollektsiya','адскую коллекцию':'adskaya-kollektsiya','любовную коллекцию':'lyubovnaya-kollektsiya','подземельную коллекцию':'podzemelnaya-kollektsiya','коллекцию рыбака':'kollektsiya-rybaka','пиратскую коллекцию':'piratskaya-kollektsiya','военную коллекцию':'voennaya-kollektsiya'}
p=P/'data/collections.json';items=json.loads(p.read_text());by={x['slug']:x for x in items};count=0
for title,slug in mapping.items():
 if title not in lookup: print('not found',title);continue
 x=by[slug];rid='zommbie-dig-'+slug
 if not any(s['url']==url for s in x['sources']):x['sources'].append({'url':url,'label':'zommbie.at.ua: где искать коллекции'})
 rec={'original_id':rid,'original_category':'Коллекции','version':'историческая браузерная версия, платформа не указана','date':'10.01.2014 — дата в каталоге; дата редакции материала неизвестна','fields':{'Где искать по списку сайта':lookup[title],'Оговорка':'Список может относиться к разным условиям, инструментам и периодам игры; не доказывает гарантированное выпадение. Заявления «только» и «невозможно» относятся лишь к времени и версии источника.'},'confidence':'Фанатский список без вероятностей и уточнения площадки; независимость от других источников не установлена.'}
 x.setdefault('prior_records',[]);x['prior_records']=[r for r in x['prior_records'] if r.get('original_id')!=rid]+[rec];count+=1
p.write_text(json.dumps(items,ensure_ascii=False,indent=2))
p=P/'data/materials.json';items=json.loads(p.read_text()); data={'mylo':'Мыло копается под сакурой в горшке.','gazety':'Газеты можно накопать в зимних декорациях, в ледяных глыбах, в ковре самолёте.','kafel':'Кафель можно накопать под бизнес-центром, под белым домом.'}
for x in items:
 if x['slug'] not in data:continue
 if not any(s['url']==url for s in x['sources']):x['sources'].append({'url':url,'label':'zommbie.at.ua: исторические подсказки по раскопкам'})
 rid='zommbie-dig-'+x['slug'];rec={'original_id':rid,'original_category':'Материалы','version':'браузерная версия; платформа не уточнена','date':'10.01.2014 — дата в каталоге; дата редакции неизвестна','fields':{'Раскопки по источнику':data[x['slug']]},'confidence':'Фанатская подсказка без вероятностей и уточнения инструмента; требуется проверка версии игры.'}
 x.setdefault('prior_records',[]);x['prior_records']=[r for r in x['prior_records'] if r.get('original_id')!=rid]+[rec]
p.write_text(json.dumps(items,ensure_ascii=False,indent=2));print('collections:',count,'materials:',len(data))

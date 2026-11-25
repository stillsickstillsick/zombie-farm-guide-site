"""Selected manually verified facts from Zombie-island.moy.su/ZombiCity mirror."""
from pathlib import Path
import json,requests,hashlib
P=Path(__file__).resolve().parents[1];cats=['materials','buildings','economy'];D={c:json.loads((P/'data'/f'{c}.json').read_text()) for c in cats}
def get(c,name,slug,typ):
 e=next((x for x in D[c] if x['name']==name),None)
 if not e:e={'slug':slug,'name':name,'category':c,'type':typ,'purchase':'нет данных','sale':'нет данных','obtain':'нет данных','use':'нет данных','features':'нет данных','versions':'браузерные Зомби Ферма и Зомби Мания; платформу и редакцию уточнить','sources':[],'image':None,'links':[],'event':'нет данных','original_category':typ};D[c].append(e)
 return e
def add(e,rid,url,fields):
 e.setdefault('prior_records',[]);e['prior_records']=[x for x in e['prior_records'] if x.get('original_id')!=rid]+[{'original_id':rid,'original_category':e.get('original_category',''), 'version':'браузерная Зомби Ферма / Зомби Мания, платформа не уточнена','date':'дата URL — дата публикации, редакция могла обновляться позже','fields':fields,'confidence':'Прочитана отдельная статья. Иллюстрации и ссылки ведут к ЗомбиСити; независимость не доказана. Исторические параметры требуют сверки редакции.'}]
 if not any(x['url']==url for x in e['sources']):e['sources'].append({'url':url,'label':'Zombie-island.moy.su: прочитана статья; связь с ЗомбиСити по ссылкам и иллюстрациям'})
 return e
url='https://zombie-island.moy.su/blog/zombie_farm_shkola/2012-07-18-270';school=get('buildings','Школа','shkola','Постройка');add(school,'moy-shkola-270',url,{'Доступ и цена':'с 1 уровня; 50 000 монет покупка, 5000 продажа; требуется открыть квест «Школа»','Стадия 1':'25 блоков + 30 белой краски + 50 шестерён; 100 опыта','Стадия 2':'15 болтов + 50 металла + 20 труб; 200 опыта','Стадия 3':'15 листов золота + 15 гаек + 15 фанеры; 300 опыта','Производство':'1 книга: 5 газет + 5 шестерён; 1 мел: 10 цемента + 2 супер-клея. Также снежные буквы русского алфавита.','Копание':'байкерская, автомобильная и коллекция знаков; металлолом, бесплатные лопаты, опыт и монеты.'})
url2='https://zombie-island.moy.su/blog/zombi_ferma_zerkalo/2012-07-17-30';mirror=get('materials','Зеркало','zerkalo','Материал');add(mirror,'moy-zerkalo-30',url2,{'Цена':'покупка 1 зомбакс; продажа 900 монет','Производство':'в улучшенном университете: 5 стекла + 1 фольга → зеркало','Применение':'Часовая башня, шатёр, огромная ёлка, школьный автобус, Летающая тарелка, другие постройки','Источники':'сокровище «Весенний фонтан»; бесплатные подарки дают стекло и фольгу'})
url3='https://zombie-island.moy.su/blog/zombi_ferma_mikroskhema/2012-07-18-57';micro=get('materials','Микросхема','mikroskhema','Материал');add(micro,'moy-mikroskhema-57',url3,{'Цена':'покупка 2 зомбакса; продажа 1000 монет','Получение':'получить пересланную лампочку, которая превращается в микросхему; чемоданы туристов, Богатырский и Скромный презенты','Применение':'Часовая башня, батискаф, голубая ракета, школьный автобус, мобильный телефон, шаттл и другие постройки'})
url4='https://zombie-island.moy.su/blog/gde_kopat_najti_sekretnyj_klady_zombie_farm_mania/2013-03-22-1825';treasure=get('economy','Секретный клад','sekretnyy-klad','Механика');add(treasure,'moy-secret-treasure-1825',url4,{'Добыча':'В историческом описании — под игровыми объектами у друзей, где допускается копание; расположение случайное.','Число и период':'Источник утверждает: 7 кладов на острове; при 1–7 предметах — раз в неделю под каждым; на домашнем острове больше. Эти числа не подтверждены для других версий и требуют проверки.','Содержимое':'опыт, монеты, материалы и различные коллекции; состав зависит от версии'})
for name in ['Блоки','Белая краска','Шестерня','Болт','Металл','Труба','Лист золота','Гайка','Фанера','Газеты','Книги','Мел','Цемент','Супер-клей']:
 m=next((x for x in D['materials'] if x['name']==name),None)
 if m and not any(x.get('category')=='materials' and x.get('slug')==m['slug'] for x in school['links']):school['links'].append({'category':'materials','slug':m['slug'],'name':m['name'],'relation':'упоминается в стадиях или производстве Школы'})
# Original illustration served from a known mirror; no recompression.
original='http://zombicity.info/zombie-farm/ZombiFermaMania/Materials/mikroskhema-materials-zombie-farm-mania.png';mapped=original.replace('http://zombicity.info','https://zombie-island.moy.su')
try:
 r=requests.get(mapped,timeout=6);r.raise_for_status();b=r.content;assert b.startswith(b'\x89PNG\r\n\x1a\n');h=hashlib.sha256(b).hexdigest();lookup={hashlib.sha256(x.read_bytes()).hexdigest():x for x in (P/'img').rglob('*') if x.is_file()};f=lookup.get(h,P/'img/archive'/('mikroskhema-'+h[:12]+'.png'))
 if not f.exists():f.write_bytes(b)
 micro['image']={'path':str(f.relative_to(P)),'retrieved_from':mapped,'attribution':original,'source_page':url3,'note':'Изображение получено с зеркала без перекодирования; идентичность оригиналу и авторство не проверены.'}
except Exception as e:print('micro image unavailable:',str(e)[:100])
for c in cats:(P/'data'/f'{c}.json').write_text(json.dumps(D[c],ensure_ascii=False,indent=2))
print('verified cards 4')

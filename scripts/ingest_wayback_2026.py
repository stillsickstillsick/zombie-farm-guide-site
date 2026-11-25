"""Verified Wayback captures of existing sources; archives are not independent sources."""
from pathlib import Path
import json,requests,hashlib
from PIL import Image
from io import BytesIO
P=Path(__file__).resolve().parents[1];D=P/'data'
def load(f):return json.loads((D/f).read_text())
def save(f,v):(D/f).write_text(json.dumps(v,ensure_ascii=False,indent=2))
def add(f,name,slug,orig,snap,date,fields):
 data=load(f);e=next((x for x in data if x['name']==name),None)
 if not e:
  e={'slug':slug,'name':name,'category':f[:-5],'type':'Материал','purchase':'нет данных','sale':'нет данных','obtain':'нет данных','use':'нет данных','features':'нет данных','versions':'браузерная версия; платформа не уточнена','sources':[],'image':None,'links':[],'event':'нет данных','original_category':'Материалы'};data.append(e)
 rid='wayback-zf3dn-'+slug;e.setdefault('prior_records',[]);e['prior_records']=[r for r in e['prior_records'] if r.get('original_id')!=rid]+[{'original_id':rid,'original_category':'Архив страницы zf.3dn.ru','version':'браузерная игра; платформа страницы не указана','date':date,'fields':fields,'confidence':'Содержание подтверждено по снимку Wayback. Архив — копия zf.3dn.ru, не независимый источник. Имена файлов значков не доказывают название предмета.'}]
 if not any(x.get('url')==snap for x in e['sources']):e['sources'].append({'url':snap,'label':'Web Archive: снимок страницы '+orig})
 save(f,data)
base='https://web.archive.org/web/'
add('materials.json','Невод','nevod','zf.3dn.ru',base+'20180617040335/http://zf.3dn.ru/publ/materialy/nevod/7-1-0-488','04.06.2014 публикация; снимок 17.06.2018',{'Получение':'По статье: сокровища на Тропических островах или награда заданий. Нельзя купить.','Продажа':'1000 монет.'})
add('materials.json','Еловая ветка','elovaya-vetka','zf.3dn.ru',base+'20170420033530/http://zf.3dn.ru/publ/materialy/elovaja_vetka/7-1-0-265','13.07.2012 публикация; снимок 20.04.2017',{'Получение':'Можно нарубить из зимних елей.','Применение':'Строительство праздничной ёлки. Другие четыре объекта обозначены изображениями без подписей.'})
add('buildings.json','Пирамида','piramida','zf.3dn.ru',base+'20171030231459/http://zf.3dn.ru/publ/postrojki/piramida/1-1-0-68','05.05.2012 публикация; снимок 30.10.2017',{'Стоимость и опыт':'6 уровень, 15 000 монет; 495 опыта (150+75+120+150).','Стадии':'1: 30 камней + 20 брёвен + 5 гипномака; 2: 100 камней + 10 досок + 10 труб; 3: 3 скотча + 10 цемента + 15 острой росянки.','Рецепты':'1 хеллия + 1000 монет = 1 жёлтая краска; 1 проволока + 1 шестерня = 1 гвозди; 1 камень + 1000 монет = 1 блоки; 5 камней + 10 зелёной краски = 1 мрамор.'})
add('buildings.json','Купидон','kupidon','zf.3dn.ru',base+'20180212012807/http://zf.3dn.ru/publ/postrojki/kupidon/1-1-0-38','05.05.2012 публикация; снимок 12.02.2018',{'Доступ':'С 1 уровня.','Стадии, имена файлов пиктограмм':'1: 30 Bloki + 15 Belaya_kraska + 15 Provoloka; 2: 50 mir + 20 Kaplya_vody + 5 List_zolota. Расшифровка пиктограмм требует проверки.','Функция':'Рулетка: любовь, мир, золотое кольцо.'})
add('collections.json','Домашняя коллекция','domashnyaya-kollektsiya','zf.3dn.ru',base+'20171124125218/http://zf.3dn.ru/publ/kollekcii/domashnjaja_kollekcija/2-1-0-117','06.05.2012 публикация; снимок 24.11.2017',{'Где копать':'Клоун, Медвезомби, Средняя зимняя ёлка, Зомбоящик, Медвежонок, Шалаш, Идол раз, Бригада Элвиса, Горгулья два, Зомби-рок, Университет, Замок, Рука зомби, Марафонец, Горгулья раз, Идол деревянный, Маленькая зимняя ёлка, Медвед, Ожившая рука, Идол два.','Добывает':'Кладоискатель.','Награда':'5000 и 300; единицы указаны только изображениями, не расшифрованы.'})
# Verified German-localized guide kept separate, with original in-game screenshots.
u='http://www.friedela.de/Aufgaben/Aliens.php';snapshot=base+'20130407103220/'+u
locations=load('locations.json');slug='ostrov-nlo-world-of-zombies-de';e=next((x for x in locations if x['slug']==slug),None)
if not e:
 e={'slug':slug,'name':'Остров НЛО — немецкая версия','category':'locations','type':'Острова зарубежной браузерной версии','purchase':'нет данных','sale':'нет данных','obtain':'нет данных','use':'нет данных','features':'нет данных','versions':'World of Zombies, немецкая локализация; снимок 2013','sources':[{'url':snapshot,'label':'Friedela.de, архив 07.04.2013: Aliens auf der Insel'}],'image':None,'links':[],'event':'нет данных','original_category':'Зарубежные локации'};locations.append(e)
rid='friedela-ufo-2013';e.setdefault('prior_records',[]);e['prior_records']=[r for r in e['prior_records'] if r.get('original_id')!=rid]+[{'original_id':rid,'original_category':'World of Zombies: острова','version':'немецкая браузерная локализация; точная социальная сеть не установлена','date':'снимок 07.04.2013','fields':{'Оригинальное имя':'UFO-Insel. Соответствие русскому Острову НЛО предположительное: детали и версии необходимо сверить.','Переход':'В руководстве путешествие на остров описано как бесплатное через глобус после постройки пристани.','Задания':'Страница содержит скриншоты цепочки Aliens auf der Insel. В подсказке к Warten: изготовить 100 лопат, ждать 12 часов на острове НЛО; условия остальных заданий заключены в изображениях и не расшифрованы.','Дальнейший путь':'В руководстве показаны постройка летающей тарелки и остров Мечты (Insel der Träume).'},'confidence':'Архивная копия фанатского сайта; применимость к русским версиям не подтверждена.'}]
imgurl='http://www.friedela.de/images/Inseln/Ufo-Insel.jpg';archive=base+'20130407103220id_/'+imgurl
try:
 r=requests.get(archive,timeout=20);r.raise_for_status();im=Image.open(BytesIO(r.content));im.verify();h=hashlib.sha256(r.content).hexdigest()[:12];fn='img/archive/friedela-ufo-'+h+'.jpg';(P/fn).write_bytes(r.content);e['image']={'path':fn,'retrieved_from':archive,'attribution':imgurl,'source_page':snapshot,'note':'Оригинальные байты из Web Archive; снимок немецкой локализации, автор иллюстрации не установлен.'}
 print('island screenshot',len(r.content))
except Exception as exc:print('screenshot unavailable',str(exc)[:120])
save('locations.json',locations)
s=load('sources.json')
for x in s:
 if x['number']==41:x['summary']+=' Проверены снимки Wayback отдельных страниц Невода, Еловой ветки, Пирамиды, Купидона и Домашней коллекции; архив — копия этого же источника. Снимок задания Механизм содержит текст задания только на картинке.'
 if x['number']==42:x['summary']+=' Действующий сайт вернул ошибку; в Wayback найдены страницы немецкой браузерной локализации, прочитаны Aliens и Chemieunterricht, сохранён скриншот UFO-Insel. Снимки и список других обнаруженных страниц доступны через каталог CDX.'
 if x['number']==3:x['summary']+=' Дополнительно завершён обход связей: всего 84 проверенные статьи материалов, 29 не подтверждены или недоступны, очередь пуста.'
 if x['number']==1:x['summary']+=' Найден снимок статьи об игре от 23.06.2024: https://web.archive.org/web/20240623165652/https://zombipedia.fandom.com/ru/wiki/Зомби_Ферма (архив исходной вики).'
 if 'zombi.at.ua' in x.get('url','') and x.get('number')==4:x['summary']+=' Архив главной zombia.ru от 25.09.2011 указывает на перенос домена и ссылки zombi.at.ua: https://web.archive.org/web/20110925102047/http://zombia.ru/ . Не считать домены независимыми источниками.'
save('sources.json',s)

import json,requests,concurrent.futures,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1];S=P/'data';M=json.loads((S/'plants.json').read_text());C=json.loads((S/'collections.json').read_text());E=json.loads((S/'eggs-trophies.json').read_text());Z=json.loads((S/'zombies.json').read_text()); G=json.loads((S/'economy.json').read_text());src='https://zombiesforever.ucoz.ru/index/rastenija/0-11';col='https://zombiesforever.ucoz.ru/index/kollekcii/0-8'
def norm(s):return s.casefold().replace('ё','е').replace('-',' ').replace(' ','')
def add(x,url,rid,fields,version='ВКонтакте, ZombieS Forever',date='дата редакции не установлена'):
 x.setdefault('prior_records',[])
 if any(r['original_id']==rid for r in x['prior_records']):return False
 x['prior_records'].append({'original_id':rid,'original_category':x.get('original_category',x.get('type','нет данных')),'version':version,'date':date,'fields':fields,'confidence':'Историческая фанатская страница; независимость от других источников не установлена. Возможны различия версий и дат.'});x.setdefault('sources',[])
 if not any(y['url']==url for y in x['sources']):x['sources'].append({'url':url,'label':'Прочитана статья или строка таблицы; требуется сверка'})
 return True
# Text is transcribed from the plants table; currency is not specified in the table.
plants=[('Маракас','1020','16 часов','4','1120'),('Красный дракон','830','8 часов','3','900'),('Спиральки','240','24 часа','5','295'),('Светляки','900','32 часа','2','1246'),('Жёлтые тюльпаны','2500','24 часа','6','2650'),('Клевер','10','1 час','0','22'),('Рожь','40','12 часов','2','115'),('Баклажан','35','8 часов','1','106'),('Кукуруза','80','4 часа','1','132'),('Росянка дикая','95','24 часа','3','218'),('Бамбук','25','16 часов','2','91'),('Смородина','70','10 часов','2','154'),('Подсолнух','80','4 часа','1','132'),('Горох','65','8 часов','2','135'),('Перец чили','55','1 час','2','142'),('Костируза','100','32 часа','4','247'),('Лилии','85','24 часа','3','202'),('Кактусы','80','10 часов','2','167'),('Чеснок','90','8 часов','2','166'),('Алые розы','70','8 часов','2','141'),('Лук','65','6 часов','2','121'),('Помидор','90','8 часов','2','166'),('Тыква','80','16 часов','2','208'),('Волчья ягода','115','24 часа','1','336'),('Клубника','200','4 часа','2','245'),('Капуста','320','24 часа','3','496'),('Костяная нога','', '', '', '')]
updated=0;missing=[]
for name,price,growth,exp,sale in plants:
 if not price:continue
 e=next((x for x in M if norm(x['name'])==norm(name) and x.get('original_category')!='Рецепты'),None)
 if not e:missing.append(name);continue
 updated+=add(e,src,'zsf-plant-'+e['slug'],{'Цена (как указано в таблице)':price+'; валюта в строке явно не указана','Рост':growth,'Опыт':exp,'Продажа (как указано в таблице)':sale+'; валюта в строке явно не указана'})
# Explicit, individually transcribed collection rows; lists are partial where source rows are long.
collections=[('Военная коллекция','250 опыта и порох','Рука терминатора, танк.'),('Японская коллекция','500 опыта и лепестки роз','Плюшевая буква «Е».'),('Райская коллекция','Подушка и 50 000 монет','Рыбаки; хрусталь палочками; сундуки в подземельях.'),('Адская коллекция','15 палочек-выручалочек и 1 шоколад','Рыбаки; щупальца и хрусталь палочками; сундуки в подземельях.'),('Коллекция рыбака','300 опыта и язь','Приносят рыбаки.'),('Любовная коллекция','1 000 опыта и 50 лопат','В подземелье.'),('Школьная коллекция','50 000 монет и книги','В подземелье.'),('Байкерская коллекция','100 опыта и волчья ягода','Сундуки, грядки, глаз-алмаз, особняк, нефтяная вышка, бассейн, цветик и др.'),('Коллекция знаков','100 опыта и кактусы','Сундуки, грядки, бригада, кладоискатель, деревья и др.'),('Ручная коллекция','100 опыта и мухоморы','Сундуки, грядки, бассейн, рука терминатора, часовня и др.; фонтан в источнике отмечен вопросом.'),('Обувная коллекция','100 опыта и перец чили','Сундуки, грядки, чучело Санты, мост и др.'),('Строительная коллекция','Доска и 200 опыта','Маяк, башня, айти-могила.'),('Столовая коллекция','Чесночная лилия и 250 опыта','Башня, пара камнетёсов, пара дровосеков.'),('Редкая коллекция','10 камней, 10 брёвен и 150 опыта','Склеп, Волшебный кролик, камнетёсы, дровосеки, пристани и др.'),('Автомобильная коллекция','Шестерня и 8 000 монет','Глаз-алмаз, нефтяная вышка, особняк, флаги, мостовая, песок и др.'),('Туристическая коллекция','Росянка дикая и 250 опыта','Университет, Волшебный кролик, Зомбоящик, столб раз, идолы, цветочный декор.'),('Домашняя коллекция','5 000 монет и 300 опыта','Замок, университет, Зомбоящик, бригада Элвиса и др.'),('Коллекция игрушек','Пружина и 400 опыта','Замок, бригада Элвиса, клоун, медвежонок и др.'),('Ёлочная коллекция','Лента для скотча и 5 000 монет','Ёлка, снеговик, Пирамида Майя, бригада, часовня, рука терминатора.'),('Коллекция Деда Мороза','500 опыта и вода','Бригада, дерево и филин.'),('Коллекция Анти-зомби','300 опыта и огонь','Пирамида, вождь, валентинка, особняк, Японский храм и др.')]
cupdated=0
for name,reward,where in collections:
 e=next((x for x in C if norm(x['name'])==norm(name)),None)
 if e:cupdated+=add(e,col,'zsf-collection-'+e['slug'],{'Награда по ZombieS Forever':reward,'Места получения: выборка из источника':where})
# 2 individually inspected ZF.3DN pages, rather than extrapolating from its 562-entry catalogue.
x=next((v for v in M if norm(v['name'])==norm('Глазное яблоко')),None)
if not x:
 x={'slug':'glaznoe-yabloko','name':'Глазное яблоко','category':'plants','type':'Растения','purchase':'нет данных','sale':'нет данных','obtain':'нет данных','use':'нет данных','features':'нет данных','versions':'браузерная версия; источник 05.10.2014','sources':[],'image':None,'links':[],'event':'нет данных','original_category':'Растения'};M.append(x)
add(x,'https://zf.3dn.ru/publ/rastenija/glaznoe_jabloko_plody_derevo_zombie_farm/3-1-0-664','zf3dn-664',{'Уровень игрока':'28','Цена семян':'42 500 монет','Цена продажи':'3 953 монеты','Опыт за сбор грядки':'5','Время созревания':'24 часа'},'браузерная версия, ZF.3dn','05.10.2014; дата редакции неизвестна')
t={'slug':'neonovyy-shchit','name':'Неоновый щит','category':'eggs-trophies','type':'Трофей','purchase':'нет данных','sale':'нет данных','obtain':'нет данных','use':'нет данных','features':'нет данных','versions':'браузерная версия; публикация 04.10.2014','sources':[],'image':None,'links':[],'event':'нет данных','original_category':'Трофеи'}
if not any(y['slug']==t['slug'] for y in E):E.append(t)
else:t=next(y for y in E if y['slug']==t['slug'])
add(t,'https://zf.3dn.ru/publ/trofei/neonovyj_shhit_trofey_v_zombi_ferme/16-1-0-659','zf3dn-659',{'Получение':'Оставить друзьям всего 3 600 пряников под новогодними ёлками.','Покупка':'Нельзя купить.'},'браузерная версия, ZF.3dn','04.10.2014; дата редакции неизвестна')
# Historical FAQ: separate clearly dated-unknown entries, not universal rules for every update.
faq='https://zombaks.ucoz.ru/faq';faq_items=[('fakely-v-sekretnykh-kladakh','Факелы в секретных кладах','Факелы можно найти в секретных кладах на ферме друзей.'),('limit-podarkov','Лимит подарков','По FAQ, лимит обновляется в 00:00 по московскому времени; коллекции не занимают лимит. Ангар увеличивает суточный лимит на 5 000 монет. Актуальность и версия требуют сверки.'),('dopolnitelnye-mozgi','Дополнительные мозги','По FAQ, мозги можно арендовать за зомбаксы; дополнительные мозги упомянуты для построек Останкино и Японский храм. Авторежим для поваров на момент написания отсутствовал.'),('zombaksy-i-vavilon','Зомбаксы и Вавилон','По FAQ, зомбаксы можно производить в Вавилоне; также получать за уровни, задания и голоса ВКонтакте.')]
for slug,name,description in faq_items:
 target=Z if slug=='dopolnitelnye-mozgi' else G
 e=next((z for z in target if z['slug']==slug),None)
 if not e:e={'slug':slug,'name':name,'category':'zombies' if target is Z else 'economy','type':'Игровая механика','purchase':'нет данных','sale':'нет данных','obtain':'нет данных','use':'нет данных','features':'нет данных','versions':'ВКонтакте; дата редакции неизвестна','sources':[],'image':None,'links':[],'event':'нет данных','original_category':'Механика'};target.append(e)
 add(e,faq,'zombaks-faq-'+slug,{'Сведения из FAQ':description},'ВКонтакте, Zombaks FAQ')
# Download original files only, if available; no lossy thumbnail conversion.
imgs=[(x,'https://zf.3dn.ru/infa/urozai/glaznoe-jabloko-urozhaj.png'),(t,'https://zf.3dn.ru/infa/trofei/neonovyj_shhit_trof.png')]
plantimages={'Маракас':'marakasy.gif','Красный дракон':'krasnyj_drakon.gif','Спиральки':'spiralki.gif','Светляки':'svetljaki.gif'}
for name,file in plantimages.items():
 e=next((x for x in M if norm(x['name'])==norm(name)),None)
 if e and not e.get('image'):imgs.append((e,'https://zombiesforever.ucoz.ru/Rostenija/'+file))
hashes={hashlib.sha256(f.read_bytes()).hexdigest():f for f in (P/'img').rglob('*') if f.is_file()}
def dl(item):
 try:
  r=requests.get(item[1],timeout=6);r.raise_for_status();b=r.content;ext='png' if b.startswith(b'\x89PNG\r\n\x1a\n') else 'gif' if b[:6] in (b'GIF87a',b'GIF89a') else 'jpg' if b[:3]==b'\xff\xd8\xff' else None;return item,b,ext
 except Exception:return item,None,None
imcount=0
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 for (e,url),b,ext in pool.map(dl,imgs):
  if not ext:continue
  h=hashlib.sha256(b).hexdigest()
  if h not in hashes:
   f=P/'img/archive'/f'{e["slug"]}-{h[:12]}.{ext}';f.write_bytes(b);hashes[h]=f
  e['image']={'path':str(hashes[h].relative_to(P)),'retrieved_from':url,'attribution':url,'note':'Исходный файл со страницы; авторство игрового изображения не установлено.'};imcount+=1
for c,obj in [('plants',M),('collections',C),('eggs-trophies',E),('zombies',Z),('economy',G)]:(S/f'{c}.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2))
sources=json.loads((S/'sources.json').read_text())
for x in sources:
 if x['number']==41:x['summary']='Проверены 57 страниц каталога, обнаружены 562 уникальные ссылки, но прочитаны и перенесены только отдельные страницы: Глазное яблоко и Неоновый щит. Пакетное чтение статей прервалось по таймауту; каталог сохранён в data/zf3dn-catalog.json. Содержимое прочих статей не проверено.'
 if x['number']==15:x['summary']='Прочитаны таблицы растений и коллекций ВКонтакте; перенесены выбранные строки растений и коллекций. Полный охват не утверждается; независимость от других справочников не установлена.'
 if x['number']==57:x['summary']='Прочитана страница FAQ; отдельные исторические ответы о факелах, лимите, мозгах и Вавилоне перенесены с оговоркой версии.'
(S/'sources.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2))
print('plant rows applied',updated,'plant names missing',missing,'collection rows applied',cupdated,'new original images',imcount,'new zf article cards',2,'faq entries',4)

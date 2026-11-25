#!/usr/bin/env python3
"""Preserve two historical plant lists separately; explicit mappings, numeric/icon provenance."""
import requests,bs4,json,re
from pathlib import Path
P=Path(__file__).resolve().parents[1];path=P/'data/plants.json';data=json.loads(path.read_text());by={x['slug']:x for x in data}
u1='https://niebalbillbur.narod.ru/semena.html';u2='https://zombiesforever.ucoz.ru/index/rastenija/0-11'
map1={'klever.png':'klever','chernika.png':'chernika','tikvahell.png':'tykvakhell','mak.png':'mak','gipnosolnuh.png':'gipnosolnukh','rog.png':'ro','baklagan.png':'bakla-an','kukuruza.png':'kukuruza','rosyanka_dikaya.png':'rosyanka-dikaya','bambuk.png':'bambuk','smorodina.png':'smorodina','podsolnuh.png':'podsolnukh','goroh.png':'gorokh','perec_chili.png':'perets-chili','kostiruza.png':'kostiruza','liliya.png':'lilii','kaktus.png':'kaktusy','chesnok.png':'chesnok','alye_rozi.png':'alye-rozy','muhomor.png':'mukhomor','luk.png':'luk','pomidory.png':'pomidor','glaznoy_goroh.png':'glaznoy-gorokh','tykva.png':'tykva','volchya_yagoda.png':'volchya-yagoda','son_trava.png':'son-trava'}
def add(slug,url,rid,fields,confidence,label):
 x=by[slug]
 if not any(s['url']==url for s in x['sources']):x['sources'].append({'url':url,'label':label})
 rec={'original_id':rid,'original_category':'Растения','version':'браузерная игра; платформа не указана' if url==u1 else 'ВКонтакте, исторический фанатский справочник','date':'дата редакции не установлена','fields':fields,'confidence':confidence}
 x.setdefault('prior_records',[]);x['prior_records']=[r for r in x['prior_records'] if r.get('original_id')!=rid]+[rec]
r=requests.get(u1,timeout=20);r.raise_for_status();s=bs4.BeautifulSoup(r.content,'html.parser');n=0
for tr in s.find_all('tr'):
 td=tr.find_all('td',recursive=False)
 if len(td)!=10:continue
 im=td[1].find('img');filename=im.get('src','').split('/')[-1] if im else ''
 if filename not in map1:continue
 slug=map1[filename];vals=[td[i].get_text(' ',strip=True) for i in range(3,9)];level=td[0].find('img').get('src','');refs=[a.get('href','') for a in td[9].find_all('a') if a.get('href')]
 fields={'Пиктограмма первого столбца':level+' (подпись не прочитана; возможно, уровень)','Число рядом со значком времени':vals[0]+' (единица измерения в таблице явно не подписана)','Опыт':vals[1],'Цена у значка монет':vals[2],'Продажа одного урожая':vals[3]+' монет (подпись значка источника)','Два расчётных столбца со значками':vals[4]+'; '+vals[5]+' (подписи и метод расчёта не установлены)','Ссылки на применение в таблице':'; '.join(refs) or 'нет ссылок'}
 if slug=='ro':fields['Расхождение']='В ZombieS Forever продажа ржи — 115; здесь 116 монет. Не установлено, ошибка это или различие редакций.'
 if slug=='perets-chili':fields['Расхождение']='В ZombieS Forever время роста перца указано как 1 час, здесь у значка времени — 12; причина различия не установлена.'
 if slug=='kostiruza':fields['Расхождение']='В ZombieS Forever опыт — 4, в таблице здесь — 3; причина различия не установлена.'
 add(slug,u1,'narod-seeds-'+slug,fields,'Историческая таблица с графическими заголовками; часть пиктограмм и единиц не расшифрована, дата редакции и независимость от других сайтов неизвестны.','niebalbillbur: таблица семян');n+=1
r=requests.get(u2,timeout=20);r.raise_for_status();t=bs4.BeautifulSoup(r.content,'html.parser').get_text('\n',strip=True);t=t[t.index('Зобильон\nМаракас'):];t=t[:t.index('\nВверх\n')]
names=[('Маракас','marakas'),('Красный Дракон','krasnyy-drakon'),('Спиральки','spiralki'),('Светляки','svetlyaki'),('Желтые Тюльпаны','yoltye-tyulpany'),('Клевер','klever'),('Тыквахелл','tykvakhell'),('Черника','chernika'),('Мак','mak'),('Гипносолнух','gipnosolnukh'),('Рожь','ro'),('Баклажан','bakla-an'),('Кукуруза','kukuruza'),('Росянка дикая','rosyanka-dikaya'),('Бамбук','bambuk'),('Смородина','smorodina'),('Подсолнух','podsolnukh'),('Горох','gorokh'),('Перец Чили','perets-chili'),('Костируза','kostiruza'),('Лилии','lilii'),('Кактусы','kaktusy'),('Чеснок','chesnok'),('Алые Розы','alye-rozy'),('Мухамор','mukhomor'),('Лук','luk'),('Помидор','pomidor'),('Глазной-горох','glaznoy-gorokh'),('Тыква','tykva'),('Волчья ягода','volchya-yagoda'),('Сон трава','son-trava'),('Клубника','klubnika'),('Черные руки','chyornye-ruki'),('Капуста','kapusta'),('Костяная нога','kostyanaya-noga'),('Ананас','ananas'),('Белые руки','belye-ruki'),('Картошка','kartoshka'),('Виноград','vinograd'),('Мозговица','mozgovitsa'),('Тростник','trostnik')]
positions=[];cursor=0
for name,slug in names:
 m=re.search(r'(?m)^'+re.escape(name)+r'\s*$',t[cursor:]);assert m,(name,cursor);pos=cursor+m.start();positions.append(pos);cursor=pos+len(name)
for j,(name,slug) in enumerate(names):
 piece=t[positions[j]:(positions[j+1] if j+1<len(names) else len(t))].strip();assert 'Цена:' in piece and 'Продажа:' in piece,(name,piece)
 fields={'Текст записи':piece}
 if slug in ('ro','perets-chili','kostiruza'):fields['Расхождение']='На таблице niebalbillbur.narod.ru встречается другое значение; см. запись этого источника, причина не установлена.'
 add(slug,u2,'forever-plant-'+slug,fields,'Историческая фанатская таблица: цены и время могут зависеть от версии. Заявления об отсутствии применения относятся только к моменту составления; независимость источников не установлена.','ZombieS Forever: растения')
path.write_text(json.dumps(data,ensure_ascii=False,indent=2));print('Narod:',n,'ZombieS Forever:',len(names))

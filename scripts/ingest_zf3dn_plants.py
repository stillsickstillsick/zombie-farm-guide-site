#!/usr/bin/env python3
import json,re,requests,bs4,concurrent.futures
from pathlib import Path
from urllib.parse import urljoin
P=Path(__file__).resolve().parents[1];p=P/'data/plants.json';data=json.loads(p.read_text());by={x['slug']:x for x in data}
exceptions={'ЧЁРНАЯ РУКА':'chyornye-ruki','ПОМИДОРЫ':'pomidor','МУХОМОРЫ':'mukhomor','МОЗГОВНИЦА':'mozgovitsa','МАРАКАСЫ':'marakas','КРАСНЫЕ ДРАКОНЫ':'krasnyy-drakon','КАКТУС':'kaktusy','ЗОМБИЛЬОНЫ':'zombilon','БЕЛАЯ РУКА':'belye-ruki'}
def norm(s):return s.casefold().replace('ё','е').strip()
names={norm(x['name']):x['slug'] for x in data};entries=[]
for n in range(1,7):
 u='https://zf.3dn.ru/publ/rastenija/3'+('-'+str(n) if n>1 else '');r=requests.get(u,timeout=20);r.raise_for_status();s=bs4.BeautifulSoup(r.content,'html.parser');rows=[(h.get_text(' ',strip=True),urljoin(u,h['href'])) for h in s.select('h1 a')];print('catalog',n,len(rows));entries.extend(rows)
assert len(entries)==53,len(entries)
def fetch(row):
 name,u=row
 try:
  r=requests.get(u,timeout=20);r.raise_for_status();s=bs4.BeautifulSoup(r.content,'html.parser');d=s.select_one('td.eText');txt=d.get_text('\n',strip=True) if d else '';date=re.search(r'\(\d{2}\.\d{2}\.\d{4}\)',s.get_text(' ',strip=True));return name,u,txt,date.group(0)[1:-1] if date else 'дата публикации не найдена'
 except Exception as e:return name,u,'','ошибка '+str(e)[:80]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:out=list(ex.map(fetch,entries))
count=0
for name,u,txt,date in out:
 slug=exceptions.get(name,names.get(norm(name)))
 if not slug or not txt:print('skipped:',name,date);continue
 x=by[slug];rid='zf3dn-plant-'+slug
 rec={'original_id':rid,'original_category':'Растения','version':'браузерная игра; платформа не указана','date':date+' — дата публикации; дата редакции неизвестна','fields':{'Текст и числовые данные страницы':txt},'confidence':'Сведения одного исторического фанатского сайта, не текущие цены или универсальные правила. Единицы и подписи-иконки могли не попасть в текст; сопоставление имён в единственном и множественном числе предварительное. Страница связана ссылками с zombi-ferma.ru, независимость не установлена.'}
 if not any(s['url']==u for s in x['sources']):x['sources'].append({'url':u,'label':'ZF.3dn: историческая карточка растения'})
 x.setdefault('prior_records',[]);x['prior_records']=[r for r in x['prior_records'] if r.get('original_id')!=rid]+[rec];count+=1
p.write_text(json.dumps(data,ensure_ascii=False,indent=2));print('matched:',count,'of',len(entries))

#!/usr/bin/env python3
"""31 daily quests from the indexed June 2015 series; original files untranscoded."""
import sys,json,re,hashlib,time,requests,pathlib
from io import BytesIO
from PIL import Image
from bs4 import BeautifulSoup
P=pathlib.Path(__file__).resolve().parents[1]; cache=pathlib.Path(sys.argv[1]);dpath=P/'data/quests.json';quests=json.loads(dpath.read_text());by_slug={x['slug']:x for x in quests};log={x['id']:x for x in map(json.loads,(cache/'download-log.jsonl').read_text().splitlines()) if x.get('status')=='downloaded_unreviewed'}; index=BeautifulSoup((cache/'pages/3680.html').read_bytes(),'html.parser'); rows=[]
for a in index.select('a[href]'):
 m=re.search(r'/2015-\d\d-\d\d-(\d+)$',a['href']);
 if m and (3681<=int(m[1])<=3712) and a.img:
  i=int(m[1]); src=a.img.get('src','');
  if not re.search(r'/2015/13/\d+\.png$',src):continue
  if i not in {r[0] for r in rows}:rows.append((i,src))
assert len(rows)==31,(len(rows),rows)
hashes={}
for p in (P/'img').rglob('*'):
 if p.is_file():hashes.setdefault(hashlib.sha256(p.read_bytes()).hexdigest(),str(p.relative_to(P)))
session=requests.Session();session.headers['User-Agent']='ZombieFarmGuideResearch/1.0 (respectful archival research)';made=[]
for order,(i,img) in enumerate(rows,1):
 slug=f'mylnaya-opera-2015-{i}';entry=log.get(i);assert entry and (cache/'pages'/f'{i}.html').exists(),i
 s=BeautifulSoup((cache/'pages'/f'{i}.html').read_bytes(),'html.parser');d=s.select_one('div.kvest_ind');assert d and d.find('ol'),i
 h=d.find('h1');name=h.get_text(' ',strip=True).removeprefix('Прохождение квеста ').strip();goals=[x.get_text(' ',strip=True) for x in d.find('ol').find_all('li',recursive=False)];reward=d.find_next_sibling('div',class_='kvest_ind_nagr');assert reward and goals,(i,name)
 p=d.select_one('p.kvest_ind_p');intro=p.get_text(' ',strip=True).removeprefix('Задание:').strip() if p else ''
 retrieved=img.replace('http://zombicity.info/','https://zombie-island.moy.su/').replace('https://zombicity.info/','https://zombie-island.moy.su/')
 if slug not in by_slug:
  response=session.get(retrieved,timeout=25);response.raise_for_status();content=response.content;im=Image.open(BytesIO(content));im.verify();assert im.format=='PNG';sha=hashlib.sha256(content).hexdigest();path=hashes.get(sha)
  if not path:path=f'img/archive/soap-opera-2015-{i}-{sha[:12]}.png';(P/path).write_bytes(content);hashes[sha]=path
  x={'slug':slug,'name':name+' — Мыльная опера 2015','category':'quests','type':'Ежедневное задание','purchase':'нет данных','sale':'нет данных','obtain':'Последовательная серия «Мыльная опера» по индексу источника.','use':'нет данных','features':'нет данных','versions':'браузерная игра; конкретная платформа и редакция требуют уточнения','sources':[{'url':entry['final_url'],'label':'Zombie-island: отдельное задание'},{'url':log[3680]['final_url'],'label':'Zombie-island: список серии'}],'image':{'path':path,'retrieved_from':retrieved,'attribution':img,'source_page':log[3680]['final_url'],'note':'Миниатюра серии по индексу; файл загружен без перекодирования с альтернативного хоста. Побайтовое совпадение с исходным хостом и авторство не проверены.'},'links':[],'event':'Мыльная опера — ежедневные задания 2015','prior_records':[{'original_id':f'soap-opera-2015-{i}','original_category':'Ежедневный квест','version':'браузерная игра, сеть не уточнена','date':'июнь 2015 — дата статьи, не дата последней правки','fields':{'Номер':f'{order} из 31 в первой серии по индексу.','Сюжет':intro,'Цели':' | '.join(f'{n}. {g}' for n,g in enumerate(goals,1)),'Награда':reward.get_text(' ',strip=True).replace('Награда за прохождение задания:','').strip(),'Срок':'Индекс серии утверждает, что на каждое задание отводится 24 часа; точный момент начала отсчёта не установлен. Отсутствие цены пропуска в статье не доказывает невозможность пропуска.'},'confidence':'Фанатский источник; содержание и условия могут различаться по версии и времени.'}]};quests.append(x);by_slug[slug]=x;time.sleep(.4)
 made.append(slug);print(order,i,name,flush=True)
for i,slug in enumerate(made):
 for j,rel in [(i-1,'предыдущее задание'),(i+1,'следующее задание')]:
  if 0<=j<len(made):
   target=by_slug[made[j]];x=by_slug[slug]
   if not any(z.get('slug')==target['slug'] and z.get('category')=='quests' for z in x['links']):x['links'].append({'category':'quests','slug':target['slug'],'name':target['name'],'relation':rel})
dpath.write_text(json.dumps(quests,ensure_ascii=False,indent=2)+'\n');print('imported',len(made))

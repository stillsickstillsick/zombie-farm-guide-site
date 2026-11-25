#!/usr/bin/env python3
"""Import source-indexed 2015 story chains with images preserved byte-for-byte."""
import sys,json,re,time,hashlib,pathlib,requests
from io import BytesIO
from PIL import Image
from bs4 import BeautifulSoup
P=pathlib.Path(__file__).resolve().parents[1];cache=pathlib.Path(sys.argv[1]);p=P/'data/quests.json';quests=json.loads(p.read_text());I={x['slug']:x for x in quests};logs={x['id']:x for x in map(json.loads,(cache/'download-log.jsonl').read_text().splitlines()) if x.get('status')=='downloaded_unreviewed'}
chains=[(3851,'kosmos-3-2015','Космос 3',17,'Постоянство серии по этому индексу не указано.'),(3885,'gribnoy-sezon-2015','Грибной сезон',6,'Индекс называет серию временной; конкретный срок не указан.'),(3892,'kosmos-4-2015','Космос 4',18,'Постоянство серии по этому индексу не указано.'),(3927,'kosmicheskiy-karnaval-2015','Космический карнавал',9,'Индекс называет серию временной к Хэллоуину 2015; точный срок не указан.'),(4012,'den-blagodareniya-2015','День Благодарения',7,'Индекс называет серию временной; точный срок не указан.'),(4041,'den-rozhdeniya-zombi-2015','День рождения зомби',7,'Индекс называет серию постоянной; различия версий требуют сверки.'),(4140,'rozhdestvo-2015','Рождество 2015–2016',5,'Индекс называет серию временной; точный срок не указан.')]
hashes={}
for z in (P/'img').rglob('*'):
 if z.is_file():hashes.setdefault(hashlib.sha256(z.read_bytes()).hexdigest(),str(z.relative_to(P)))
s=requests.Session();s.headers['User-Agent']='ZombieFarmGuideResearch/1.0 (respectful archival research)'; image_cache={};done=0
for index,prefix,series,expected,time_note in chains:
 root=BeautifulSoup((cache/'pages'/f'{index}.html').read_bytes(),'html.parser');rows=[]
 for a in root.select('a[href]'):
  m=re.search(r'/20\d\d-\d\d-\d\d-(\d+)$',a['href'])
  if not m or not a.img:continue
  i=int(m[1]);img=a.img.get('src','')
  if index<i<=index+45 and i not in [k[0] for k in rows]:rows.append((i,img))
 assert len(rows)==expected,(index,len(rows));out=[]
 for order,(i,img) in enumerate(rows,1):
  assert i in logs and (cache/'pages'/f'{i}.html').exists(),i
  src=BeautifulSoup((cache/'pages'/f'{i}.html').read_bytes(),'html.parser');d=src.select_one('div.kvest_ind');assert d and d.find('ol'),i
  name=d.find('h1').get_text(' ',strip=True).removeprefix('Прохождение квеста ').strip();goals=[li.get_text(' ',strip=True) for li in d.find('ol').find_all('li',recursive=False)];reward=d.find_next_sibling('div',class_='kvest_ind_nagr');assert goals and reward,i
  intro=d.select_one('p.kvest_ind_p');intro=intro.get_text(' ',strip=True).removeprefix('Задание:').strip() if intro else ''
  slug=f'{prefix}-{i}';retrieved=('https://zombie-island.moy.su'+img if img.startswith('/') else img.replace('http://zombicity.info/','https://zombie-island.moy.su/').replace('https://zombicity.info/','https://zombie-island.moy.su/'));attribution=('https://zombie-island.moy.su'+img if img.startswith('/') else img)
  if slug not in I:
   if retrieved not in image_cache:
    r=s.get(retrieved,timeout=25);r.raise_for_status();content=r.content;im=Image.open(BytesIO(content));im.verify();ext={'PNG':'.png','JPEG':'.jpg','GIF':'.gif'}[im.format];sha=hashlib.sha256(content).hexdigest();path=hashes.get(sha)
    if not path:path=f'img/archive/story-2015-{i}-{sha[:12]}{ext}';(P/path).write_bytes(content);hashes[sha]=path
    image_cache[retrieved]=path;time.sleep(.4)
   x={'slug':slug,'name':name+' — '+series,'category':'quests','type':'Задание','purchase':'нет данных','sale':'нет данных','obtain':'Последовательность заданий по индексу источника.','use':'нет данных','features':'нет данных','versions':'браузерная игра; сеть и версия требуют сверки','sources':[{'url':logs[i]['final_url'],'label':'Zombie-island: отдельное задание'},{'url':logs[index]['final_url'],'label':'Zombie-island: индекс серии'}], 'image':{'path':image_cache[retrieved],'retrieved_from':retrieved,'attribution':attribution,'source_page':logs[index]['final_url'],'note':'Изображение из индекса серии, загружено без перекодирования; точное соответствие игровому экрану и авторство не установлены. Идентичность файлов разных хостов не проверена.'},'links':[],'event':series+' — 2015','prior_records':[{'original_id':f'cached-story-2015-{i}','original_category':'Задание','version':'браузерная игра; платформа не уточнена','date':'2015 — дата статьи; последующая правка не датирована','fields':{'Порядок':f'{order} из {expected} по индексу серии.','Сюжет':intro,'Цели':' | '.join(f'{j}. {g}' for j,g in enumerate(goals,1)),'Награда':reward.get_text(' ',strip=True).replace('Награда за прохождение задания:','').strip(),'Время':time_note+' Если цена пропуска не показана, нельзя заключать, что пропуск невозможен.'},'confidence':'Фанатский источник; текст статьи может содержать ошибки, поздние изменения и отличия между версиями.'}]};quests.append(x);I[slug]=x;done+=1
  out.append(slug)
 for order,slug in enumerate(out):
  for j,rel in ((order-1,'предыдущее задание'),(order+1,'следующее задание')):
   if 0<=j<len(out):
    target=I[out[j]];x=I[slug]
    if not any(z.get('category')=='quests' and z.get('slug')==target['slug'] for z in x['links']):x['links'].append({'category':'quests','slug':target['slug'],'name':target['name'],'relation':rel})
 print(series,'заданий',len(out),flush=True)
p.write_text(json.dumps(quests,ensure_ascii=False,indent=2)+'\n');print('Добавлено',done)

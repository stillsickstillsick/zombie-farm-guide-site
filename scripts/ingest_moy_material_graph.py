"""Crawl linked material articles from verified browser-game pages, with page checkpoints."""
import requests,bs4,json,re,hashlib,concurrent.futures
from pathlib import Path
from urllib.parse import urljoin,urlsplit
from collections import deque
P=Path(__file__).resolve().parents[1];F=P/'data/moy-material-graph-audit.json';seeds=['https://zombie-island.moy.su/blog/zombie_farm_shkola/2012-07-18-270','https://zombie-island.moy.su/blog/zombi_ferma_zerkalo/2012-07-17-30','https://zombie-island.moy.su/blog/zombi_ferma_mikroskhema/2012-07-18-57','https://zombie-island.moy.su/blog/zombi_ferma_metall/2012-07-17-55'];audit=json.loads(F.read_text()) if F.exists() else {'articles':[],'failed':[],'frontier':seeds};articles={x['url']:x for x in audit['articles']};failed={x['url'] for x in audit['failed']};seen=set(articles)|failed;queue=deque(audit.get('frontier') or seeds)
def parse(url):
 try:
  q=requests.get(url,timeout=8);q.raise_for_status();s=bs4.BeautifulSoup(q.content,'html.parser');body=s.select_one('.blog_body_mat');h=body.find('h1') if body else None
  if not h:return {'url':url,'error':'нет игрового блока и заголовка'}
  links=[]
  for a in body.find_all('a',href=True):
   u=urljoin(url,a['href']).split('#')[0].replace('http://zombicity.info','https://zombie-island.moy.su').replace('https://zombicity.info','https://zombie-island.moy.su')
   if re.match(r'https://zombie-island\.moy\.su/blog/(?:zombi_ferma_|belaja_kraska_)[^/]+/\d{4}-\d\d-\d\d-\d+$',u) and u not in links:links.append(u)
  if url in seeds and 'shkola/' in url:return {'url':url,'links':links,'seed_only':True}
  title=h.get_text(' ',strip=True);root=body.select_one('table.individualnye') or body.select_one('div.ind');header=(root.select_one('.kartinki_div p') or root.select_one('.kart_div_100 p')) if root else None
  if not root or not header or header.get_text(' ',strip=True).casefold()!='материал':return {'url':url,'error':'страница не подтверждена как материал','links':links}
  image=root.select_one('.kartinki_div img[src], .kart_div_100 img[src]');image_url=urljoin(url,image['src']) if image else None
  for t in root.select('script,style,ins'):t.decompose()
  for img in root.find_all('img'):
   if img.get('title') or img.get('alt'):img.replace_with(' [иллюстрация: '+(img.get('title') or img.get('alt'))+'] ')
   else:img.decompose()
  text=re.sub(r'\n{3,}','\n\n',root.get_text('\n',strip=True));return {'url':url,'name':title,'text':text,'image':image_url,'links':links}
 except Exception as e:return {'url':url,'error':str(e)[:150]}
# At most 70 additional URLs per run; failures are skipped and the discovered frontier persists.
fetched=0
while queue and fetched<70:
 batch=[]
 while queue and len(batch)<4 and fetched+len(batch)<70:
  u=queue.popleft()
  if u not in seen:seen.add(u);batch.append(u)
 if not batch:continue
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
  for r in ex.map(parse,batch):
   fetched+=1;queue.extend(r.get('links',[]))
   if r.get('error'):audit['failed'].append({'url':r['url'],'error':r['error']})
   elif r.get('seed_only'):audit.setdefault('seed_pages',[]).append(r)
   else:articles[r['url']]=r
 audit.update({'articles':list(articles.values()),'frontier':list(dict.fromkeys(u for u in queue if u not in seen)),'note':'Связанные статьи о материалах браузерной игры; 70 новых адресов за запуск, не полный обход источника. Картинки указывают на ЗомбиСити, независимость текстов не установлена.'});F.write_text(json.dumps(audit,ensure_ascii=False,indent=2))
Fdata=P/'data/materials.json';data=json.loads(Fdata.read_text());normalize=lambda t:re.sub(r'\s+',' ',t.casefold().replace('ё','е')).strip();by={normalize(e['name']):e for e in data};used={e['slug'] for e in data};tr=str.maketrans(dict(zip('абвгдеёзийклмнопрстуфхцчшщъыьэюя',['a','b','v','g','d','e','yo','z','i','y','k','l','m','n','o','p','r','s','t','u','f','kh','ts','ch','sh','shch','','y','','e','yu','ya'])));new=added=0;pending=[]
for x in articles.values():
 id=x['url'].split('-')[-1];name=x['name'];e=by.get(normalize(name))
 if not e:
  sp=re.sub(r'[^a-z0-9]+','-',name.lower().translate(tr)).strip('-') or 'material';sp=sp if sp not in used else sp+'-'+id;used.add(sp);e={'slug':sp,'name':name,'category':'materials','type':'Материал','purchase':'нет данных','sale':'нет данных','obtain':'нет данных','use':'нет данных','features':'нет данных','versions':'браузерная Зомби Ферма / Зомби Мания; платформа не уточнена','sources':[],'image':None,'links':[],'event':'нет данных','original_category':'Материалы'};data.append(e);by[normalize(name)]=e;new+=1
 rid='moy-graph-'+id;e.setdefault('prior_records',[])
 if not any(z.get('original_id')==rid for z in e['prior_records']):e['prior_records'].append({'original_id':rid,'original_category':'Материалы','version':'браузерная Зомби Ферма / Зомби Мания; платформа требует проверки','date':'дата URL не гарантирует дату редакции','fields':{'Основной блок страницы и подписи изображений':x['text']},'confidence':'Индивидуальная страница прочитана автоматически, подписи значков могут содержать ошибки; даты редакции и независимость от ЗомбиСити не установлены.'});added+=1
 if not any(z.get('url')==x['url'] for z in e['sources']):e['sources'].append({'url':x['url'],'label':'Zombie-island.moy.su: прочитана отдельная статья'})
 if not e.get('image') and x.get('image'):pending.append((e,x))
Fdata.write_text(json.dumps(data,ensure_ascii=False,indent=2));hmap={hashlib.sha256(p.read_bytes()).hexdigest():p for p in (P/'img').rglob('*') if p.is_file()}
def getimage(task):
 e,x=task;original=x['image'];url=original.replace('http://zombicity.info','https://zombie-island.moy.su')
 try:
  q=requests.get(url,timeout=6);q.raise_for_status();b=q.content;ext='png' if b.startswith(b'\x89PNG\r\n\x1a\n') else 'jpg' if b.startswith(b'\xff\xd8\xff') else 'gif' if b[:6] in (b'GIF89a',b'GIF87a') else None;return e,x,url,b,ext
 except:return e,x,url,None,None
ok=0
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
 for e,x,u,b,ext in ex.map(getimage,pending):
  if not ext:continue
  h=hashlib.sha256(b).hexdigest();f=hmap.get(h)
  if not f:f=P/'img/archive'/f'{e["slug"]}-{h[:12]}.{ext}';f.write_bytes(b);hmap[h]=f
  e['image']={'path':str(f.relative_to(P)),'retrieved_from':u,'attribution':x['image'],'source_page':x['url'],'note':'Без перекодирования; при замене домена идентичность оригиналу не проверена, авторство не установлено.'};ok+=1
Fdata.write_text(json.dumps(data,ensure_ascii=False,indent=2));print('new urls attempted',fetched,'verified material articles',len(articles),'failed total',len(audit['failed']),'new cards',new,'source facts added',added,'images',ok,'remaining frontier',len(audit['frontier']))

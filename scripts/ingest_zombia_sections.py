"""Ingest readable ZOMBIA catalogue cards with section-aware matching and listing provenance."""
import requests,bs4,concurrent.futures,json,re,hashlib,math
from pathlib import Path
from urllib.parse import urljoin
P=Path(__file__).resolve().parents[1];base='https://zombi.at.ua';spec=[('rastenija',20,6,'plants','Растение'),('kollekcii',22,6,'collections','Коллекция'),('paskhalnye_jajca',24,4,'eggs-trophies','Пасхальное яйцо'),('zombi',26,3,'zombies','Зомби'),('trofei',29,2,'eggs-trophies','Трофей')];sets={name:json.loads((P/'data'/f'{name}.json').read_text()) for *_,name,typ in spec};used={name:{e['slug'] for e in v} for name,v in sets.items()};tr=str.maketrans(dict(zip('абвгдеёзийклмнопрстуфхцчшщъыьэюя',['a','b','v','g','d','e','yo','z','i','y','k','l','m','n','o','p','r','s','t','u','f','kh','ts','ch','sh','shch','','y','','e','yu','ya'])))
def norm(t):return re.sub(r'[^а-яa-z0-9]+',' ',t.casefold().replace('ё','е')).strip()
def sslug(t):return re.sub(r'[^a-z0-9]+','-',t.lower().translate(tr)).strip('-') or 'item'
def collkey(t):
 t=re.sub(r'\bколлекц\w*\b',' ',norm(t));words=[w for w in t.split() if w];return ' '.join(sorted(words))
def find(name,cat,typ):
 aliases={'маракасы':'Маракас','красные драконы':'Красный дракон','помидоры':'Помидор','сон трава':'Сон-трава','сонтрава':'Сон-трава','черная рука':'Чёрные руки','белая рука':'Белые руки','мозговница':'Мозговица','кактус':'Кактусы','коллекция хеллоуин':'Коллекция Хэллоуина'}
 if cat in ('plants','collections') and norm(name) in aliases:name=aliases[norm(name)]
 pool=sets[cat];matches=[]
 for e in pool:
  if cat=='plants' and e.get('original_category')=='Рецепты':continue
  if cat=='eggs-trophies' and typ=='Трофей' and 'троф' not in (e.get('type','')+' '+e.get('original_category','')).lower():continue
  if cat=='eggs-trophies' and typ=='Пасхальное яйцо' and 'яйц' not in (e.get('type','')+' '+e.get('original_category','')).lower():continue
  if norm(name)==norm(e['name']):matches.append(e)
  elif cat=='collections' and collkey(name) and collkey(name)==collkey(e['name']):matches.append(e)
 return matches[0] if len(matches)==1 else None
def process(job):
 path,cid,i,cat,typ=job;url=f'{base}/board/menju/{path}/{cid}'+(f'-{i}' if i>1 else '')
 try:
  r=requests.get(url,timeout=8);r.raise_for_status();s=bs4.BeautifulSoup(r.content,'html.parser');out=[]
  for t in s.select('.eTitle'):
   a=t.find('a',href=True);m=re.search(fr'/{cid}-1-0-(\d+)',a['href']) if a else None
   if not m:continue
   name=a.get_text(' ',strip=True).replace('(Кликнуть, чтобы прокомментировать)','').strip();td=t.parent;im=td.find('img',src=True);img=urljoin(url,im['src']) if im else None;item_url=urljoin(url,a['href']);t.decompose()
   for x in td.select('script,style,ins'):x.decompose()
   raw=td.get_text('\n',strip=True);raw=re.sub(r'\n{3,}','\n\n',raw)
   out.append({'id':m.group(1),'name':name,'text':raw,'listing':url,'item_url':item_url,'img':img,'category':cat,'type':typ})
  return {'listing':url,'records':out,'error':None if out else 'Нет карточек'}
 except Exception as e:return {'listing':url,'records':[],'error':str(e)[:200]}
jobs=[(path,cid,i,cat,typ) for path,cid,total,cat,typ in spec for i in range(1,total+1)];results=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
 for r in ex.map(process,jobs):
  results.append(r);(P/'data/zombia-sections-audit.json').write_text(json.dumps({'note':'Проверены страницы списков, не все индивидуальные статьи; иллюстрации могут иметь ошибочные alt-тексты.','pages':results},ensure_ascii=False,indent=2))
new=merged=0;pending=[]
for r in results:
 for item in r['records']:
  cat=item['category'];typ=item['type'];name=item['name'];e=find(name,cat,typ)
  if not e:
   display=name+' (яйцо)' if typ=='Пасхальное яйцо' else name+' (трофей)' if typ=='Трофей' else name
   sp=sslug(display);sp=sp if sp not in used[cat] else sp+'-'+item['id'];used[cat].add(sp);e={'slug':sp,'name':display,'category':cat,'type':typ,'purchase':'нет данных','sale':'нет данных','obtain':'нет данных','use':'нет данных','features':'нет данных','versions':'браузерная версия; платформа и дата редакции не установлены','sources':[],'image':None,'links':[],'event':'нет данных','original_category':typ};sets[cat].append(e);new+=1
  else:merged+=1
  rid='zombia-section-'+item['id'];e.setdefault('prior_records',[])
  if not any(x.get('original_id')==rid for x in e['prior_records']):e['prior_records'].append({'original_id':rid,'original_category':typ,'version':'браузерная версия; платформа не указана','date':'дата редакции не установлена','fields':{'Текст карточки из каталога':item['text'] or 'Текст отсутствует; сведения могут быть на пиктограммах.'},'confidence':'Содержимое списка: изображения и колонки могут терять смысл при извлечении текста; отдельная страница и дата не проверены. Подписи alt иногда ошибочны.'})
  for u,label in [(item['listing'],'ZOMBIA: прочитана карточка в списке'),(item['item_url'],'Ссылка на отдельную страницу; отдельно не проверена')]:
   if not any(y.get('url')==u for y in e['sources']):e['sources'].append({'url':u,'label':label})
  if not e.get('image') and item['img'] and cat!='collections':pending.append((e,item))
for cat,vals in sets.items():(P/'data'/f'{cat}.json').write_text(json.dumps(vals,ensure_ascii=False,indent=2))
hashes={hashlib.sha256(x.read_bytes()).hexdigest():x for x in (P/'img').rglob('*') if x.is_file()}
def getpic(task):
 e,item=task;u=item['img'];u=u.replace('http://zombia.ru/','https://zombi.at.ua/').replace('https://zombia.ru/','https://zombi.at.ua/')
 try:
  q=requests.get(u,timeout=6);q.raise_for_status();b=q.content;ext='png' if b.startswith(b'\x89PNG\r\n\x1a\n') else 'jpg' if b.startswith(b'\xff\xd8\xff') else 'gif' if b[:6] in (b'GIF87a',b'GIF89a') else None;return e,item,u,b,ext
 except Exception:return e,item,u,None,None
ok=0
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
 for e,item,u,b,ext in ex.map(getpic,pending):
  if not ext:continue
  h=hashlib.sha256(b).hexdigest();f=hashes.get(h)
  if not f:f=P/'img/archive'/f'{e["slug"]}-{h[:12]}.{ext}';f.write_bytes(b);hashes[h]=f
  e['image']={'path':str(f.relative_to(P)),'retrieved_from':u,'attribution':item['img'],'source_page':item['listing'],'note':'Первая иллюстрация карточки каталога; подписи изображений источника могут содержать ошибки. Авторство и идентичность при замене домена не подтверждены.'};ok+=1
for cat,vals in sets.items():(P/'data'/f'{cat}.json').write_text(json.dumps(vals,ensure_ascii=False,indent=2))
print('list pages',len(results),'failed',sum(bool(r['error']) for r in results),'records',sum(len(r['records']) for r in results),'new',new,'matched',merged,'images',ok,'failed images',len(pending)-ok)

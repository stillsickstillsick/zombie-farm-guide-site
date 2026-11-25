"""Ingest historical building rows; preserve pictogram provenance and flag ambiguities."""
import json,re,requests,bs4,hashlib,concurrent.futures
from pathlib import Path
from urllib.parse import urljoin,unquote
P=Path(__file__).resolve().parents[1];F=P/'data/buildings.json';url='https://niebalbillbur.narod.ru/postrojki.html';r=requests.get(url,timeout=12);r.raise_for_status();s=bs4.BeautifulSoup(r.content,'html.parser');data=json.loads(F.read_text());norm=lambda x:re.sub(r'\s+',' ',x.casefold().replace('ё','е')).strip();by={norm(x['name']):x for x in data};used={x['slug'] for x in data};tr=str.maketrans(dict(zip('абвгдеёзийклмнопрстуфхцчшщъыьэюя',['a','b','v','g','d','e','yo','z','i','y','k','l','m','n','o','p','r','s','t','u','f','kh','ts','ch','sh','shch','','y','','e','yu','ya'])))
def slug(x):return re.sub('[^a-z0-9]+','-',x.lower().translate(tr)).strip('-')
rows=[]
for row in s.select('tr'):
 c=row.find_all('td',recursive=False)
 if len(c)>=2 and 'СТАДИИ СТРОИТЕЛЬСТВА' in c[1].get_text(' ',strip=True) and c[0].find('img',title=True):rows.append(c)
new=0; pending=[];report=[]
for c in rows:
 main=c[0].find('img',title=True);name=main['title'].strip();key=norm(name);e=by.get(key)
 if not e:
  sp=slug(name);sp=sp if sp not in used else sp+'-narod';used.add(sp);e={'slug':sp,'name':name,'category':'buildings','type':'Постройка','purchase':'нет данных','sale':'нет данных','obtain':'нет данных','use':'нет данных','features':'нет данных','versions':'браузерная версия; платформа и дата редакции не установлены','sources':[],'image':None,'links':[],'event':'нет данных','original_category':'Постройки'};data.append(e);by[key]=e;new+=1
 imgurl=urljoin(url,main.get('src',''));first=[]
 for node in c[0].descendants:
  if isinstance(node,bs4.element.NavigableString):
   txt=str(node).strip()
   if txt:first.append(txt)
  elif node.name=='img' and node.get('title'):first.append('['+node['title']+']')
 # Extract construction markers and resource pictograms only, without including later production sections.
 active=False;stage=None;digits='';stages={};unknown=[]
 for node in c[1].descendants:
  if isinstance(node,bs4.element.NavigableString):
   text=str(node).strip().upper()
   if 'СТАДИИ СТРОИТЕЛЬСТВА' in text:active=True
   elif active and any(h in text for h in ['ПРОИЗВОДСТВО','МОДЕРНИЗАЦИЯ','БОНУС-РУЛЕТКА','ОБМЕН']):active=False
   continue
  if not active or node.name!='img':continue
  src=node.get('_mce_src') or node.get('src','');raw=unquote(src);filename=raw.split('/')[-1];
  if '/Numeracia/' in raw:
   m=re.match(r'(\d+)\.png',filename,re.I)
   if m:stage=m.group(1);stages.setdefault(stage,[]);digits=''
  elif '/nomer/' in raw:
   m=re.match(r'(\d)\.png',filename,re.I)
   if m:digits+=m.group(1)
  elif filename.lower() in ('plus.png','_.png'):continue
  elif stage is not None:
   parent=node.find_parent('a');href=parent.get('href','') if parent else '';title=node.get('title','').strip()
   if href.lower().endswith('#monet') or filename.lower()=='monet.png':label='монеты'
   elif title:label=title
   elif '#' in href:label='значок #'+unquote(href.split('#',1)[1])
   else:label='значок '+filename;unknown.append(filename)
   stages[stage].append((digits if digits else '?')+' × '+label);digits=''
 fields={'Исходные подписи и цифры в первой колонке':' | '.join(first),'Стадии по пиктограммам': '\n'.join('Стадия '+k+': '+' + '.join(v) for k,v in stages.items()) or 'Не удалось автоматически распознать; см. источник'}
 # don't replace the separately hand-checked Sklep transcription
 rid='narod-building-pictogram-'+e['slug']; e.setdefault('prior_records',[]);e['prior_records']=[x for x in e['prior_records'] if x.get('original_id')!=rid]+[{'original_id':rid,'original_category':'Постройки','version':'браузерная версия; платформа не определена','date':'дата редакции не установлена','fields':fields,'confidence':'Автоматическое чтение цифровых пиктограмм и их подписей; знак ? означает нераспознанное количество, подписи могут содержать ошибки источника. Требуется ручная сверка каждой стадии.'}]
 if not any(x.get('url')==url for x in e['sources']):e['sources'].append({'url':url,'label':'Каталог построек: строка и пиктограммы; дата неизвестна'})
 if not e.get('image') and imgurl:pending.append((e,imgurl))
 report.append({'name':name,'stage_count':len(stages),'unknown_labels':unknown,'image_url':imgurl})
hashes={hashlib.sha256(x.read_bytes()).hexdigest():x for x in (P/'img').rglob('*') if x.is_file()}
def fetch(x):
 e,u=x
 try:
  r=requests.get(u,timeout=6);r.raise_for_status();b=r.content;ext='png' if b.startswith(b'\x89PNG\r\n\x1a\n') else 'jpg' if b.startswith(b'\xff\xd8\xff') else 'gif' if b[:6] in (b'GIF87a',b'GIF89a') else None
  return e,u,b,ext
 except Exception:return e,u,None,None
ok=0
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
 for e,u,b,ext in pool.map(fetch,pending):
  if not ext:continue
  h=hashlib.sha256(b).hexdigest();dest=hashes.get(h)
  if not dest:dest=P/'img/archive'/f'{e["slug"]}-{h[:12]}.{ext}';dest.write_bytes(b);hashes[h]=dest
  e['image']={'path':str(dest.relative_to(P)),'retrieved_from':u,'attribution':u,'source_page':url,'note':'Исходный файл без перекодирования; авторство не установлено.'};ok+=1
F.write_text(json.dumps(data,ensure_ascii=False,indent=2));(P/'data/narod-buildings-audit.json').write_text(json.dumps({'source':url,'read_rows':len(rows),'new_cards':new,'images_added':ok,'images_unavailable':len(pending)-ok,'method':'Пиктограммы распознаны автоматически; построчная ручная проверка не завершена.','rows':report},ensure_ascii=False,indent=2));print('rows',len(rows),'new',new,'images',ok,'unavailable',len(pending)-ok,'no stages',sum(not a['stage_count'] for a in report))

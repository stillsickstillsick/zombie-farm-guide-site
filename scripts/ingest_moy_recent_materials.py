"""Read recent-material entries from a single browser-game catalogue; checkpoint each page."""
import requests,bs4,re,json,hashlib,concurrent.futures
from pathlib import Path
from urllib.parse import urljoin,urlsplit
P=Path(__file__).resolve().parents[1];index='https://zombie-island.moy.su/blog/products_gde_vzjat_materialy_materials_zombie_farm_igra_mania_island/2012-11-11-1387';s=bs4.BeautifulSoup(requests.get(index,timeout=10).content,'html.parser');tasks=[]
for d in s.select('.blog_body_mat .i_new'):
 a=d.find('a',href=True);i=d.find('img');p=d.find('p');
 if not (a and i and p ):continue
 u=urljoin(index,a['href']);tasks.append({'listing_name':p.get_text(' ',strip=True),'url':u,'listing_image':urljoin(index,i.get('src',''))})
def get(x):
 try:
  r=requests.get(x['url'],timeout=7);r.raise_for_status();s=bs4.BeautifulSoup(r.content,'html.parser');h=s.find('h1');root=h.find_parent('div',class_='ind') if h else None;head=root.select_one('.ind_1') if root else None
  if not h or not root or not head or 'Материал' not in head.get_text(' ',strip=True):return {**x,'error':'Нет подтверждённого блока материала'}
  for t in root.select('script,style,ins'):t.decompose()
  img=head.select_one('img[src]');txt=root.get_text('\n',strip=True);return {**x,'name':h.get_text(' ',strip=True),'text':re.sub(r'\n{3,}','\n\n',txt),'image':urljoin(x['url'],img['src']) if img else None}
 except Exception as e:return {**x,'error':str(e)[:200]}
audit=P/'data/moy-recent-materials-audit.json';old=json.loads(audit.read_text()) if audit.exists() else {};cached={x['url']:x for x in old.get('records',[]) if 'error' not in x}; records=list(cached.values());tasks=[x for x in tasks if x['url'] not in cached]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
 for r in ex.map(get,tasks):
  records.append(r);(P/'data/moy-recent-materials-audit.json').write_text(json.dumps({'catalog':index,'note':'Блок новых записей; каждая статья проверена отдельно и сохраняется только если явно указана как материал. Дата URL не является датой последней правки.','records':records},ensure_ascii=False,indent=2))
F=P/'data/materials.json';data=json.loads(F.read_text());norm=lambda t:re.sub(r'\s+',' ',t.casefold().replace('ё','е')).strip();lookup={norm(e['name']):e for e in data};slugs={e['slug'] for e in data};tr=str.maketrans(dict(zip('абвгдеёзийклмнопрстуфхцчшщъыьэюя',['a','b','v','g','d','e','yo','z','i','y','k','l','m','n','o','p','r','s','t','u','f','kh','ts','ch','sh','shch','','y','','e','yu','ya'])));pending=[];new=added=0
for r in records:
 if 'error' in r:continue
 name=r['name'];e=lookup.get(norm(name));id=r['url'].rstrip('/').split('-')[-1]
 if not e:
  slug=re.sub(r'[^a-z0-9]+','-',name.lower().translate(tr)).strip('-') or 'material';slug=slug if slug not in slugs else slug+'-'+id;slugs.add(slug);e={'slug':slug,'name':name,'category':'materials','type':'Материал','purchase':'нет данных','sale':'нет данных','obtain':'нет данных','use':'нет данных','features':'нет данных','versions':'браузерная Зомби Ферма / Зомби Мания; платформу и дату редакции уточнить','sources':[],'image':None,'links':[],'event':'нет данных','original_category':'Материалы'};data.append(e);lookup[norm(name)]=e;new+=1
 rid='moy-material-'+id;e.setdefault('prior_records',[])
 if not any(x.get('original_id')==rid for x in e['prior_records']):e['prior_records'].append({'original_id':rid,'original_category':'Материалы','version':'браузерная Зомби Ферма / Зомби Мания; платформа не указана','date':'дата URL — дата размещения, редакция могла изменяться','fields':{'Текст основного блока статьи':r['text']},'confidence':'Прочитана отдельная статья. Значки без текстовых подписей и количества могут быть не извлечены; требуется проверка версии и дата редакции. Связь с ЗомбиСити возможна.'});added+=1
 if not any(x.get('url')==r['url'] for x in e['sources']):e['sources'].append({'url':r['url'],'label':'Zombie-island.moy.su: прочитана отдельная статья материала'})
 if not e.get('image') and r.get('image'):pending.append((e,r))
F.write_text(json.dumps(data,ensure_ascii=False,indent=2));hashes={hashlib.sha256(f.read_bytes()).hexdigest():f for f in (P/'img').rglob('*') if f.is_file()}
def img(z):
 e,r=z;original=r['image'];u=original.replace('http://zombicity.info','https://zombie-island.moy.su')
 try:
  q=requests.get(u,timeout=6);q.raise_for_status();b=q.content;ext='png' if b.startswith(b'\x89PNG\r\n\x1a\n') else 'jpg' if b.startswith(b'\xff\xd8\xff') else 'gif' if b[:6] in (b'GIF87a',b'GIF89a') else None;return e,r,u,b,ext
 except:return e,r,u,None,None
ok=0
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
 for e,r,u,b,ext in ex.map(img,pending):
  if not ext:continue
  h=hashlib.sha256(b).hexdigest();f=hashes.get(h)
  if not f:f=P/'img/archive'/f'{e["slug"]}-{h[:12]}.{ext}';f.write_bytes(b);hashes[h]=f
  e['image']={'path':str(f.relative_to(P)),'retrieved_from':u,'attribution':r['image'],'source_page':r['url'],'note':'Исходный файл без перекодирования; при замене домена идентичность оригиналу не проверена, авторство не установлено.'};ok+=1
F.write_text(json.dumps(data,ensure_ascii=False,indent=2));print('catalog entries',len(tasks),'articles read',sum('error' not in r for r in records),'failed',sum('error' in r for r in records),'new',new,'added facts',added,'images',ok,'unavailable',len(pending)-ok)

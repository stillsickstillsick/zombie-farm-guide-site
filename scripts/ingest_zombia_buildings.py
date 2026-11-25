"""Import building catalogue listings while preserving inline icon filenames, not unreliable alt captions."""
import requests,bs4,json,re,hashlib,concurrent.futures
from pathlib import Path
from urllib.parse import urljoin,urlsplit,unquote
P=Path(__file__).resolve().parents[1];F=P/'data/buildings.json';data=json.loads(F.read_text());norm=lambda t:re.sub(r'\s+',' ',t.casefold().replace('ё','е')).strip();by={norm(e['name']):e for e in data};used={e['slug'] for e in data};tr=str.maketrans(dict(zip('абвгдеёзийклмнопрстуфхцчшщъыьэюя',['a','b','v','g','d','e','yo','z','i','y','k','l','m','n','o','p','r','s','t','u','f','kh','ts','ch','sh','shch','','y','','e','yu','ya'])))
def slug(n):return re.sub('[^a-z0-9]+','-',n.lower().translate(tr)).strip('-') or 'postroyka'
def getpage(i):
 url='https://zombi.at.ua/board/postrojki/9'+('-'+str(i) if i>1 else '')
 try:
  r=requests.get(url,timeout=8);r.raise_for_status();s=bs4.BeautifulSoup(r.content,'html.parser');items=[]
  for t in s.select('.eTitle'):
   a=t.find('a',href=True);m=re.search(r'/\d+-1-0-(\d+)',a['href']) if a else None
   if not m:continue
   name=a.get_text(' ',strip=True).replace('(Кликнуть, чтобы прокомментировать)','').strip();td=t.parent;im=td.find('img',src=True);img=urljoin(url,im['src']) if im else None;item_url=urljoin(url,a['href']);t.decompose()
   for x in td.select('script,style,ins'):x.decompose()
   for x in td.find_all('img'):
    src=x.get('src','');x.replace_with(' [рисунок: '+unquote(urlsplit(src).path.split('/')[-1])+'] ')
   raw=re.sub(r'\n{3,}','\n\n',td.get_text('\n',strip=True));items.append({'id':m.group(1),'name':name,'text':raw,'image_url':img,'listing':url,'item_url':item_url})
  return {'url':url,'items':items,'error':None if items else 'Нет карточек'}
 except Exception as e:return {'url':url,'items':[],'error':str(e)[:150]}
results=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
 for row in ex.map(getpage,range(1,9)):
  results.append(row);(P/'data/zombia-buildings-audit.json').write_text(json.dumps({'description':'8 страниц каталога; карточки отдельных статей не обязательно посещены. Названия файлов иконок сохранены без расшифровки, поскольку alt-тексты могут быть неверны.','pages':results},ensure_ascii=False,indent=2))
new=added=0;pending=[]
for row in results:
 for item in row['items']:
  e=by.get(norm(item['name']))
  if not e:
   sp=slug(item['name']);sp=sp if sp not in used else sp+'-'+item['id'];used.add(sp);e={'slug':sp,'name':item['name'],'category':'buildings','type':'Постройка','purchase':'нет данных','sale':'нет данных','obtain':'нет данных','use':'нет данных','features':'нет данных','versions':'браузерная версия; платформа и дата редакции не установлены','sources':[],'image':None,'links':[],'event':'нет данных','original_category':'Постройки'};data.append(e);by[norm(item['name'])]=e;new+=1
  rid='zombia-building-'+item['id'];e.setdefault('prior_records',[])
  if not any(x.get('original_id')==rid for x in e['prior_records']):e['prior_records'].append({'original_id':rid,'original_category':'Постройки','version':'браузерная версия; платформа не установлена','date':'дата редакции списка не установлена','fields':{'Сведения из списка, включая имена файлов пиктограмм':item['text']},'confidence':'Прочитан список. Имена файлов пиктограмм приводятся как есть: они не гарантируют идентификацию материала. Alt-атрибуты источника содержат ошибки. Отдельная статья и дата не проверены.'});added+=1
  for u,l in [(item['listing'],'ZOMBIA: прочитана карточка в каталоге'),(item['item_url'],'Адрес отдельной карточки, отдельный доступ не проверен')]:
   if not any(x.get('url')==u for x in e['sources']):e['sources'].append({'url':u,'label':l})
  if not e.get('image') and item['image_url']:pending.append((e,item))
F.write_text(json.dumps(data,ensure_ascii=False,indent=2))
hashes={hashlib.sha256(x.read_bytes()).hexdigest():x for x in (P/'img').rglob('*') if x.is_file()}
def getpic(x):
 e,item=x;u=item['image_url'].replace('http://zombia.ru/','https://zombi.at.ua/').replace('https://zombia.ru/','https://zombi.at.ua/')
 try:
  r=requests.get(u,timeout=6);r.raise_for_status();b=r.content;ext='png' if b.startswith(b'\x89PNG\r\n\x1a\n') else 'jpg' if b.startswith(b'\xff\xd8\xff') else 'gif' if b[:6] in (b'GIF87a',b'GIF89a') else None;return e,item,u,b,ext
 except Exception:return e,item,u,None,None
ok=0
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
 for e,item,u,b,ext in ex.map(getpic,pending):
  if not ext:continue
  h=hashlib.sha256(b).hexdigest();p=hashes.get(h)
  if not p:p=P/'img/archive'/f'{e["slug"]}-{h[:12]}.{ext}';p.write_bytes(b);hashes[h]=p
  e['image']={'path':str(p.relative_to(P)),'retrieved_from':u,'attribution':item['image_url'],'source_page':item['listing'],'note':'Первая иллюстрация строки каталога; авторство не подтверждено. Идентичность изображения при замене домена не проверена.'};ok+=1
F.write_text(json.dumps(data,ensure_ascii=False,indent=2));sources=json.loads((P/'data/sources.json').read_text())
for x in sources:
 if x['number']==5 and 'каталога построек 9' not in x['summary']:x['summary']+=' Исследованы 8 страниц каталога построек 9: сведения строк и имена файлов пиктограмм перенесены; подписи alt часто ошибочны, стадии требуют ручной сверки.'
(P/'data/sources.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2));print('pages',len(results),'errors',sum(bool(x['error']) for x in results),'cards read',sum(len(x['items']) for x in results),'new',new,'added source rows',added,'images',ok,'failed images',len(pending)-ok)

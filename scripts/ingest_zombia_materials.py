"""Ingest individually checked ZOMBIA browser-game material articles, keeping table labels and source fidelity."""
import json,re,requests,bs4,concurrent.futures,hashlib
from pathlib import Path
from urllib.parse import urljoin,urlsplit,urlunsplit
P=Path(__file__).resolve().parents[1];datafile=P/'data/materials.json';items=json.loads(datafile.read_text());root='https://zombi.at.ua';index=root+'/board/materialy/16'
r=requests.get(index,timeout=25);r.raise_for_status();s=bs4.BeautifulSoup(r.content,'html.parser');links={}
for a in s.select('a[href]'):
 u=urljoin(index,a['href']);p=urlsplit(u);match=re.search(r'/(\d+)-1-0-(\d+)',p.path)
 if not match or int(match.group(1)) not in {1,2,3,4,5,6,7,8,25,27,28,30,31}:continue
 u=urlunsplit(('https','zombi.at.ua',p.path,'',''));links[int(match.group(2))]=u

def read_article(u):
 try:
  r=requests.get(u,timeout=15);r.raise_for_status();s=bs4.BeautifulSoup(r.content,'html.parser');t=s.select_one('.eTitle');node=s.select_one('td.eText');
  if not t or not node:return {'url':u,'error':'нет карточки'}
  name=t.get_text(' ',strip=True).replace('(Кликнуть, чтобы прокомментировать)','').strip();table=node.find('table');rows=table.find_all('tr',recursive=True) if table else []
  if len(rows)<2:return {'url':u,'name':name,'error':'нет таблицы'}
  heads=rows[0].find_all(['td','th'],recursive=False);cells=rows[1].find_all(['td','th'],recursive=False)
  if not heads or len(heads)!=len(cells):return {'url':u,'name':name,'error':'нет сопоставимых колонок'}
  fields={};picture=None
  for i,(head,cell) in enumerate(zip(heads,cells)):
   label=head.get_text(' ',strip=True).strip(':') or f'Колонка {i+1}'
   # Keep text and image alternative labels in their original sequence; mark image-derived labels as such.
   for im in cell.find_all('img'):
    alt=(im.get('alt') or im.get('title') or '').strip()
    if i==0 and not picture:
     imgurl=urljoin(u,im.get('src',''));picture={'url':imgurl,'alt':alt}
    if alt:im.replace_with(f' [изображение: {alt}] ')
   text=cell.get_text('\n',strip=True);text=re.sub(r'\n{3,}','\n\n',text)
   fields[label]=text or 'нет текстовых данных; возможны неподписанные изображения'
  whole=s.get_text(' ',strip=True);date=re.search(r'Размещено:\s*(\d{1,2}\s+[^,]+,\s*\d{2}:\d{2})',whole)
  return {'url':u,'name':name,'fields':fields,'date':date.group(1) if date else 'дата публикации не установлена','image':picture}
 except Exception as e:return {'url':u,'error':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:results=list(ex.map(read_article,links.values()))
tr=str.maketrans(dict(zip('абвгдеёзийклмнопрстуфхцчшщъыьэюя',['a','b','v','g','d','e','yo','z','i','y','k','l','m','n','o','p','r','s','t','u','f','kh','ts','ch','sh','shch','','y','','e','yu','ya'])))
def slug(s):return re.sub(r'[^a-z0-9]+','-',s.lower().translate(tr)).strip('-') or 'material'
def norm(s):return re.sub(r'\s+',' ',s.strip().casefold().replace('ё','е'))
# Only unambiguous spelling variations are mapped.
alias={'канаты':'канат','брус секвойи':'брус секвойи','бревна':'брёвна','лента':'лента для скотча'}
by={norm(x['name']):x for x in items};used={x['slug'] for x in items};assets={hashlib.sha256(f.read_bytes()).hexdigest():f for f in (P/'img').rglob('*') if f.is_file()};download=[];added=0;enriched=0;failed=[];ambiguous=[]
for res in results:
 if 'error' in res:failed.append(res);continue
 name=res['name'];key=norm(alias.get(norm(name),name));e=by.get(key)
 # Generic "Лента" is not guaranteed to be the same as tape ribbon; leave separate pending review.
 if norm(name)=='лента':key=norm(name);e=by.get(key);ambiguous.append('Лента — не объединена с «Лентой для скотча» до проверки.')
 if not e:
  slug0=slug(name);sp=slug0
  if sp in used:sp=slug0+'-'+res['url'].rsplit('-',1)[-1]
  used.add(sp);e={'slug':sp,'name':name,'category':'materials','type':'нет данных','purchase':'нет данных','sale':'нет данных','obtain':'нет данных','use':'нет данных','features':'нет данных','versions':'ВКонтакте; данные из ZOMBIA; '+res['date'],'sources':[],'image':None,'links':[],'event':'нет данных','original_category':'Материалы'};items.append(e);by[key]=e;added+=1
 else:enriched+=1
 e.setdefault('prior_records',[])
 rid='zombia-'+res['url'].rsplit('-',1)[-1]
 if not any(x.get('original_id')==rid for x in e['prior_records']):e['prior_records'].append({'original_id':rid,'original_category':'Материалы','version':'ВКонтакте, ZOMBIA','date':res['date']+'; дата редакции не установлена','fields':res['fields'],'confidence':'Данные одной исторической фанатской страницы; цифры и подписи изображений требуют сверки. Описание и условия сохранены по колонкам без додумывания.'})
 if not any(x.get('url')==res['url'] for x in e['sources']):e['sources'].append({'url':res['url'],'label':'ZOMBIA: прочитана индивидуальная карточка; '+res['date']})
 if not e.get('image') and res.get('image'):
  p=res['image'];alt=norm(p['alt']);
  if alt and (alt==norm(name) or alt in ('материал '+norm(name),)):
   u=p['url'];mapped=u.replace('http://zombia.ru/','https://zombi.at.ua/').replace('https://zombia.ru/','https://zombi.at.ua/').replace('http://zombi.at.ua/','https://zombi.at.ua/')
   download.append((e,p['url'],mapped,res['url']))
def fetch(job):
 try:
  r=requests.get(job[2],timeout=10);r.raise_for_status();b=r.content;ext='png' if b.startswith(b'\x89PNG\r\n\x1a\n') else 'jpg' if b[:3]==b'\xff\xd8\xff' else 'gif' if b[:6] in (b'GIF87a',b'GIF89a') else None;return job,b,ext
 except:return job,None,None
imgok=0
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
 for (e,original,mapped,page),b,ext in ex.map(fetch,download):
  if not ext:continue
  h=hashlib.sha256(b).hexdigest()
  if h not in assets:
   f=P/'img/archive'/f'{e["slug"]}-{h[:12]}.{ext}';f.write_bytes(b);assets[h]=f
  e['image']={'path':str(assets[h].relative_to(P)),'retrieved_from':mapped,'attribution':original,'source_page':page,'note':'Получены исходные байты по адресу страницы; идентичность оригинальному домену при замене хоста не подтверждена.'};imgok+=1
datafile.write_text(json.dumps(items,ensure_ascii=False,indent=2));report={'catalog':index,'discovered_unique':len(links),'articles_read':len(results)-len(failed),'new_cards':added,'existing_enriched':enriched,'images_recovered':imgok,'errors':failed,'ambiguities':ambiguous};(P/'data'/'zombia-materials-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in report.items() if k not in ('errors','ambiguities')},ensure_ascii=False));print('failed',len(failed));print('ambiguous',ambiguous)

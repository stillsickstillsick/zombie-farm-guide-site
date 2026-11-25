"""Import only catalog-visible labels; individually linked articles are NOT assumed read."""
import collections,concurrent.futures,hashlib,json,re,requests
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urljoin,urlparse
P=Path(__file__).resolve().parents[1];DATA=P/'data';PAGE='https://web.archive.org/web/20191210005054/https://zombicity.info/blog/ostrova_zombie_farm_island_podzemele_bridge_most_postroyka_mania/2012-11-10-1378'; BASE='https://zombicity.info';RAW=PAGE.replace('/20191210005054/','/20191210005054id_/')
r=requests.get(RAW,timeout=30);r.raise_for_status();s=BeautifulSoup(r.content,'html.parser');body=s.select_one('.blog_body_mat');assert body
items=[];group=''
for node in body.find_all(recursive=False):
 if node.name!='div':continue
 cls=node.get('class',[])
 if 'panel_mat' in cls:
  h=node.find('h2')
  if h:group=h.get_text(' ',strip=True)
 if 'i_new' not in cls:continue
 title=node.find('p');link=node.find('a',href=True);img=node.find('img',src=True)
 if not title or not link:continue
 name=title.get_text(' ',strip=True);u=urljoin(BASE,link['href']);m=re.search(r'-(\d+)$',urlparse(u).path)
 if not m:continue
 image=urljoin(BASE,img['src']) if img else None
 items.append({'name':name,'section':group,'article_url':u,'article_archive_url':'https://web.archive.org/web/20191210005054/'+u,'image_original':image,'id':m.group(1)})
assert len(items)>200
(DATA/'zombicity-islands-catalog-audit.json').write_text(json.dumps({'catalog_snapshot':PAGE,'note':'Только подписи и ссылки каталога; отдельные статьи и даты снимков изображений отдельно не установлены без проверки.','items':items},ensure_ascii=False,indent=2))
f=DATA/'locations.json';a=json.loads(f.read_text());norm=lambda t:re.sub(r'[^а-яa-z0-9]+',' ',t.lower().replace('ё','е')).strip();lookup=collections.defaultdict(list)
for e in a:lookup[norm(e['name'])].append(e)
name_counts=collections.Counter(norm(x['name']) for x in items if x['section'].startswith(('Новые Острова','Домашние Острова','Первые Дальние')))
allowed_pirates={'Остров Сокровищ','Таинственный остров','Жуткий остров','Древний остров','Роща Калипсо','Спутник Гиас','Ипсилон Андромеды','Гамма Цефея','Край'}
new=match=skip=0;image_work=[]
for x in items:
 if not (x['section'].startswith(('Новые Острова','Домашние Острова','Первые Дальние')) or x['section'].startswith('Телепорты пиратских') and x['name'] in allowed_pirates):continue
 key=norm(x['name']);existing=lookup.get(key,[])
 # Same label with different links may describe distinct historical versions.
 if name_counts[key]>1 or len(existing)>1:skip+=1;continue
 if existing:e=existing[0];match+=1
 else:
  # Avoid automatic duplication of near-identical labels until reviewed manually.
  if any((len(key)>5 and (key in k or k in key)) for k in lookup if len(k)>5):skip+=1;continue
  slug='zombicity-island-'+x['id'];e=next((v for v in a if v['slug']==slug),None)
  if not e:
   e={'slug':slug,'name':x['name'],'category':'locations','type':'Локация по каталогу ЗомбиСити','purchase':'нет данных','sale':'нет данных','obtain':'нет данных','use':'нет данных','features':'нет данных','versions':'историческая браузерная версия; платформа и редакция не уточнены','sources':[],'image':None,'links':[],'event':'нет данных','prior_records':[]};a.append(e);new+=1
  lookup[key].append(e)
 rec={'original_id':'zombicity-island-catalog-'+x['id'],'original_category':'Острова и подземелья','version':'браузерная «Зомби Ферма» / «Зомби Мания»; платформа не уточнена','date':'снимок каталога 10.12.2019; дата редакции неизвестна','fields':{'Каталог':f'В разделе «{x["section"]}» указана локация «{x["name"]}».','Оговорка':'Каталог показывает название, картинку и ссылку; отдельная статья по этой ссылке не прочитана в рамках этого импорта. Условия доступа и версии требуют проверки.'},'confidence':'Фанатский каталог; возможны общие картинки для разных локаций и зависимость от других источников.'}
 e['prior_records']=[v for v in e.get('prior_records',[]) if v.get('original_id')!=rec['original_id']]+[rec]
 if not any(v['url']==PAGE for v in e['sources']):e['sources'].append({'url':PAGE,'label':'ЗомбиСити: архив каталога, снимок 10.12.2019'})
 if not any(v['url']==x['article_archive_url'] for v in e['sources']):e['sources'].append({'url':x['article_archive_url'],'label':'Ссылка из каталога; отдельная статья не проверена'})
 if not e.get('image') and x['image_original']:image_work.append((e,x))
# Fetch the actual archive capture, not a re-encoded or generated substitute.
def download(pair):
 e,x=pair;u='https://web.archive.org/web/20191210005054im_/'+x['image_original']
 try:
  z=requests.get(u,timeout=10);z.raise_for_status();b=z.content
  ext='png' if b.startswith(b'\x89PNG\r\n\x1a\n') else 'gif' if b[:6] in (b'GIF87a',b'GIF89a') else 'jpg' if b[:3]==b'\xff\xd8\xff' else None
  # Redirects must still point to the same original path, not a different archived item.
  if not ext or urlparse(x['image_original']).path not in urlparse(z.url).path:return pair,None,None,None
  return pair,b,ext,z.url
 except Exception:return pair,None,None,None
hashes={hashlib.sha256(p.read_bytes()).hexdigest():p for p in (P/'img').rglob('*') if p.is_file()};ok=0
with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
 for (e,x),b,ext,actual in pool.map(download,image_work):
  if not b:continue
  h=hashlib.sha256(b).hexdigest()
  if h not in hashes:
   out=P/'img'/'locations'/f'zombicity-{x["id"]}-{h[:12]}.{ext}';out.parent.mkdir(exist_ok=True,parents=True);out.write_bytes(b);hashes[h]=out
  e['image']={'path':str(hashes[h].relative_to(P)),'retrieved_from':actual,'attribution':x['image_original'],'source_page':PAGE,'note':'Иллюстрация каталога; фактический URL указывает снимок файла, который может отличаться от даты снимка страницы. Некоторые картинки общие для нескольких локаций; авторство не установлено.'};ok+=1
f.write_text(json.dumps(a,ensure_ascii=False,indent=2));print('catalog entries',len(items),'new locations',new,'exact matches',match,'ambiguous skipped',skip,'images fetched',ok,'failed',len(image_work)-ok)
sourcefile=DATA/'sources.json';sources=json.loads(sourcefile.read_text())
if not any(z.get('url')==PAGE for z in sources):sources.append({'number':max(z.get('number',0) for z in sources)+1,'name':'ЗомбиСити — каталог островов (архив 10.12.2019)','category':'Прохождения и каталоги','url':PAGE,'summary':f'Прочитан каталог: {len(items)} подписей и ссылок на острова и переходы. Состояние отдельных статей и независимость от других сайтов требуют проверки; дата редакции неизвестна.'})
sourcefile.write_text(json.dumps(sources,ensure_ascii=False,indent=2))

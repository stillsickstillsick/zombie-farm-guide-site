"""Compare two captures of the same ZombiCity catalog; never claim independence."""
import collections,concurrent.futures,hashlib,json,re,requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin,urlparse
from pathlib import Path
P=Path(__file__).resolve().parents[1];D=P/'data'
base='https://zombicity.info';suffix='/blog/ostrova_zombie_farm_island_podzemele_bridge_most_postroyka_mania/2012-11-10-1378'
page='https://web.archive.org/web/20180914143019/'+base+suffix
r=requests.get(page.replace('20180914143019/','20180914143019id_/'),timeout=20);r.raise_for_status();body=BeautifulSoup(r.content,'html.parser').select_one('.blog_body_mat');assert body
rows=[];section=''
for node in body.find_all(recursive=False):
 if node.name!='div':continue
 cls=node.get('class',[])
 if 'panel_mat' in cls and node.find('h2'):section=node.find('h2').get_text(' ',strip=True)
 if 'i_new' not in cls:continue
 p=node.find('p');a=node.find('a',href=True);im=node.find('img',src=True)
 if not p or not a:continue
 u=urljoin(base,a['href']);m=re.search(r'-(\d+)$',urlparse(u).path)
 if m:rows.append({'id':m.group(1),'name':p.get_text(' ',strip=True),'section':section,'article_url':u,'image_original':urljoin(base,im['src']) if im else None})
assert len(rows)==258
later=json.loads((D/'zombicity-islands-catalog-audit.json').read_text());later_by={x['id']:x for x in later['items']};earlier_by={x['id']:x for x in rows};only2018=sorted(set(earlier_by)-set(later_by));only2019=sorted(set(later_by)-set(earlier_by));changed=[]
for x in rows:
 y=later_by.get(x['id'])
 if y:
  for k in ('name','section','image_original'):
   if x[k]!=y[k]:changed.append({'id':x['id'],'field':k,'2018':x[k],'2019':y[k]})
comparison={'snapshot_2018':page,'snapshot_2019':later['catalog_snapshot'],'entries_2018':rows,'ids_only_2018':only2018,'ids_only_2019':only2019,'changes':changed,'method':'Сопоставление по числовому идентификатору ссылки; сравниваются подписи, разделы и URL изображений. Отдельные статьи не проверены. Это два снимка одного сайта, не независимые источники.'}
(D/'zombicity-islands-catalog-2018-audit.json').write_text(json.dumps(comparison,ensure_ascii=False,indent=2))
f=D/'locations.json';a=json.loads(f.read_text());matched=0;work=[]
for e in a:
 ids=[x.get('original_id','').removeprefix('zombicity-island-catalog-') for x in e.get('prior_records',[]) if x.get('original_id','').startswith('zombicity-island-catalog-')]
 ids=[x for x in ids if x in earlier_by]
 if not ids:continue
 matched+=1
 if not any(x['url']==page for x in e['sources']):e['sources'].append({'url':page,'label':'ЗомбиСити: тот же каталог, снимок 14.09.2018; не независимый источник'})
 for rec in e['prior_records']:
  if rec.get('original_id')=='zombicity-island-catalog-'+ids[0]:rec['fields']['Сравнение снимков']='Эта же подпись, раздел и адрес картинки присутствуют в снимке того же каталога 14.09.2018; это не независимое подтверждение.'
 if not e.get('image') and earlier_by[ids[0]]['image_original']:work.append((e,earlier_by[ids[0]]))
# Bounded batch; preserve actual redirect URL and its own capture date.
def download(pair):
 e,x=pair;orig=x['image_original'];url='https://web.archive.org/web/20180914143019im_/'+orig
 try:
  res=requests.get(url,timeout=12);res.raise_for_status();b=res.content
  ext='png' if b.startswith(b'\x89PNG\r\n\x1a\n') else 'gif' if b[:6] in (b'GIF87a',b'GIF89a') else 'jpg' if b[:3]==b'\xff\xd8\xff' else None
  if not ext or urlparse(orig).path not in urlparse(res.url).path:return pair,None,None,None
  return pair,b,ext,res.url
 except Exception:return pair,None,None,None
hashes={hashlib.sha256(p.read_bytes()).hexdigest():p for p in (P/'img').rglob('*') if p.is_file()};ok=0;selected=work[:45]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 for (e,x),b,ext,actual in pool.map(download,selected):
  if not b:continue
  h=hashlib.sha256(b).hexdigest()
  if h not in hashes:
   out=P/'img'/'locations'/f'zombicity-{x["id"]}-{h[:12]}.{ext}';out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(b);hashes[h]=out
  e['image']={'path':str(hashes[h].relative_to(P)),'retrieved_from':actual,'attribution':x['image_original'],'source_page':page,'note':'Иллюстрация каталога. Архив мог вернуть снимок файла другой даты — она указана в ссылке на полученный файл; общие картинки и авторство требуют проверки.'};ok+=1
f.write_text(json.dumps(a,ensure_ascii=False,indent=2))
f=D/'economy.json';a=json.loads(f.read_text());e=next(x for x in a if x['slug']=='zombicity-travel-catalog-2019')
if not any(x['url']==page for x in e['sources']):e['sources'].append({'url':page,'label':'Снимок того же каталога 14.09.2018; не независимый источник'})
e['prior_records'][0]['fields']['Снимок 2018 года']='По ссылочным идентификаторам и подписям каталог 14.09.2018 содержит 258 записей; все они присутствуют в снимке 10.12.2019. В снимке 2019 ещё 15 идентификаторов; дата их добавления не установлена.'
f.write_text(json.dumps(a,ensure_ascii=False,indent=2))
f=D/'sources.json';a=json.loads(f.read_text())
if not any(x.get('url')==page for x in a):a.append({'number':max(x.get('number',0) for x in a)+1,'name':'ЗомбиСити — каталог островов (архив 14.09.2018)','category':'Прохождения и каталоги','url':page,'summary':'Ранний снимок того же каталога, что архив 10.12.2019: не независимый источник. 258 записей, все ссылки по ID присутствуют и в позднем снимке; дата редакции неизвестна.'})
f.write_text(json.dumps(a,ensure_ascii=False,indent=2))
print('2018',len(rows),'2019',len(later['items']),'2018 only',len(only2018),'2019 only',len(only2019),'changes',len(changed),'matched location cards',matched,'image added',ok,'failed',len(selected)-ok,'remaining candidates',len(work)-len(selected))

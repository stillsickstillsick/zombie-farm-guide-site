"""Download original island catalog image files from the live moy.su mirror.
Match by linked article ID AND exact catalog label, not names alone.
"""
import concurrent.futures,hashlib,json,re,requests
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urljoin,urlparse
P=Path(__file__).resolve().parents[1];D=P/'data';page='https://zombie-island.moy.su/blog/ostrova_zombie_farm_island_podzemele_bridge_most_postroyka_mania/2012-11-10-1378'
r=requests.get(page,timeout=25);r.raise_for_status();s=BeautifulSoup(r.content,'html.parser');catalog={}
for div in s.select('.i_new'):
 a=div.find('a',href=True);p=div.find('p');img=div.find('img',src=True)
 if not(a and p and img):continue
 m=re.search(r'-(\d+)$',urlparse(a['href']).path)
 if m:catalog[m.group(1)]={'name':p.get_text(' ',strip=True),'url':urljoin(page,img['src']),'article':urljoin(page,a['href'])}
f=D/'locations.json';records=json.loads(f.read_text());known=json.loads((D/'zombicity-islands-catalog-audit.json').read_text());byid={x['id']:x for x in known['items']};work=[];mismatches=[]
for e in records:
 if e.get('image'):continue
 for rec in e.get('prior_records',[]):
  t=rec.get('original_id','');id=t.removeprefix('zombicity-island-catalog-')
  if not t.startswith('zombicity-island-catalog-') or id not in catalog or id not in byid:continue
  if catalog[id]['name']!=byid[id]['name']:mismatches.append(id);continue
  work.append((e,id,catalog[id]));break
hashes={hashlib.sha256(p.read_bytes()).hexdigest():p for p in (P/'img').rglob('*') if p.is_file()}
def download(job):
 e,id,x=job
 try:
  u=urlparse(x['url']); source=x['url']
  if u.hostname in ('zombicity.info','www.zombicity.info'):source='https://zombie-island.moy.su'+u.path+('?' + u.query if u.query else '')
  r=requests.get(source,timeout=16);r.raise_for_status();b=r.content
  ext='png' if b.startswith(b'\x89PNG\r\n\x1a\n') else 'gif' if b[:6] in (b'GIF87a',b'GIF89a') else 'jpg' if b[:3]==b'\xff\xd8\xff' else None
  if not ext:raise ValueError('Ответ не распознан как PNG, JPEG или GIF')
  return job,b,ext,r.url,None
 except Exception as ex:return job,None,None,None,str(ex)[:180]
ok=0;failed=[];results=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
 for (e,id,x),b,ext,url,err in pool.map(download,work):
  if b is None:failed.append({'id':id,**x,'error':err});continue
  h=hashlib.sha256(b).hexdigest()
  if h not in hashes:
   p=P/'img'/'locations'/f'moy-island-{id}-{h[:12]}.{ext}';p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b);hashes[h]=p
  e['image']={'path':str(hashes[h].relative_to(P)),'retrieved_from':url,'attribution':url,'source_page':page,'note':'Иллюстрация каталога zombie-island.moy.su; совпадают идентификатор ссылки и подпись с каталогом ЗомбиСити. Если каталог ссылается на zombicity.info, использована копия по тому же пути на moy.su; побайтовая идентичность оригиналу не проверена. Сайты содержат общий контент и не считаются независимыми; дата файла и авторство неизвестны. Некоторые картинки могут быть общими для разных локаций.'}
  if not any(z['url']==page for z in e.get('sources',[])):e.setdefault('sources',[]).append({'url':page,'label':'Zombie-island.moy.su — иллюстрация каталога (связанный источник)'})
  results.append({'id':id,'name':x['name'],'image':url,'catalog_image_url':x['url'],'sha256':h});ok+=1
f.write_text(json.dumps(records,ensure_ascii=False,indent=2));(D/'moy-island-image-audit.json').write_text(json.dumps({'catalog_url':page,'matching':'Идентификатор связанной статьи и точная подпись каталога; связь сайтов означает отсутствие независимости.','downloaded':results,'failed':failed,'label_mismatches':mismatches},ensure_ascii=False,indent=2))
print('catalog',len(catalog),'candidates',len(work),'added',ok,'failed',len(failed),'mismatches',len(mismatches));print('errors',failed[:5])

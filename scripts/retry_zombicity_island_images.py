"""Retry archived catalog illustrations without altering their bytes; save a download audit."""
import concurrent.futures,hashlib,json,requests,re,time
from pathlib import Path
from urllib.parse import urlparse
P=Path(__file__).resolve().parents[1];D=P/'data';f=D/'locations.json';items=json.loads(f.read_text());catalog=json.loads((D/'zombicity-islands-catalog-audit.json').read_text());byid={x['id']:x for x in catalog['items']};work=[]
for e in items:
 if e.get('image'):continue
 for rec in e.get('prior_records',[]):
  v=rec.get('original_id','');id=v.removeprefix('zombicity-island-catalog-')
  if v.startswith('zombicity-island-catalog-') and id in byid and byid[id].get('image_original'):
   work.append((e,byid[id]));break
hashes={hashlib.sha256(x.read_bytes()).hexdigest():x for x in (P/'img').rglob('*') if x.is_file()}
def download(pair):
 e,x=pair;orig=x['image_original'];err='';wanted='https://web.archive.org/web/20180914143019im_/'+orig
 for i in range(3):
  try:
   r=requests.get(wanted,timeout=12);r.raise_for_status();b=r.content
   ext='png' if b.startswith(b'\x89PNG\r\n\x1a\n') else 'gif' if b[:6] in (b'GIF87a',b'GIF89a') else 'jpg' if b[:3]==b'\xff\xd8\xff' else None
   if not ext or urlparse(orig).path not in urlparse(r.url).path:raise ValueError('Ответ не является изображением исходного пути')
   return pair,b,ext,r.url,None
  except Exception as ex:err=f'{type(ex).__name__}: {str(ex)[:150]}';time.sleep(0.25*(i+1))
 return pair,None,None,None,err
ok=0;failed=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 for (e,x),b,ext,actual,error in pool.map(download,work):
  if not b:failed.append({'id':x['id'],'name':x['name'],'image_original':x['image_original'],'error':error});continue
  h=hashlib.sha256(b).hexdigest()
  if h not in hashes:
   path=P/'img'/'locations'/f'zombicity-{x["id"]}-{h[:12]}.{ext}';path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(b);hashes[h]=path
  e['image']={'path':str(hashes[h].relative_to(P)),'retrieved_from':actual,'attribution':x['image_original'],'source_page':catalog['catalog_snapshot'],'note':'Каталожное изображение, сохранено без перекодирования. Архив перенаправил на снимок файла, дата которого может отличаться от даты страницы; некоторые иллюстрации общие для нескольких локаций.'};ok+=1
f.write_text(json.dumps(items,ensure_ascii=False,indent=2));(D/'zombicity-image-retry-audit.json').write_text(json.dumps({'note':'Неудачи относятся к попытке загрузки, не доказывают отсутствия файла в архиве.','success':ok,'failed':failed},ensure_ascii=False,indent=2));print('проверено',len(work),'загружено',ok,'не получилось',len(failed))

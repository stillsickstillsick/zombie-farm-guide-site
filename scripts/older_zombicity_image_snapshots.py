"""Look up earlier Wayback image captures; write original bytes and actual capture URL."""
import concurrent.futures,hashlib,json,requests
from pathlib import Path
from urllib.parse import urlparse
P=Path(__file__).resolve().parents[1];D=P/'data';f=D/'locations.json';records=json.loads(f.read_text());cat=json.loads((D/'zombicity-islands-catalog-audit.json').read_text());byid={v['id']:v for v in cat['items']};work=[]
for e in records:
 if e.get('image'):continue
 for z in e.get('prior_records',[]):
  k=z.get('original_id','');i=k.removeprefix('zombicity-island-catalog-')
  if k.startswith('zombicity-island-catalog-') and i in byid and byid[i].get('image_original'):work.append((e,byid[i]));break
hashes={hashlib.sha256(p.read_bytes()).hexdigest():p for p in (P/'img').rglob('*') if p.is_file()}
def fetch(job):
 e,x=job;orig=x['image_original'];u=urlparse(orig);http='http://'+u.netloc+u.path+('?' + u.query if u.query else '');last=''
 for stamp in ['20160101000000','20140101000000','20180101000000','20170101000000']:
  for origin in (http,orig) if http!=orig else (http,):
   try:
    res=requests.get('https://web.archive.org/web/'+stamp+'im_/'+origin,timeout=6);res.raise_for_status();b=res.content
    ext='png' if b.startswith(b'\x89PNG\r\n\x1a\n') else 'gif' if b[:6] in (b'GIF87a',b'GIF89a') else 'jpg' if b[:3]==b'\xff\xd8\xff' else None
    if not ext or u.path not in urlparse(res.url).path:raise ValueError('Получен неподходящий ресурс')
    return job,b,ext,res.url,origin,None
   except Exception as exc:last=type(exc).__name__+': '+str(exc)[:120]
 return job,None,None,None,None,last
ok=0;failed=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 for (e,x),b,ext,actual,archive_origin,error in pool.map(fetch,work):
  if b is None:failed.append({'id':x['id'],'name':x['name'],'image_original':x['image_original'],'error':error});continue
  h=hashlib.sha256(b).hexdigest()
  if h not in hashes:
   p=P/'img'/'locations'/f'zombicity-{x["id"]}-{h[:12]}.{ext}';p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b);hashes[h]=p
  e['image']={'path':str(hashes[h].relative_to(P)),'retrieved_from':actual,'attribution':archive_origin,'source_page':cat['catalog_snapshot'],'note':'Исходный файл из архивного снимка; дата файла указана в ссылке на полученный файл и может отличаться от даты страницы каталога. В каталоге для разных локаций иногда используется общая иллюстрация; авторство не установлено.'};ok+=1
f.write_text(json.dumps(records,ensure_ascii=False,indent=2));(D/'zombicity-older-image-audit.json').write_text(json.dumps({'note':'Неудача не доказывает отсутствие изображения в архиве. При запросе ранней даты архив мог перенаправить на более поздний снимок.','success':ok,'failed':failed},ensure_ascii=False,indent=2));print('attempted',len(work),'added',ok,'failed',len(failed))

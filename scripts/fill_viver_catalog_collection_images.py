"""Match uniquely named collection records to the original images in ViveR's catalog."""
import requests,json,re,hashlib,concurrent.futures
from bs4 import BeautifulSoup
from urllib.parse import urljoin,urlparse
from pathlib import Path
P=Path(__file__).resolve().parents[1];f=P/'data/collections.json';a=json.loads(f.read_text()); catalog={}
def norm(s):return re.sub(r'[^а-яa-z0-9]+',' ',s.lower().replace('ё','е')).strip()
for n in range(1,4):
 u='https://viver.my1.ru/publ/collection/1'+('' if n==1 else '-'+str(n));r=requests.get(u,timeout=15);r.raise_for_status()
 for x in BeautifulSoup(r.content,'html.parser').select('a.inf_matblokmin_url'):
  t=x.select_one('.inf_matblokmin_txt');im=x.select_one('.inf_matblokmin_img');m=re.search(r'url\([\'\"]?([^\)\'\"]+)',im.get('style','')) if im else None
  if t and m:
   img=urljoin(u,m.group(1));key=norm(t.get_text(' ',strip=True));catalog.setdefault(key,[]).append((img,urljoin(u,x['href']),u,t.get_text(' ',strip=True)))
work=[]
for e in a:
 if e.get('image'):continue
 matches=catalog.get(norm(e['name']),[])
 if len(matches)==1 and urlparse(matches[0][0]).hostname=='viver.my1.ru':work.append((e['slug'],matches[0]))
def get(job):
 slug,(image,page,cat,label)=job
 try:
  r=requests.get(image,timeout=15);r.raise_for_status();b=r.content;ext='png' if b.startswith(b'\x89PNG\r\n\x1a\n') else 'gif' if b[:6] in (b'GIF87a',b'GIF89a') else 'jpg' if b[:3]==b'\xff\xd8\xff' else None
  return (job,b,ext) if ext else (job,None,None)
 except Exception:return (job,None,None)
index={e['slug']:e for e in a};hashes={hashlib.sha256(p.read_bytes()).hexdigest():p for p in (P/'img').rglob('*') if p.is_file()};ok=0
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
 for (slug,(image,page,cat,label)),b,ext in pool.map(get,work):
  if not b:continue
  h=hashlib.sha256(b).hexdigest()
  if h not in hashes:
   path=P/'img'/'collections'/f'{slug}-{h[:12]}.{ext}';path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(b);hashes[h]=path
  e=index[slug];e['image']={'path':str(hashes[h].relative_to(P)),'retrieved_from':image,'attribution':image,'source_page':cat,'note':f'Иллюстрация «{label}» из каталога ViveR_9, сопоставлена по точному названию; возможны отличия версий. Оригинальный файл без перекодирования; авторство отдельно не установлено.'}
  if not any(x.get('url')==cat for x in e['sources']):e['sources'].append({'url':cat,'label':'ViveR_9: изображение в каталоге коллекций; совпадение названия'})
  ok+=1
f.write_text(json.dumps(a,ensure_ascii=False,indent=2));print('matched',len(work),'images',ok,'remaining',sum(not x.get('image') for x in a))

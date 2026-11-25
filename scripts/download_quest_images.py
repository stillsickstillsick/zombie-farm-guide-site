"""Download a bounded batch of original quest illustrations. Failed addresses remain unmodified."""
import json,requests,hashlib,concurrent.futures
from pathlib import Path
P=Path(__file__).resolve().parents[1];F=P/'data/quests.json';items=json.loads(F.read_text());byurl={}
for e in items:
 if not e.get('image') and e.get('_image_candidate'):byurl.setdefault(e['_image_candidate'],[]).append(e)
urls=list(byurl)[:300]; hashes={hashlib.sha256(f.read_bytes()).hexdigest():f for f in (P/'img').rglob('*') if f.is_file()}
def download(u):
 try:
  r=requests.get(u,timeout=5);r.raise_for_status();b=r.content;ext='png' if b.startswith(b'\x89PNG\r\n\x1a\n') else 'jpg' if b[:3]==b'\xff\xd8\xff' else 'gif' if b[:6] in (b'GIF87a',b'GIF89a') else None;return u,b,ext
 except Exception:return u,None,None
ok=0;failure=0
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
 for u,b,ext in pool.map(download,urls):
  if ext:
   h=hashlib.sha256(b).hexdigest()
   if h not in hashes:
    f=P/'img/archive'/f'{byurl[u][0]["slug"]}-{h[:12]}.{ext}';f.write_bytes(b);hashes[h]=f
   for e in byurl[u]:e['image']={'path':str(hashes[h].relative_to(P)),'retrieved_from':u,'attribution':u,'source_page':e['sources'][0]['url'],'note':'Исходный файл из каталога задания; авторство изображения отдельно не установлено.'};e.pop('_image_candidate',None);ok+=1
  else:failure+=1
F.write_text(json.dumps(items,ensure_ascii=False,indent=2));print('urls',len(urls),'images added to cards',ok,'failed addresses skipped',failure,'pending cards',sum(bool(e.get('_image_candidate')) for e in items))

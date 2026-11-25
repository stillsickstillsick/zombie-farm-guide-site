#!/usr/bin/env python3
"""Resumable, rate-limited collection for manual review; never changes published site."""
from pathlib import Path
import json,time,hashlib,re,requests,urllib.parse,traceback,gzip,os
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
P=Path(__file__).resolve().parents[1]; out=P/'research/incoming';out.mkdir(parents=True,exist_ok=True); state=out/'island-queue.json';loc=json.loads((P/'data/locations.json').read_text()); queue=[]
for x in loc:
 if not x['slug'].startswith('zombicity-island-') or '/moy-island-' not in str(x.get('image','')):continue
 for src in x.get('sources',[]):
  m=re.search(r'https://zombicity\.info(/blog/[^?#]+)',src['url'])
  if m and 'ostrova_zombie' not in m.group(1):queue.append({'slug':x['slug'],'name':x['name'],'url':'https://zombie-island.moy.su'+m.group(1)});break
if state.exists():
 old=json.loads(state.read_text()); known={q['slug']:q for q in old['items']};queue=[known.get(q['slug'],q) for q in queue]+[q for q in old['items'] if q['slug'] not in {i['slug'] for i in queue}]
def save():
 tmp=state.with_suffix('.tmp');tmp.write_text(json.dumps({'items':queue},ensure_ascii=False,indent=2));tmp.replace(state)
def workspace_bytes():
 return sum(os.path.getsize(os.path.join(r,f)) for r,ds,fs in os.walk('/home/user') for f in fs if os.path.isfile(os.path.join(r,f)))
class StorageCap(Exception): pass
def request(u):
 r=requests.get(u,headers={'User-Agent':'Mozilla/5.0 (compatible; HistoricalResearch/1.0)'},timeout=(8,25));r.raise_for_status();return r
print('Queue:',len(queue),'items; manual review required.',flush=True)
for item in queue:
 if item.get('status')=='collected' or item.get('attempts',0)>=3:continue
 if workspace_bytes()>125.5*1024*1024:print('Workspace cap: pause for cleanup before retry.',flush=True);raise SystemExit(75)
 item['attempts']=item.get('attempts',0)+1; print('Reading:',item['name'],item['url'],'attempt',item['attempts'],flush=True);save()
 try:
  r=request(item['url']);s=BeautifulSoup(r.content,'html.parser');title=s.get_text(' ',strip=True)
  if item['name'].casefold().replace('ё','е') not in title.casefold().replace('ё','е'):raise ValueError('Название отсутствует на странице: требует ручной проверки')
  d=out/item['slug'];d.mkdir(exist_ok=True);packed=gzip.compress(r.content,compresslevel=9,mtime=0)
  if workspace_bytes()+len(packed)>126.5*1024*1024:raise StorageCap('workspace limit before page')
  (d/'source.html.gz').write_bytes(packed)
  candidates=[]
  for h in s.find_all(['h2','h3','h4']):
   text=h.get_text(' ',strip=True).lower()
   if 'фото' not in text or not ('остров' in text or 'локац' in text):continue
   for el in h.next_elements:
    if getattr(el,'name',None) in ['h2','h3','h4']:break
    if getattr(el,'name',None)=='img' and el.get('src'):
     original=urllib.parse.urljoin(r.url,el['src']);p=urllib.parse.urlsplit(original)
     if p.hostname and p.hostname.lower() in ('zombicity.info','www.zombicity.info'):fetch='https://zombie-island.moy.su'+p.path
     elif p.hostname and p.hostname.lower() in ('zombie-island.moy.su','pp.userapi.com'):fetch=original
     else:continue
     candidates.append({'heading':h.get_text(' ',strip=True),'original_url':original,'fetch_url':fetch})
  downloaded=[]
  for cand in candidates[:3]:
   try:
    res=request(cand['fetch_url']); b=res.content
    if len(b)>12*1024*1024:raise ValueError('image exceeds 12MB')
    ext='.jpg' if b.startswith(b'\xff\xd8\xff') else '.png' if b.startswith(b'\x89PNG\r\n\x1a\n') else None
    if not ext:raise ValueError('not PNG/JPEG')
    h=hashlib.sha256(b).hexdigest();f=d/(h+ext)
    if not f.exists() and workspace_bytes()+len(b)>126.5*1024*1024:raise StorageCap('workspace limit before image')
    f.write_bytes(b);downloaded.append(dict(cand,path=str(f.relative_to(P)),sha256=h,bytes=len(b)))
   except StorageCap:raise
   except Exception as e:downloaded.append(dict(cand,error=str(e)[:300]))
   time.sleep(1)
  item.update(status='collected',page_title=s.title.get_text(' ',strip=True) if s.title else '',page_saved=str((d/'source.html.gz').relative_to(P)),images=downloaded,note='Материал не опубликован; вручную проверить подпись, версию игры, комментарии HTML и соответствие хостов.')
  print('Collected',item['name'],'images',sum('path' in z for z in downloaded),flush=True)
 except StorageCap as e:
  item['attempts']-=1;item.update(status='retry',error=str(e));save();print('Paused:',e,flush=True);raise SystemExit(75)
 except Exception as e:item.update(status='retry',error=str(e)[:300]);print('Retry later:',item['name'],str(e)[:160],flush=True)
 save();time.sleep(3)
# Retried on subsequent pass; subprocess supervisor retries until 3 attempts or complete.
remaining=sum(1 for i in queue if i.get('status')!='collected' and i.get('attempts',0)<3)
print('Pass complete; remaining',remaining,flush=True);raise SystemExit(75 if remaining else 0)

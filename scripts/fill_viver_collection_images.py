"""Attach original collection illustrations from their already-cited ViveR article.
Only explicit first article illustration hosted on ViveR is fetched; no recompression.
"""
import concurrent.futures,hashlib,json,re
from pathlib import Path
from urllib.parse import urljoin,urlparse
import requests
from bs4 import BeautifulSoup
P=Path(__file__).resolve().parents[1]; f=P/'data/collections.json'; a=json.loads(f.read_text())
work=[]
for e in a:
 if e.get('image'): continue
 for s in e.get('sources',[]):
  u=s.get('url','')
  if 'viver.my1.ru/publ/' in u and re.search(r'/1-1-0-\d+',u): work.append((e['slug'],u));break

def get(job):
 slug,url=job
 try:
  r=requests.get(url,timeout=15);r.raise_for_status();s=BeautifulSoup(r.content,'html.parser')
  blocks=s.select('.inf_matblokmin_url');
  if not blocks:return (slug,url,None,None,'no article image')
  block=blocks[0];label=block.select_one('.inf_matblokmin_txt'); im=block.select_one('.inf_matblokmin_img');style=im.get('style','') if im else ''
  m=re.search(r'url\([\'\"]?([^\)\'\"]+)',style)
  if not m or not label:return (slug,url,None,None,'missing title or url')
  image=urljoin(r.url,m.group(1));host=urlparse(image).hostname
  if host!='viver.my1.ru':return (slug,url,None,None,'remote game server skipped')
  v=requests.get(image,timeout=15);v.raise_for_status();b=v.content
  ext='png' if b.startswith(b'\x89PNG\r\n\x1a\n') else 'gif' if b[:6] in (b'GIF87a',b'GIF89a') else 'jpg' if b[:3]==b'\xff\xd8\xff' else None
  if not ext:return (slug,url,None,None,'not a recognised image')
  return (slug,url,image,(b,ext,label.get_text(' ',strip=True)),None)
 except Exception as ex:return (slug,url,None,None,str(ex))
by={e['slug']:e for e in a}; hashes={hashlib.sha256(p.read_bytes()).hexdigest():p for p in (P/'img').rglob('*') if p.is_file()};ok=0;fails=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
 for slug,page,image,data,error in ex.map(get,work):
  if error:fails.append((slug,error));continue
  b,ext,label=data;h=hashlib.sha256(b).hexdigest()
  if h not in hashes:
   path=P/'img'/'collections'/f'{slug}-{h[:12]}.{ext}';path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(b);hashes[h]=path
  by[slug]['image']={'path':str(hashes[h].relative_to(P)),'retrieved_from':image,'attribution':image,'source_page':page,'note':f'Иллюстрация в отдельной статье ViveR_9 «{label}»; исходный файл без перекодирования. Авторство отдельно не установлено.'};ok+=1
f.write_text(json.dumps(a,ensure_ascii=False,indent=2));print('found',ok,'failed',len(fails),fails)

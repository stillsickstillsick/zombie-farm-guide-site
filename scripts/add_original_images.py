"""Collect original image bytes from explicitly labelled browser-game pages, preserving source attribution."""
import json,requests,bs4,re,hashlib,concurrent.futures
from pathlib import Path
from urllib.parse import urljoin,urlsplit,urlunsplit
P=Path(__file__).resolve().parents[1]; files=['materials','buildings','collections','quests','locations','plants'];D={c:json.loads((P/'data'/f'{c}.json').read_text()) for c in files}
hashes={hashlib.sha256(f.read_bytes()).hexdigest():f for f in (P/'img').rglob('*') if f.is_file()}
def norm(s):return re.sub(r'\s+',' ',s.casefold().replace('ё','е')).strip()
def exact_image(url):
 u=urlsplit(url)
 if u.hostname in ('zombicity.info','www.zombicity.info'):return urlunsplit(('https','zombie-island.moy.su',u.path,u.query,''))
 return url.replace('http://zombie-island.moy.su','https://zombie-island.moy.su')
def fetch(u):
 try:
  r=requests.get(u,timeout=12);r.raise_for_status();raw=r.content
  ext='png' if raw.startswith(b'\x89PNG\r\n\x1a\n') else 'jpg' if raw[:3]==b'\xff\xd8\xff' else 'gif' if raw[:6] in (b'GIF87a',b'GIF89a') else 'webp' if raw[:4]==b'RIFF' and raw[8:12]==b'WEBP' else None
  return raw,ext
 except:return None,None
def store(raw,ext,slug):
 h=hashlib.sha256(raw).hexdigest()
 if h not in hashes:
  p=P/'img/archive'/f'{slug}-{h[:12]}.{ext}';p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);hashes[h]=p
 return str(hashes[h].relative_to(P))
# Repair unavailable original hosts by requesting the exact same asset path from the known mirror.
jobs=[]
for x in D['collections']:
 for g in x.get('gallery',[]):
  if not g.get('image'):
   original=g['url'];mirror=exact_image(original)
   if mirror!=original:jobs.append((x,g,original,mirror))
result=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
 for job,(raw,ext) in zip(jobs,ex.map(lambda z:fetch(z[3]),jobs)):
  x,g,original,mirror=job
  if raw and ext:g['image']={'path':store(raw,ext,x['slug']),'retrieved_from':mirror,'attribution':original,'note':'Файл с зеркала; побайтовое соответствие оригиналу не проверено.'};result.append(g)
print('gallery recovered',len(result),'of',len(jobs))
# Verified browser articles with material thumbnails. Select only exact title and Material alt text.
pages=['https://zombie-island.moy.su/blog/zombie_farm_majak/2012-07-18-196','https://zombie-island.moy.su/blog/zombie_farm_universitet/2012-07-18-239','https://zombie-island.moy.su/blog/zombie_farm_sklep/2012-07-18-230','https://zombie-island.moy.su/blog/zombie_farm_belyj_dom/2012-07-18-155','https://zombie-island.moy.su/blog/zombie_farm_shkola/2012-07-18-270','https://zombie-island.moy.su/blog/zombi_ferma_metall/2012-07-17-55','https://zombie-island.moy.su/blog/zombie_farm_most/2012-07-18-199','https://zombie-island.moy.su/blog/zombi_ferma_gvozdi/2012-07-17-19']
for x in D['buildings']+D['plants']:
 if not x.get('image'):
  pages += [s['url'].replace('http://zombicity.info','https://zombie-island.moy.su').replace('https://zombicity.info','https://zombie-island.moy.su') for s in x.get('sources',[]) if 'zombie-island.moy.su/blog/' in s.get('url','') or 'zombicity.info/blog/' in s.get('url','')]
pages += ['https://zombie-island.moy.su/blog/stal_zombi_ferma/2012-07-18-141','https://zombie-island.moy.su/blog/zombi_ferma_kuvalda/2012-07-17-48','https://zombie-island.moy.su/blog/zombi_ferma_cement/2012-07-18-95','https://zombie-island.moy.su/blog/zombie_farm_big_ben/2012-08-01-426']
pages += ['https://zombie-island.moy.su/blog/zombie_farm_dzhoker/2012-07-18-170','https://zombie-island.moy.su/blog/zombi_ferma_bumaga/2012-07-17-11','https://zombie-island.moy.su/blog/zombie_farm_japonskij_khram/2012-07-18-274','https://zombie-island.moy.su/blog/khrustalnyj_zombie_farm/2012-08-14-885','https://zombie-island.moy.su/blog/zombi_ferma_ugol/2012-07-18-90','https://zombi-mania.at.ua/index/drugie_materialy/0-13']
pages=list(dict.fromkeys(pages));candidates={}
def parse(page):
 try:
  r=requests.get(page,timeout=12);r.raise_for_status();return page,bs4.BeautifulSoup(r.content,'html.parser')
 except:return page,None
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
 for page,s in ex.map(parse,pages):
  if s is None:continue
  for im in s.select('img[src][alt]'):
   title=im.get('title','').strip();alt=im.get('alt','');
   if not title:continue
   match=re.match(r'^(Материал|Постройка|Рецепт|Урожай)\s+(.+?)\s+игры Зомби Ферма',alt,re.I)
   if not match or norm(match.group(2))!=norm(title):continue
   key=(norm(match.group(1)),norm(title));original=urljoin(page,im['src']);candidates.setdefault(key,(original,page))
alias={'канат':'канаты','жёлтая краска':'желтая краска','брёвна':'бревна','кирпичи':'кирпичи','эйфелева башня':'эйфелевая'}
requests_list=[]
for cat in ('materials','buildings','plants'):
 for x in D[cat]:
  if x.get('image'):continue
  name=norm(alias.get(norm(x['name']),x['name']));types={'materials':['материал'],'buildings':['постройка'],'plants':['рецепт','урожай']}[cat]
  for typ in types:
   if (typ,name) in candidates:
    u,page=candidates[(typ,name)];requests_list.append((cat,x,u,page,exact_image(u)));break
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
 for (cat,x,original,page,mirror),(raw,ext) in zip(requests_list,ex.map(lambda z:fetch(z[4]),requests_list)):
  if raw and ext:
   x['image']={'path':store(raw,ext,x['slug']),'retrieved_from':mirror,'attribution':original,'note':'Изображение подписано на странице-источнике; файл получен с зеркала. Совпадение с оригиналом не проверено.','source_page':page}
   print('asset',cat,x['name'],page)
for c in files:(P/'data'/f'{c}.json').write_text(json.dumps(D[c],ensure_ascii=False,indent=2))
print('searched pages',len(pages),'candidates',len(candidates),'new object images',sum(bool(x.get('image')) for _,x,*_ in requests_list))

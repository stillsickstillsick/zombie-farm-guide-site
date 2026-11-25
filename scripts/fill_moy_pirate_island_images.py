import requests,json,re,hashlib
from pathlib import Path
from urllib.parse import urljoin,urlparse
from bs4 import BeautifulSoup
P=Path(__file__).resolve().parents[1];f=P/'data/locations.json';records=json.loads(f.read_text());page='https://zombie-island.moy.su/blog/piraty_zombie_farm_kak_stat_piratom/2013-10-30-2293';r=requests.get(page,timeout=20);r.raise_for_status();s=BeautifulSoup(r.content,'html.parser');hashes={hashlib.sha256(x.read_bytes()).hexdigest():x for x in (P/'img').rglob('*') if x.is_file()};out=[]
for e in records:
 if e.get('image') or not e.get('slug','').startswith('zombicity-island-'):continue
 id=e['slug'].removeprefix('zombicity-island-');a=s.find('a',href=re.compile('-'+re.escape(id)+r'(?:$|[?#])'))
 if not a or not a.find('img',src=True):continue
 img=a.find('img');label=img.get('title') or img.get('alt','');name=e['name'];
 if name.casefold() not in label.casefold():continue
 listed=urljoin(page,img['src']);u=urlparse(listed);download=('https://zombie-island.moy.su'+u.path+('?' + u.query if u.query else '')) if u.hostname=='zombicity.info' else listed
 try:
  r=requests.get(download,timeout=15);r.raise_for_status();b=r.content;ext='png' if b.startswith(b'\x89PNG\r\n\x1a\n') else 'jpg' if b.startswith(b'\xff\xd8\xff') else 'gif' if b[:6] in (b'GIF87a',b'GIF89a') else None
  if not ext:continue
  h=hashlib.sha256(b).hexdigest()
  if h not in hashes:
   p=P/'img'/'locations'/f'moy-pirate-{id}-{h[:12]}.{ext}';p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b);hashes[h]=p
  e['image']={'path':str(hashes[h].relative_to(P)),'retrieved_from':r.url,'attribution':download,'source_page':page,'note':'Иллюстрация из обзора пиратских островов; сопоставлены идентификатор статьи и подпись. Некоторые острова в источнике используют одинаковую картинку — не обязательно карта конкретного острова. При ссылке на zombicity.info получен файл по тому же пути с moy.su; идентичность не проверена.'}
  e.setdefault('sources',[]).append({'url':page,'label':'Zombie-island.moy.su — обзор пиратских островов и иллюстрация'});out.append({'id':id,'name':name,'listed':listed,'retrieved':r.url,'hash':h})
 except requests.RequestException as ex:print('failed',name,str(ex)[:80])
f.write_text(json.dumps(records,ensure_ascii=False,indent=2));(P/'data/moy-pirate-island-image-audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print('added',len(out),[v['name'] for v in out])

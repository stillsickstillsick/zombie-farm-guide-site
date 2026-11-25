"""Curated named images on individual ZOMBIA material pages; no inference from wrong alt text."""
import json,requests,hashlib,concurrent.futures
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urljoin,urlparse
P=Path(__file__).resolve().parents[1];f=P/'data/materials.json';items=json.loads(f.read_text());paths={'mramor':'/material/kamen/Mramor.png','zub-drakona':'/material/zub-drakona.png','bozon-khiggsa':'/material/bozon.png','meteorit':'/material/meteor.png','lunnyy-kamen':'/material/lunniy.png','zombi-oskar':'/material/oscar.png','prostynya':'/material/prostinya.png','kinolenta':'/material/kinolenta.png','tsirkovoy-shar':'/material/circovoy_shar.png','ognennyy-obruch':'/material/obruch.png','lestnitsa':'/material/lestnica.png','bigudi':'/material/bigudi.png','fantik':'/material/NY/Fantik.jpg','palochki':'/material/NY/palochki.jpg','drevniy-sunduk':'/material/sunduki/01_drevniy_sunduk.jpg','skazochnyy-sunduk':'/material/sunduki/02_skazochniy_sunduk.jpg','krutoy-sunduk':'/material/sunduki/03_krutoy_sunduk.jpg','fantasticheskiy-sunduk':'/material/sunduki/04_fantasticheskiy.jpg','nosok-zombi':'/material/NY/nosok.jpg','polyarnyy-nosok':'/material/NY/polarniy_nosok.jpg','skakalka':'/material/school/skakalka.png','chyortova-boksyorskaya':'/material/NY/chertova_bokserskaya.jpg','belyy-mramor':'/material/kamen/belyj-mramor.png','sakharnaya-vata':'/material/sakharnaja_vata.png','emchu-ina':'/material/zhemchuzhina.png','babochka':'/material/babochka.png','veer':'/material/veer.png'}
hashes={hashlib.sha256(x.read_bytes()).hexdigest():x for x in (P/'img').rglob('*') if x.is_file()}
def work(e):
 path=paths[e['slug']];page=next((s['url'] for s in e['sources'] if 'zombi.at.ua/board/materialy/' in s['url']),None)
 try:
  if not page:raise ValueError('no source page')
  r=requests.get(page,timeout=15);r.raise_for_status();s=BeautifulSoup(r.content,'html.parser');matches=[urljoin(page,i['src']) for i in s.find_all('img',src=True) if urlparse(urljoin(page,i['src'])).path==path]
  if not matches:raise ValueError('image path not present in page')
  listed=matches[0];u=urlparse(listed);actual='https://zombi.at.ua'+path if u.hostname in ['zombia.ru','www.zombia.ru'] else listed
  r=requests.get(actual,timeout=15);r.raise_for_status();b=r.content;ext='png' if b.startswith(b'\x89PNG\r\n\x1a\n') else 'jpg' if b.startswith(b'\xff\xd8\xff') else 'gif' if b[:6] in (b'GIF87a',b'GIF89a') else None
  if not ext:raise ValueError('not recognized image')
  return e,b,ext,r.url,page,listed,None
 except Exception as ex:return e,None,None,None,page,None,str(ex)[:130]
results=[];failed=[];jobs=[e for e in items if not e.get('image') and e['slug'] in paths]
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
 for e,b,ext,url,page,listed,err in pool.map(work,jobs):
  if not b:failed.append((e['name'],err));continue
  h=hashlib.sha256(b).hexdigest()
  if h not in hashes:
   p=P/'img'/'materials'/f'zombia-{e["slug"]}-{h[:12]}.{ext}';p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b);hashes[h]=p
  extra=' Для недоступного домена zombia.ru взят файл по тому же пути на zombi.at.ua; побайтовая идентичность не проверена.' if urlparse(listed).hostname in ('zombia.ru','www.zombia.ru') else ''
  e['image']={'path':str(hashes[h].relative_to(P)),'retrieved_from':url,'attribution':url,'source_page':page,'note':'Иллюстрация найдена на отдельной странице материала ZOMBIA; некоторые alt-подписи источника ошибочны, сопоставление по странице и имени файла.'+extra};results.append(e['name'])
f.write_text(json.dumps(items,ensure_ascii=False,indent=2));(P/'data/zombia-material-images-audit.json').write_text(json.dumps({'added':results,'failed':failed},ensure_ascii=False,indent=2));print('added',len(results),results,'failed',failed)

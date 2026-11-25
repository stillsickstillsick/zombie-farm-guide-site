from pathlib import Path
from io import BytesIO
import hashlib,json,requests
from PIL import Image
P=Path(__file__).resolve().parents[1];p=P/'data/plants.json';data=json.loads(p.read_text());by={x['slug']:x for x in data};hashes={}
for f in (P/'img').rglob('*'):
 if f.is_file():hashes.setdefault(hashlib.sha256(f.read_bytes()).hexdigest(),str(f.relative_to(P)))
for slug,num in [('ogurec-zvezdnyy-urozhay','944567420'),('shesteren-urozhay','402651205'),('ventilyutiki','695804028'),('kolrabi','655493377'),('svetiki','967685214')]:
 x=by[slug];u=f'https://zombie-island.moy.su/_ph/9/2/{num}.png';g=x.setdefault('gallery',[])
 if any(y.get('url')==u for y in g):continue
 r=requests.get(u,timeout=20);r.raise_for_status();Image.open(BytesIO(r.content)).verify();h=hashlib.sha256(r.content).hexdigest();path=hashes.get(h)
 if not path:path=f'img/archive/seed-{slug}-{h[:12]}.png';(P/path).write_bytes(r.content);hashes[h]=path
 g.append({'name':'Семена: '+x['name'],'url':u,'image':{'path':path,'retrieved_from':u,'attribution':u,'source_page':x['sources'][0]['url'],'note':'Пиктограмма семян по подписи статьи; файл получен без перекодирования. Для изображений, ссылающихся на zombicity.info, идентичность на другом хосте не проверена.'}})
p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')

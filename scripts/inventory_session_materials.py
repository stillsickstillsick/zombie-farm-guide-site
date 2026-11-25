#!/usr/bin/env python3
"""Inventory and structural analysis of the private raw session materials, without asserting historical accuracy."""
import pathlib,json,hashlib,collections,re,datetime
from bs4 import BeautifulSoup
from PIL import Image
P=pathlib.Path(__file__).resolve().parents[1]; root=P/'research/session-materials'; entries=[]; errors=[]; counts=collections.Counter()
for f in sorted(root.rglob('*')):
 if not f.is_file() or f.name in ('inventory.json','inventory-summary.md'):continue
 b=f.read_bytes();r={'path':str(f.relative_to(root)),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}; ext=f.suffix.lower();counts[ext or '[без расширения]']+=1
 if ext=='.html':
  s=BeautifulSoup(b,'html.parser');h=s.find('h1');title=s.title
  r.update(title=title.get_text(' ',strip=True) if title else '',heading=h.get_text(' ',strip=True) if h else '',quest_structure=bool(s.select_one('.kvest_ind') or (h and h.find_parent('table') and 'Задание:' in h.find_parent('table').get_text(' ',strip=True))),image_tags=len(s.find_all('img')),links=len(s.find_all('a',href=True)))
  if not r['title'] or not h:errors.append({'path':r['path'],'issue':'нет title или h1 — содержание требует ручной проверки'})
 elif ext in ('.jpg','.jpeg','.png','.gif','.webp'):
  try:
   with Image.open(f) as im:r.update(format=im.format,width=im.width,height=im.height);im.verify()
  except Exception as e:errors.append({'path':r['path'],'issue':'ошибка декодирования изображения: '+str(e)[:160]})
 elif ext in ('.json','.jsonl'):
  try:
   if ext=='.json':json.loads(b)
   else:
    for line in b.splitlines():json.loads(line)
  except Exception as e:errors.append({'path':r['path'],'issue':'ошибка JSON: '+str(e)[:160]})
 entries.append(r)
manifest={'version':1,'generated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'research/session-materials, кроме самого манифеста и сводки','note':'Инвентаризация и структурный анализ; не является содержательной проверкой каждой статьи. HTML и изображения сохранены как получены, авторство и независимость источников не подтверждены. Остров Фанатов сохраняется только в приватном разделе research.','files':entries,'warnings':errors}
(root/'inventory.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
html=[r for r in entries if r['path'].endswith('.html')];pages=sum(r.get('quest_structure',False) for r in html);dupes=collections.Counter(r['sha256'] for r in entries);summary=['# Инвентаризация материалов сессии','','Файлов: '+str(len(entries)),'HTML-страниц: '+str(len(html)),'Страниц с распознаваемой структурой задания: '+str(pages),'Файлов изображений: '+str(sum(counts[e] for e in ('.jpg','.jpeg','.png','.gif','.webp'))),'Предупреждений структуры/декодирования: '+str(len(errors)),'Повторяющихся SHA-256 групп: '+str(sum(v>1 for v in dupes.values())),'','Полный список путей, размеров, SHA-256 и структурных характеристик — inventory.json. Инвентаризация не заменяет ручную историческую проверку каждого источника. Сырой материал оставлен для последующего содержательного анализа; страницы могут быть зеркалами или поздними правками. Остров Фанатов и результаты поиска находятся только в приватном разделе research, который исключён из публичного сайта.','']
(root/'inventory-summary.md').write_text('\n'.join(summary));print('\n'.join(summary));print('Предупреждения:',errors[:8])

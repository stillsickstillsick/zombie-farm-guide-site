#!/usr/bin/env python3
"""Проверка сайта без сети. Ничего не изменяет и не удаляет."""
import hashlib,json
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote,urlsplit
P=Path(__file__).resolve().parents[1]
missing=[];external=[];image_refs=set();pages=0
class Scan(HTMLParser):
 def __init__(self,path): super().__init__(convert_charrefs=True);self.path=path
 def handle_starttag(self,tag,attrs):
  if tag not in ('a','img','script','link'):return
  v=dict(attrs).get('href' if tag in ('a','link') else 'src') or ''
  if not v or v.startswith('#'):return
  u=urlsplit(v)
  if u.scheme in ('mailto','tel','data','javascript'):return
  if u.scheme or u.netloc:
   if tag!='a':external.append((self.path.relative_to(P),v))
  elif u.path and not (self.path.parent / unquote(u.path)).resolve().exists():missing.append((self.path.relative_to(P),v))
def collect(o):
 if isinstance(o,dict):
  p=o.get('path')
  if isinstance(p,str) and p.startswith('img/'):image_refs.add(p)
  for x in o.values():collect(x)
 elif isinstance(o,list):
  for x in o:collect(x)
for f in (P/'data').glob('*.json'):
 try:collect(json.loads(f.read_text(encoding='utf-8')))
 except (OSError,ValueError) as e:raise SystemExit(f'Ошибка данных {f}: {e}')
for f in P.rglob('*.html'):
 if f.is_relative_to(P/'research'):continue # Saved source pages are evidence, not site pages.
 parser=Scan(f);parser.feed(f.read_text(encoding='utf-8'));pages+=1
hashes=defaultdict(list);images=set()
for f in (P/'img').rglob('*'):
 if f.is_file():
  rel=str(f.relative_to(P));images.add(rel);hashes[hashlib.sha256(f.read_bytes()).hexdigest()].append(rel)
duplicates=[xs for xs in hashes.values() if len(xs)>1];unused=sorted(images-image_refs)
print(f'HTML: {pages}; битые ссылки: {len(missing)}; внешние загружаемые ресурсы: {len(external)}')
print(f'Изображения: {len(images)}; побайтовые дубли: {sum(len(x)-1 for x in duplicates)}; не упомянуты в JSON: {len(unused)}')
for name,rows in [('Битая ссылка',missing),('Внешний ресурс',external),('Дубликат',duplicates),('Не упомянуто',unused)]:
 for row in rows:print(name, row)
print('Неупомянутые файлы не обязательно лишние: они могут сохранять исследовательские материалы.')
raise SystemExit(1 if missing or external else 0)

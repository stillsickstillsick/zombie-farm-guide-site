#!/usr/bin/env python3
"""ZF.3dn building catalogue: exact unique names, retain image file labels as placeholders."""
import concurrent.futures,json,re,requests,bs4
from pathlib import Path
from urllib.parse import urljoin,urlparse,unquote
P=Path(__file__).resolve().parents[1];path=P/'data/buildings.json';data=json.loads(path.read_text());normal=lambda s:s.casefold().replace('ё','е').strip();by={}
for x in data:by.setdefault(normal(x['name']),[]).append(x)
urls=['https://zf.3dn.ru/publ/postrojki/1'+('-'+str(n) if n>1 else '') for n in range(1,14)]
def catalog(u):
 try:
  r=requests.get(u,timeout=20);r.raise_for_status();s=bs4.BeautifulSoup(r.content,'html.parser');rows=[(h.get_text(' ',strip=True),urljoin(u,h['href'])) for h in s.select('h1 a')];return u,rows,''
 except Exception as e:return u,[],str(e)[:160]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:pages=list(ex.map(catalog,urls))
rows=[]
for u,entries,err in pages:
 print('catalog',u,len(entries),err);rows.extend(entries)
if len(rows)!=121 or len({u for _,u in rows})!=121:raise RuntimeError('Incomplete or duplicate catalogue; no data modified')
todo=[];skipped=[]
for name,u in rows:
 hits=by.get(normal(name),[])
 if len(hits)==1:todo.append((name,u,hits[0]['slug']))
 else:skipped.append((name,u))
def fetch(row):
 name,u,slug=row
 try:
  r=requests.get(u,timeout=20);r.raise_for_status();s=bs4.BeautifulSoup(r.content,'html.parser');e=s.select_one('td.eText')
  if not e:return row,'','','нет eText'
  for tag in e(['script','style']):tag.decompose()
  for im in e.find_all('img'):
   src=im.get('src','');alt=im.get('alt','').strip();file=unquote(Path(urlparse(src).path).name);im.replace_with('[изображение: '+(alt+'; ' if alt else '')+file+']')
  txt=e.get_text('\n',strip=True);txt=re.sub(r'\n{3,}','\n\n',txt)
  dt=re.search(r'\(\d{2}\.\d{2}\.\d{4}\)',s.get_text(' ',strip=True));date=dt.group()[1:-1] if dt else 'дата публикации не найдена'
  if not txt or len(txt)>25000:return row,'',date,'empty or oversized'
  return row,txt,date,''
 except Exception as e:return row,'','',str(e)[:160]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:out=list(ex.map(fetch,todo))
lookup={x['slug']:x for x in data};count=0;failed=[]
for (name,u,slug),txt,date,err in out:
 if err:failed.append({'name':name,'url':u,'error':err});continue
 x=lookup[slug];rid='zf3dn-building-'+slug;rec={'original_id':rid,'original_category':'Постройки','version':'историческая браузерная игра, площадка не указана','date':date+' — дата публикации; дата редакции неизвестна','fields':{'Текст и пиктограммы источника':txt},'confidence':'Сопоставлено по единственному точному названию; различные версии или одноимённые объекты могут различаться. Названия файлов и alt пиктограмм сохранены как подписи, не заменяют проверенную расшифровку; изображения и цены требуют ручной сверки. Независимость от zombi-ferma.ru и других сайтов не установлена.'}
 if not any(z['url']==u for z in x['sources']):x['sources'].append({'url':u,'label':'ZF.3dn: историческая карточка постройки'})
 x.setdefault('prior_records',[]);x['prior_records']=[r for r in x['prior_records'] if r.get('original_id')!=rid]+[rec];count+=1
path.write_text(json.dumps(data,ensure_ascii=False,indent=2));report={'catalog_pages':13,'catalog_entries':len(rows),'matched':count,'unmatched':[{'name':n,'url':u} for n,u in skipped],'failed':failed,'note':'Совпадение только по имени; пиктограммы не расшифрованы; обход остальных разделов и сайтов не завершён.'};(P/'data/zf3dn-buildings-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))

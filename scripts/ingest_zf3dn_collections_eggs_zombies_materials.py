#!/usr/bin/env python3
"""Read remaining four ZF categories. Match uniquely; retain unresolved pages in audit."""
import concurrent.futures,json,re,requests,bs4,collections,sys
from pathlib import Path
from urllib.parse import unquote,urlparse
P=Path(__file__).resolve().parents[1];inventory=json.loads((P/'data/zf3dn-catalog-inventory.json').read_text());assert inventory['pages_checked']==57 and not inventory['failed_pages'] and len(inventory['entries'])==562
files=['materials','eggs-trophies','collections','zombies','buildings'];datasets={k:json.loads((P/'data'/f'{k}.json').read_text()) for k in files};normal=lambda s:re.sub(r'\s+',' ',s.casefold().replace('ё','е').strip());maps={}
for cid,kinds in [(7,['materials','eggs-trophies']),(2,['collections']),(4,['zombies','buildings']),(9,['eggs-trophies'])]:
 d=collections.defaultdict(list)
 for kind in kinds:
  for e in datasets[kind]:
   n=e['name'];n=re.sub(r'\s*\(яйцо\)$','',n,flags=re.I) if cid==9 else n;d[normal(n)].append((kind,e))
 maps[cid]=d
rows=[x for x in inventory['entries'] if x['category_id'] in maps];assert len(rows)==346,len(rows)
part=int(sys.argv[1]) if len(sys.argv)>1 else 0
assert 0 <= part <= 6
rows=rows[part*50:(part+1)*50]
print('Processing batch',part,'pages',len(rows),flush=True)
def fetch(row):
 try:
  r=requests.get(row['url'],timeout=(4,8));r.raise_for_status();s=bs4.BeautifulSoup(r.content,'html.parser');node=s.select_one('td.eText')
  if not node:return row,'','','отсутствует eText'
  for tag in node(['script','style']):tag.decompose()
  for im in node.find_all('img'):
   src=im.get('src','');alt=im.get('alt','').strip();fname=unquote(Path(urlparse(src).path).name);im.replace_with('[изображение: '+(alt+'; ' if alt else '')+fname+']')
  text=node.get_text('\n',strip=True);text=re.sub(r'\n{3,}','\n\n',text)
  dt=re.search(r'\(\d{2}\.\d{2}\.\d{4}\)',s.get_text(' ',strip=True));date=dt.group()[1:-1] if dt else 'дата не найдена'
  if not text or len(text)>25000:return row,'',date,'пустая или слишком длинная статья'
  return row,text,date,''
 except Exception as e:return row,'','','ошибка '+str(e)[:180]
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:results=list(ex.map(fetch,rows))
unmatched=[];failed=[];counts=collections.Counter();matched_slugs=collections.defaultdict(set)
for row,txt,date,err in results:
 if err:failed.append({**row,'error':err});continue
 cid=row['category_id'];hits=maps[cid].get(normal(row['name']),[])
 if len(hits)!=1:
  unmatched.append({**row,'date':date,'text':txt,'reason':'нет точного уникального соответствия' if not hits else 'неоднозначное совпадение'});continue
 kind,e=hits[0];article_id=re.search(r'-(\d+)$',row['url']).group(1);rid='zf3dn-'+str(cid)+'-'+article_id
 rec={'original_id':rid,'original_category':{2:'Коллекции',4:'Зомби',7:'Материалы и предметы',9:'Яйца'}[cid],'version':'историческая браузерная игра; площадка не указана','date':date+' — дата публикации, дата редакции неизвестна','fields':{'Текст и пиктограммы источника':txt},'confidence':'Сопоставление по единственному точному названию в данной категории, варианты одной сущности и одноимённые объекты требуют проверки. Значения из пиктограмм не расшифрованы: alt и имена файлов могут содержать ошибки. Это фанатский источник; зависимость от zombi-ferma.ru и других сайтов не установлена.'}
 if not any(x['url']==row['url'] for x in e['sources']):e['sources'].append({'url':row['url'],'label':'ZF.3dn: историческая карточка'})
 e.setdefault('prior_records',[]);e['prior_records']=[v for v in e['prior_records'] if v.get('original_id')!=rid]+[rec];counts[str(cid)]+=1;matched_slugs[str(cid)].add(e['slug'])
for kind,arr in datasets.items():(P/'data'/f'{kind}.json').write_text(json.dumps(arr,ensure_ascii=False,indent=2))
audit={'read_pages':len(rows),'matched_article_counts':dict(counts),'matched_distinct_cards':{k:len(v) for k,v in matched_slugs.items()},'failed':failed,'unmatched':unmatched,'note':'Исходные описания несопоставленных страниц для дальнейшей ручной проверки; наличие записей не означает ручную сверку каждой пиктограммы или завершение всех источников.'}
(P/'data'/f'zf3dn-other-categories-audit-{part}.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2));print('matched pages',dict(counts),'unique cards',{k:len(v) for k,v in matched_slugs.items()},'unmatched',len(unmatched),'failed',len(failed));print('failed',failed[:20])

"""Incrementally read ZOMBIA quest listings. Failed pages are skipped and recorded; no fabricated data."""
import json,re,requests,bs4,concurrent.futures,hashlib
from pathlib import Path
from urllib.parse import urljoin
P=Path(__file__).resolve().parents[1];F=P/'data/quests.json';items=json.loads(F.read_text());base='https://zombi.at.ua/board/menju/zadanija/21'
byid={r['original_id']:e for e in items for r in e.get('prior_records',[]) if r.get('original_id','').startswith('zombia-quest-')};slugs={e['slug'] for e in items}
tr=str.maketrans(dict(zip('абвгдеёзийклмнопрстуфхцчшщъыьэюя',['a','b','v','g','d','e','yo','z','i','y','k','l','m','n','o','p','r','s','t','u','f','kh','ts','ch','sh','shch','','y','','e','yu','ya'])))
def slug(s):return re.sub(r'[^a-z0-9]+','-',s.lower().translate(tr)).strip('-') or 'kvest'
def page(i):
 url=base+(('-'+str(i)) if i>1 else '')
 try:
  res=requests.get(url,timeout=8);res.raise_for_status();s=bs4.BeautifulSoup(res.content,'html.parser');entries=[]
  for title in s.select('.eTitle'):
   a=title.find('a',href=True);td=title.parent
   if not a or not td:continue
   match=re.search(r'/21-1-0-(\d+)',a['href']);
   if not match:continue
   name=a.get_text(' ',strip=True).replace('(Кликнуть, чтобы прокомментировать)','').strip();urlitem=urljoin(url,a['href']);qid=match.group(1);im=td.find('img',src=True);image=urljoin(url,im['src']) if im else None
   title.decompose()
   for z in td.select('script,style,ins'):z.decompose()
   raw=td.get_text('\n',strip=True);raw=re.sub(r'\n{3,}','\n\n',raw)
   if not raw:continue
   entries.append({'id':qid,'name':name,'raw':raw,'url':urlitem,'listing':url,'image':image})
  if not entries:return i,[],f'нет извлечённых карточек: {url}'
  return i,entries,None
 except Exception as e:return i,[],str(e)[:220]
results=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 for result in pool.map(page,range(1,73)):results.append(result)
errors=[{'page':i,'error':err} for i,arr,err in results if err];entries={e['id']:e for i,arr,err in results for e in arr};new=0
for qid,r in entries.items():
 rid='zombia-quest-'+qid;e=byid.get(rid)
 if not e:
  sp=slug(r['name']);sp=sp if sp not in slugs else sp+'-'+qid;slugs.add(sp);e={'slug':sp,'name':r['name'],'category':'quests','type':'Квест или линейка','purchase':'нет данных','sale':'нет данных','obtain':'нет данных','use':'нет данных','features':'нет данных','versions':'ВКонтакте; дата публикации и редакции не установлена','sources':[],'image':None,'links':[],'event':'нет данных','original_category':'Квесты'};items.append(e);byid[rid]=e;new+=1
 if not any(x.get('original_id')==rid for x in e.get('prior_records',[])):
  e.setdefault('prior_records',[]).append({'original_id':rid,'original_category':'Квесты','version':'ВКонтакте, ZOMBIA','date':'дата публикации и редакции не установлена','fields':{'Текст карточки на странице каталога':r['raw']},'confidence':'Содержимое списка; цели, диалоги и награды приведены в том виде, как опубликованы. Отдельная страница не обязательно проверена. Версия и дата требуют сверки.'})
  e['sources'].append({'url':r['listing'],'label':'ZOMBIA: прочитан текст карточки в каталоге'});e['sources'].append({'url':r['url'],'label':'Адрес отдельной карточки, прочитан в каталоге; отдельный доступ не проверен'})
 if not e.get('image') and r['image']:e['_image_candidate']=r['image']
F.write_text(json.dumps(items,ensure_ascii=False,indent=2));(P/'data/zombia-quest-audit.json').write_text(json.dumps({'catalog':base,'pages_requested':72,'pages_read':72-len(errors),'failed_pages':errors,'unique_listed_quests':len(entries),'new_records':new},ensure_ascii=False,indent=2));print('pages',72-len(errors),'failed',len(errors),'entries',len(entries),'new',new,'candidates',sum(bool(x.get('_image_candidate')) for x in items))

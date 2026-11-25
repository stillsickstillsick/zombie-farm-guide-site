"""Crawl bounded related-answer graph; save a checkpoint after each completed batch."""
import requests,bs4,json,re,concurrent.futures
from urllib.parse import urljoin,unquote
from pathlib import Path
from collections import deque
P=Path(__file__).resolve().parents[1];F=P/'data/fatalgame-catalog.json';seed='https://www.fatalgame.com/answer/zombiferma/собрать-автомобильную-коллекцию-в-игре-зомби-ферма';d=json.loads(F.read_text()) if F.exists() else {'pages':[],'failed':[]};pages={x['url']:x for x in d['pages']};failed={x['url'] for x in d['failed']};seen=set(pages)|failed;queue=deque([seed])
for p in pages.values():queue.extend(p.get('related',[]))
def get(u):
 try:
  q=requests.get(u,timeout=6);q.raise_for_status();s=bs4.BeautifulSoup(q.content,'html.parser');root=next((x for x in s.select('.post-inner') if x.find('h1') and x.select_one('.entry')),None);entry=root.select_one('.entry') if root else None;h=root.find('h1') if root else None
  if not (h and entry):return {'url':u,'error':'Нет тела ответа'}
  text=entry.get_text(' ',strip=True);raw=root.get_text(' ',strip=True);date=re.search(r'\b\d{2}/\d{2}/\d{4}\b',raw);links=[]
  for a in root.select('.answers-col a[href]'):
   v=unquote(urljoin(u,a['href'])).split('#')[0]
   if '/answer/zombiferma/' in v and 'коллекц' in v and v not in links:links.append(v)
  return {'url':u,'title':h.get_text(' ',strip=True),'date_as_published':date.group() if date else 'не установлена','answer':text,'related':links}
 except Exception as e:return {'url':u,'error':str(e)[:180]}
for batchno in range(20):
 batch=[]
 while queue and len(batch)<8 and len(seen)<120:
  u=queue.popleft()
  if u not in seen:seen.add(u);batch.append(u)
 if not batch:break
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
  for result in ex.map(get,batch):
   if 'error' in result:d['failed'].append(result)
   else:pages[result['url']]=result;queue.extend(result['related'])
 d['pages']=list(pages.values());d['note']='Статьи графа ссылок, а не весь сайт. Автоматический сбор; применимость к конкретной версии требуется сверить.';F.write_text(json.dumps(d,ensure_ascii=False,indent=2))
print('read',len(pages),'failed',len(d['failed']),'queue',len(queue));
for x in pages.values():print(x['title'])

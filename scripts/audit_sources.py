"""Check one registered URL per site; skip failures and record evidence. A homepage is not a full site audit."""
import requests,concurrent.futures,json,bs4,re,datetime
from pathlib import Path
P=Path(__file__).resolve().parents[1];S=json.loads((P/'data/sources.json').read_text());out=[]
def check(x):
 u=x['url'];r={'number':x['number'],'name':x['name'],'requested_url':u,'checked_on':'2026-11-21','scope':'Только указанный в реестре URL, не весь сайт'}
 try:
  q=requests.get(u,timeout=7,headers={'User-Agent':'Mozilla/5.0 (compatible; research catalog/1.0)'},allow_redirects=True);r.update(status_code=q.status_code,final_url=q.url,content_type=q.headers.get('Content-Type',''))
  if q.status_code!=200:r['status']='http_error';return r
  soup=bs4.BeautifulSoup(q.content,'html.parser')
  for t in soup.select('script,style,noscript'):t.decompose()
  text=re.sub(r'\s+',' ',soup.get_text(' ',strip=True));r['title']=soup.title.get_text(' ',strip=True) if soup.title else '';r['visible_chars']=len(text)
  flags=['domain is for sale','домен продается','captcha','access denied','checking your browser','verify you are human','страница не найдена','404 not found']
  if any(f in text.lower() for f in flags):r['status']='blocked_or_error_content'
  elif len(text)<250:r['status']='insufficient_content'
  else:r['status']='content_returned_unreviewed';r['excerpt']=text[:280]
 except requests.RequestException as e:r['status']='network_error';r['error']=str(e)[:220]
 return r
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
 for result in ex.map(check,S):
  out.append(result);(P/'data/source-url-audit.json').write_text(json.dumps({'note':'Проверка URL не подтверждает, что источник изучен полностью; HTTP 200 не гарантирует содержание об игре. Сайты с ограничением доступа пропущены. Время указано по часовому поясу пользователя.','checks':out},ensure_ascii=False,indent=2))
from collections import Counter
print('checked',len(out),Counter(x['status'] for x in out))
for x in out:print(x['number'],x['status'],x.get('status_code',''),x['name'])

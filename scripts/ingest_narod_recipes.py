"""Read historical recipe pictograms and titles; don't invent unsupported fields."""
import json,re,requests,bs4
from pathlib import Path
P=Path(__file__).resolve().parents[1];u='https://niebalbillbur.narod.ru/retsepty.html';s=bs4.BeautifulSoup(requests.get(u,timeout=12).content,'html.parser'); data={c:json.loads((P/'data'/f'{c}.json').read_text()) for c in ['plants','materials']}
names=['Гипномак','Клеверхелл','Черничный крендель','Золотая пыль','Кукурузные палочки','Баклажадина','Гарбузики','Японский горох','Белая краска','Росянка острая','Черника с косточкой','Грибная текила','Черепки в томате','Волчий штык','Глазная настойка','Чесночная лилия','Сонный качан','Гипносон','Хеллия','Глазная росянка','Волчья кость','Голова-гриб','Сонхелл','Сонная росянка','Волчья пасть','Волчиум','Зомбиум']
rows=[(r,r.find_all('td',recursive=False)) for r in s.select('tr')];rows=[c for r,c in rows if len(c)>=5 and c[0].find('img') and c[2].find('img',title=lambda t:t and 'Время варки' in t)]
assert len(rows)==len(names),f'Таблица изменилась: {len(rows)} строк'
for name,cells in zip(names,rows):
 cat='materials' if name=='Белая краска' else 'plants';e=next(x for x in data[cat] if x['name']==name and (cat=='materials' or x.get('original_category')=='Рецепты'));parts=[];digits=''
 for img in cells[1].find_all('img'):
  fn=img.get('src','').split('/')[-1]; m=re.match(r'^(\d)(?:_\d+)?\.png$',fn)
  if m:digits+=m.group(1)
  elif fn in ('ravno.png','plus.png'):continue
  else:parts.append((digits or '?')+' × '+(img.get('title') or '[без подписи: '+fn+']'));digits=''
 uses=[a.get('title') for a in cells[5].find_all('img') if a.get('title')] if len(cells)>5 else []
 fields={'Ингредиенты (подписи пиктограмм источника)':' + '.join(parts),'Время варки':cells[2].get_text(' ',strip=True)+' минут','Продажа':cells[3].get_text(' ',strip=True)+' монет','Чистая прибыль по определению сайта':cells[4].get_text(' ',strip=True)+' монет; продажа продукта минус продажа ингредиентов','Применение (подписи пиктограмм)':'; '.join(uses) or 'не указано'}
 rid='narod-recipes-'+e['slug'];r={'original_id':rid,'original_category':'Рецепты','version':'браузерная версия; платформа не указана','date':'дата редакции не установлена','fields':fields,'confidence':'Данные исторической таблицы; количество и название прочитаны по значкам и их подписям. Возможны изменения игры и отличия версий.'};e.setdefault('prior_records',[]);e['prior_records']=[x for x in e['prior_records'] if x.get('original_id')!=rid]+[r]
 if not any(x['url']==u for x in e['sources']):e['sources'].append({'url':u,'label':'Таблица рецептов: прочитана строка и подписи пиктограмм'})
for cat,items in data.items():(P/'data'/f'{cat}.json').write_text(json.dumps(items,ensure_ascii=False,indent=2))
sources=json.loads((P/'data/sources.json').read_text())
for x in sources:
 if x['number']==16:x['summary']=x['summary'].replace('8 строк перенесены с указанием источника и неопределённости последней колонки.', '27 строк перенесены с подписями пиктограмм; последняя колонка — чистая прибыль по определению источника. Дата и игровая платформа требуют уточнения.')
(P/'data/sources.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2));print('Перенесено строк',len(rows))

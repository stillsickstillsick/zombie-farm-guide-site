"""Import material table as ordered pictogram descriptions with source labels, not inferred recipes."""
import requests,bs4,re,json
from pathlib import Path
from urllib.parse import unquote
P=Path(__file__).resolve().parents[1];url='https://niebalbillbur.narod.ru/materialy.html';q=requests.get(url,timeout=10);q.raise_for_status();s=bs4.BeautifulSoup(q.content,'html.parser');F=P/'data/materials.json';data=json.loads(F.read_text());norm=lambda s:re.sub(r'\s+',' ',s.lower().replace('ё','е')).strip();names={norm(e['name']):e for e in data};aliases={'Ингредиент белой краски':'Белая краска','Канаты':'Канат'};excluded={'Опыт','Монеты','Зомбаксы'};reports=[];n=0
for row in s.select('tr'):
 c=row.find_all('td',recursive=False)
 if len(c)!=5 or not c[0].find('img',title=True):continue
 img=c[0].find('img',title=True);title=img['title'].strip()
 if title in excluded:reports.append({'name':title,'status':'исключено: игровая валюта/опыт'});continue
 e=names.get(norm(aliases.get(title,title)))
 if not e:reports.append({'name':title,'status':'совпадение не установлено'});continue
 cols=[]
 for cell in c:
  bits=[]
  for node in cell.descendants:
   if isinstance(node,bs4.element.NavigableString):
    v=' '.join(str(node).split())
    if v:bits.append(v)
   elif node.name=='img':
    fn=unquote(node.get('src','').split('/')[-1]);desc=node.get('title') or node.get('alt') or ''
    par=node.find_parent('a');href=par.get('href','') if par else ''
    if desc:bits.append('[подпись: '+desc+'; файл '+fn+']')
    elif href and '#' in href:bits.append('[значок: #'+unquote(href.split('#')[-1])+'; файл '+fn+']')
    else:bits.append('[значок: '+fn+']')
  cols.append(' '.join(bits))
 fields={f'Колонка {i+1} в порядке пиктограмм':v for i,v in enumerate(cols)};rid='narod-material-'+e['slug'];rec={'original_id':rid,'original_category':'Материалы','version':'браузерная версия; платформа не указана','date':'дата редакции неизвестна','fields':fields,'confidence':'Подписи и последовательность пиктограмм перенесены без автоматического толкования. Названия, цены и направления стрелок требуют визуальной сверки; возможны ошибки самого сайта.'}
 if title=='Лента':rec['confidence']+=' Вероятная связь с «Лентой для скотча» не доказана, карточки остаются отдельными.'
 e.setdefault('prior_records',[]);e['prior_records']=[x for x in e['prior_records'] if x.get('original_id')!=rid]+[rec]
 if not any(x.get('url')==url for x in e['sources']):e['sources'].append({'url':url,'label':'Каталог материалов: строка и подписи значков'})
 n+=1;reports.append({'name':title,'slug':e['slug'],'status':'перенесено'})
F.write_text(json.dumps(data,ensure_ascii=False,indent=2));(P/'data/narod-materials-audit.json').write_text(json.dumps({'source':url,'rows':reports,'matched':n},ensure_ascii=False,indent=2));sources=json.loads((P/'data/sources.json').read_text())
for x in sources:
 if x['number']==16 and '48 строк таблицы материалов' not in x['summary']:x['summary']+=' Перенесены 48 строк таблицы материалов с последовательностями подписей значков; валюта и направления стрелок требуют ручной проверки.'
(P/'data/sources.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2));print('materials',n,'skip',[(x['name'],x['status']) for x in reports if x['status']!='перенесено'])

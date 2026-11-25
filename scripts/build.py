#!/usr/bin/env python3
"""Generate local-file-compatible pages, CSV and search index from canonical JSON. Never modify images."""
import json,csv,html,re,io
from pathlib import Path
P=Path(__file__).resolve().parents[1]
sections=[('sources','Источники'),('overview','Обзор игры'),('start','Начало игры'),('materials','Материалы'),('buildings','Постройки'),('collections','Коллекции'),('quests','Квесты'),('locations','Локации и острова'),('plants','Растения и рецепты'),('zombies','Зомби и рабочие'),('eggs-trophies','Яйца и трофеи'),('updates','Обновления'),('economy','Экономика'),('glossary','Глоссарий'),('open-questions','Нерешённые вопросы')]
labels=dict(sections); esc=lambda x:html.escape(str(x),quote=True)
def read(n):
 f=P/'data'/f'{n}.json';return json.loads(f.read_text()) if f.exists() else []
records={s:read(s) for s,_ in sections if s not in ('sources','overview','start','open-questions')};sources=read('sources');search=[]
for cat,items in records.items():
 seen=set()
 for x in items:
  slug=x.get('slug','')
  if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',slug):raise ValueError(f'Некорректный slug: {cat}/{slug}')
  if slug in seen:raise ValueError(f'Повторный slug: {cat}/{slug}')
  seen.add(slug)
  images=([x['image']] if x.get('image') else [])+[g['image'] for g in x.get('gallery',[]) if g.get('image')]
  for image in images:
   path=(P/image['path']).resolve()
   if not path.is_relative_to((P/'img').resolve()) or not path.is_file():raise ValueError(f'Недоступный или некорректный файл: {image["path"]}')
by_key={(cat,x['slug']):x for cat,items in records.items() for x in items}; inbound={} 
for cat,items in records.items():
 for x in items:
  for link in x.get('links',[]):
   if (link.get('category'),link.get('slug')) in by_key:inbound.setdefault((link['category'],link['slug']),[]).append((cat,x,link.get('relation','связано'))) 
def url(root,path):return root+path
def layout(title,body,root,section=None):
 # Search is present only on the homepage; other pages do not need the 459 KB index.
 index_script=f'<script defer src="{root}data/search-index.js"></script>' if section is None else ''
 nav=''.join(f'<a href="{url(root,k+"/index.html")}"'+(' aria-current="page"' if k==section else '')+'>'+esc(v)+'</a>' for k,v in sections)
 return f'''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><script src="{root}assets/theme-init.js"></script><title>{esc(title)} — Зомби Ферма</title><link rel="stylesheet" href="{root}assets/style.css">{index_script}<script defer src="{root}assets/app.js"></script></head><body data-root="{root}" class="{'home-page' if section is None else 'inner-page'}"><header><div class="wrap top"><a class="brand" href="{root}index.html"><span class="brand-leaf">✿</span> ЗОМБИ <em>ФЕРМА</em><small>НЕОФИЦИАЛЬНЫЙ СПРАВОЧНИК</small></a><nav class="topnav" aria-label="Главная навигация"><a href="{root}index.html">Главная</a><a href="{root}locations/index.html">Острова</a><a href="{root}quests/index.html">Квесты</a><a href="{root}updates/index.html">Новости</a><a href="{root}sources/index.html">Источники</a></nav><button class="theme-toggle" type="button" aria-label="Переключить цветовую тему">☾ Тёмная тема</button><a class="top-button" href="{root}overview/index.html">Об игре</a></div></header><div class="wrap layout"><aside class="sidebar"><span class="eyebrow">Оглавление</span><nav>{nav}</nav></aside><main>{body}</main></div><footer class="wrap">Неофициальный фанатский справочник. Права на игру и графику принадлежат правообладателям; материалы используются в справочных целях. Правовой статус изображений требует проверки. Данные исторические. Заставка: скриншот Домашнего острова, файл с <a href="https://zombie-island.moy.su/zombie-farm/ZombiFermaMania/Ostrova-foto/Domashnij-Ostrov-foto-skrin-Igra-Zombie-Farm-Mania.jpg">Zombie-island</a>; исходная ссылка в архиве — zombicity.info. Значки монет и зомбаксов: <a href="https://niebalbillbur.narod.ru/materialy.html">источник изображений</a>.</footer></body></html>'''
def thumbnail(x,root):
 image=x.get('image'); alt=x['name']
 if not image:
  for g in x.get('gallery',[]):
   if g.get('image'):
    image=g['image'];alt='Элемент коллекции: '+g['name'];break
 if not image:return '<span class="list-placeholder" aria-label="нет изображения">—</span>'
 return f'<img class="list-thumb" loading="lazy" src="{root}{esc(image["path"])}" alt="{esc(alt)}" title="{esc(alt)}">'
def thumbdata(x):
 if x.get('image'):return x['image']['path'],x['name']
 for g in x.get('gallery',[]):
  if g.get('image'):return g['image']['path'],'Элемент коллекции: '+g['name']
 return '', 'нет изображения'
def write(path,text):
 f=P/path;f.parent.mkdir(parents=True,exist_ok=True)
 if not f.exists() or f.read_text(encoding='utf8')!=text:f.write_text(text,encoding='utf8')
def block(title,content):return f'<section class="box"><h2>{esc(title)}</h2>{content}</section>'
# Rendering changes do not alter canonical JSON, CSV, search text or screen-reader currency labels.
amount=re.compile(r'(?<![\w])(?P<number>\d[\d \u00a0\u202f]*?)[ \u00a0\u202f]*(?P<unit>зб|зомбаксов|зомбакса|зомбаксы|зомбакс|зомбобаксов|зомбобакса|зомбобакс|зомбибаксов|зомбибакса|зомбибакс|монетами|монетах|монетам|монетой|монетку|монеты|монета|монету|монет)(?![\w])',re.I)
# Exact material names only, plus a small audited set of quantity-dependent inflections.
ambiguous={'мир','свет','тепло','огонь','вода','сила','любовь','опыт','звезда','рука','воля','счастье','удача','семена','время','камень','песок'}
def normalize_material(t):return t.casefold().replace('ё','е')
material_by_name={}
for entity in records.get('materials',[]):
 name=entity['name'].strip();key=normalize_material(name)
 if len(name)>=4 and key not in ambiguous:material_by_name.setdefault(key,[]).append(entity)
material_by_name={k:v[0] for k,v in material_by_name.items() if len(v)==1}
inflections={'блоков':'Блоки','шестерён':'Шестерня','шестерен':'Шестерня','болтов':'Болт','труб':'Труба','листов золота':'Лист золота','гаек':'Гайка','газет':'Газеты','книг':'Книги','досок':'Доска','гвоздей':'Гвозди','камней':'Камни','брёвен':'Брёвна','бревен':'Брёвна','фанеры':'Фанера','проволоки':'Проволока','цемента':'Цемент','стекла':'Стекло','фольги':'Фольга','металла':'Металл','белой краски':'Белая краска','красной краски':'Красная краска','зелёной краски':'Зелёная краска','желтой краски':'Жёлтая краска','красной черепицы':'Красная черепица','синей черепицы':'Синяя черепица','супер-клея':'Супер-клей','кварца':'Кварц','пружин':'Пружина','ведер':'Ведро','вёдер':'Ведро'}
inflections={normalize_material(k):material_by_name[normalize_material(v)] for k,v in inflections.items() if normalize_material(v) in material_by_name}
variants=dict(material_by_name)
for name,e in inflections.items():variants.setdefault(name,e)
words=re.compile(r'(?<![\w])(?:'+'|'.join(re.escape(t).replace('е','[её]') for t in sorted(variants,key=len,reverse=True))+r')(?![\w])',re.I) if variants else re.compile(r'(?!x)x')

def currency_text(value,root,link_materials=False,exclude_slug=None):
 text=str(value);matches=[(m.start(),m.end(),'currency',m) for m in amount.finditer(text)]
 if link_materials:
  for m in words.finditer(text):
   key=normalize_material(m.group());e=variants.get(key)
   # Inflected forms are linked only after an explicit quantity, to avoid e.g. "остров Любви".
   if not e or e['slug']==exclude_slug or (key in inflections and not re.search(r'\d[ \u00a0\u202f]*$',text[max(0,m.start()-20):m.start()])):continue
   if any(a < m.end() and m.start() < b for a,b,_,_ in matches):continue
   matches.append((m.start(),m.end(),'material',(m,e)))
 parts=[];pos=0
 for start,end,kind,match in sorted(matches,key=lambda m:m[0]):
  if start<pos:continue
  parts.append(esc(text[pos:start]))
  if kind=='material':
   m,e=match;parts.append('<a class="material-link" href="'+root+'materials/'+esc(e['slug'])+'/index.html" title="Автоматическая ссылка на материал: '+esc(e['name'])+'; проверьте контекст">'+esc(m.group())+'</a>')
  else:
   unit=match.group('unit');coin=unit.casefold().startswith('мон');file='moneta.png' if coin else 'zombaks.png';label='Монеты' if coin else 'Зомбаксы'
   parts.append(esc(match.group('number').rstrip())+' <img class="currency-icon" src="'+root+'assets/'+file+'" alt="" aria-hidden="true" title="'+label+'"><span class="visually-hidden">'+esc(unit)+'</span>')
  pos=end
 parts.append(esc(text[pos:]));return ''.join(parts)

def bread(root,parts):return '<div class="bread"><a href="'+root+'index.html">Главная</a> / '+' / '.join(parts)+'</div>'
searchbox='<div class="searchrow"><input id="search" type="search" placeholder="Название, материал, рецепт…" aria-label="Полнотекстовый поиск" autocomplete="off"><select id="search-category" aria-label="Категория"><option value="">Все категории</option>'+''.join(f'<option value="{esc(v)}">{esc(v)}</option>' for k,v in sections if k in records)+'</select><select id="search-order" aria-label="Порядок сортировки"><option value="name">По названию</option><option value="price">По цене покупки</option></select></div><div id="results" class="results" hidden aria-live="polite"></div>'
category_picks={'materials':'zoloto','buildings':'mayak','collections':'morskaya-kollektsiya','quests':'','locations':'','plants':'','zombies':'','eggs-trophies':'','updates':'zombia-football-2012','economy':'zombia-my1-zombium-scheme-2012'}
def category_image(k):
 items=records.get(k,[]); pick=category_picks.get(k,'')
 selected=next((e for e in items if e['slug']==pick and e.get('image')),None) or next((e for e in items if e.get('image')),None)
 return ('<img class="category-art" src="'+esc(selected['image']['path'])+'" alt="" loading="lazy">') if selected else '<span class="category-symbol" aria-hidden="true">✿</span>'
grid=''.join(f'<a class="card" href="{k}/index.html">{category_image(k)}<strong>{esc(v)}</strong><span class="count">{len(records.get(k,[]))} карточек</span></a>' for k,v in sections if k not in ('sources','open-questions','overview','start'))
home=f'''<section class="hero-stage"><div class="hero-copy"><span class="hero-kicker">ДОБРО ПОЖАЛОВАТЬ НА ФЕРМУ</span><h1>Зомби<br><span>Ферма</span></h1><p>Вспомним любимую игру вместе! Острова, коллекции, задания и многое другое — в одном уютном справочнике.</p><a class="hero-button" href="#catalog">Открыть справочник <span aria-hidden="true">→</span></a><div class="hero-note">✿ Неофициальный архив браузерной игры</div></div></section><section class="search-panel"><div><span class="eyebrow">ПОИСК ПО ФЕРМЕ</span><h2>Что будем искать?</h2></div>{searchbox}</section><section class="catalog-section" id="catalog"><div class="section-heading"><span>✿</span><h2>Разделы справочника</h2><span>✿</span></div><p class="section-intro">Исследуйте острова, находите рецепты и узнавайте истории любимых предметов.</p><div class="grid">{grid}</div></section><section class="welcome-section"><div class="section-heading"><span>✿</span><h2>С чего начать</h2><span>✿</span></div><div class="welcome-grid"><a href="overview/index.html"><b>1</b><strong>Об игре</strong><span>Вспомнить мир и его историю</span></a><a href="start/index.html"><b>2</b><strong>Начало игры</strong><span>Основы и первые шаги</span></a><a href="sources/index.html"><b>3</b><strong>Источники</strong><span>Узнать, откуда взяты сведения</span></a></div></section><section class="archive-note"><span class="archive-icon">✉</span><div><strong>Сохраняем историю фермы вместе</strong><p>Здесь собраны исторические данные. Спорные сведения и пробелы мы честно отмечаем.</p></div><a href="open-questions/index.html">Что ещё проверить →</a></section>'''

write('index.html',layout('Главная',home,'./'))
headers=[('name','Название'),('purchase','Покупка'),('sale','Продажа'),('obtain','Получение'),('use','Применение')]
for sec,title in sections:
 root='../';start=bread(root,[esc(title)])+f'<section class="box"><span class="eyebrow">Справочник · исторические данные</span><h1>{esc(title)}</h1>'
 if sec=='sources':
  rows=''.join(f'<tr><td><a href="{esc(x["url"])}">{esc(x["name"])}</a></td><td>{esc(x["category"])}</td><td>{esc(x["summary"])}</td><td>не установлено</td><td>не установлено, если не описано в примечании</td></tr>' for x in sources)
  body=start+f'<p>Аудит отдельных страниц; состояние каждого сайта и дата последнего обновления нуждаются в дополнительной проверке. {len(sources)} записей не означают независимые источники.</p><input id="table-filter" type="search" placeholder="Фильтр источников" aria-label="Фильтр источников"><div class="scroll"><table data-sortable><thead><tr>'+''.join(f'<th><button>{x}</button></th>' for x in ('Источник','Тип','Содержимое и проверка','Последнее обновление','Независимость / заимствование'))+f'</tr></thead><tbody>{rows}</tbody></table></div></section>'
  body+=block('Проверенные архивные снимки','<ul><li><a href="https://web.archive.org/web/20220118123554/http://zombitime.com/portal">ZombiTime, портал — снимок 18.01.2022</a></li><li><a href="https://web.archive.org/web/20211205170834/http://zombitime.com/prohozhdenie-kvesta-znanie">«Знание» — снимок 05.12.2021</a></li><li><a href="https://web.archive.org/web/20170615061646/https://zombieisland.org/eng">Zombie Island — снимок 15.06.2017</a></li><li><a href="https://web.archive.org/web/20130703023915/http://zombicity.info/blog/zombie_farm_na_ostrov_ljubvi/2012-07-18-206">ЗомбиСити: остров Любви — снимок 03.07.2013</a></li></ul><p>Снимок страницы не гарантирует, что архивированы все файлы.</p>')
  body+=block('Карта копий','<p>Статья «Воздушный шар» Zombie-island.moy.su и архив ЗомбиСити совпадают. Скриншот острова Любви на зеркале совпал по SHA-256 с архивом. Ссылки на чужие картинки доказывают источник картинки, но не авторство текста. Не все страницы этих сайтов сверены.</p>')
 elif sec=='open-questions':
  body=start+'''<ul><li>Проверить запуск и фактическую дату закрытия по первичным источникам; прекращение разработки не равно закрытию.</li><li>Постранично проверить версии игры, цены, уровни, квесты и стадии построек.</li><li>Сверить заявленную связь zombia.ru и zombi.at.ua; использование одного хоста изображений само по себе не доказывает зеркало текста.</li><li>Проверить предварительные карточки; изображения низкого разрешения не выдавать за оригиналы.</li><li>Проверить источники недостающих изображений и сохранность архивов.</li><li>В статье ZOMBIA о кирке в получении упомянут топор; не переносить это как подтверждённый способ. Подпись картинки зуба дракона называет белую краску.</li><li>Установить, совпадают ли отдельные карточки «Лента» и «Лента для скотча»; пока они не объединены.</li><li>Создать нормализованные связи сущностей и матрицы построек; сравнить противоречия с датами версий.</li></ul></section>'''
 elif sec=='materials':
  items=records[sec]; rows=''
  for x in items:
   cells=[f'<a class="name-cell" href="{esc(x["slug"])}/index.html">{thumbnail(x,root)}<span>{esc(x["name"])}</span></a>']+[currency_text(x[k],root).replace('\n','; ') for k,_ in headers[1:]];rows+='<tr>'+''.join('<td>'+v+'</td>' for v in cells)+'</tr>'
  body=start+f'<p>{len(items)} карточек из исторических источников ВКонтакте, «Моего Мира» и других браузерных версий. Сведения разных площадок и дат приведены раздельно; неподписанные изображения и ошибки источников требуют сверки.</p><input id="table-filter" type="search" placeholder="Фильтр таблицы" aria-label="Фильтр таблицы"><div class="scroll"><table data-sortable><thead><tr>'+''.join(f'<th><button>{esc(v)}</button></th>' for k,v in headers)+f'</tr></thead><tbody>{rows}</tbody></table></div><p><a href="../data/materials.csv">Выгрузить CSV</a></p></section>'
 else:
  items=records.get(sec,[])
  if items:
   rows=''.join(f'<tr><td><a class="name-cell" href="{esc(x["slug"])}/index.html">{thumbnail(x,root)}<span>{esc(x["name"])}</span></a></td><td>{esc(x.get("original_category",x.get("type","нет данных")))}</td><td>{esc(x.get("versions","нет данных"))}</td><td>предварительные сведения, требуется сверка</td></tr>' for x in items)
   body=start+f'<p>{len(items)} карточек из предыдущего исследования. Полнота и точность каждой карточки нуждаются в дополнительной сверке.</p><input id="table-filter" type="search" placeholder="Фильтр таблицы" aria-label="Фильтр таблицы"><div class="scroll"><table data-sortable><thead><tr>'+''.join(f'<th><button>{esc(v)}</button></th>' for v in ('Название','Тип','Версия и дата','Статус'))+f'</tr></thead><tbody>{rows}</tbody></table></div></section>'
  else:body=start+'<p class="empty">Раздел создан; проверенные карточки для новой структуры пока не перенесены. Это не свидетельство отсутствия игровых объектов.</p></section>' 
 write(sec+'/index.html',layout(title,body,root,sec))
for sec,items in records.items():
 for x in items:
  root='../../';title=x['name'];route=f'{sec}/{x["slug"]}/index.html';text=' '.join(str(x.get(k,'')) for k in ('name','type','purchase','sale','obtain','use','features','versions','source_text'))+' '+ ' '.join(' '.join(str(k)+' '+str(v) for k,v in record.get('fields',{}).items()) for record in x.get('prior_records',[]))
  search.append({'name':title,'section':labels[sec],'url':route,'text':text,'purchase':x.get('purchase','нет данных'),'type':x.get('type','нет данных'),'event':x.get('event','нет данных'),'thumbnail':thumbdata(x)[0],'thumbnail_alt':thumbdata(x)[1]})
  image=x.get('image')
  if image:
   page_link = (' Страница: <a href="'+esc(image['source_page'])+'">источник</a>.') if image.get('source_page') else ''
   photo=f'<div><a href="{root}{esc(image["path"])}" title="Открыть исходное изображение"><img class="itemimage" loading="lazy" src="{root}{esc(image["path"])}" alt="{esc(title)}"></a><p class="small">Получено: <a href="{esc(image["retrieved_from"])}">файл</a>; <a href="{esc(image["attribution"])}">исходный URL</a>. {esc(image["note"])}{page_link}</p></div>'
  else:photo='<div class="placeholder">[нет изображения]</div>' 
  flds=[('Тип','type'),('Покупка','purchase'),('Продажа','sale'),('Как получить','obtain'),('Применение','use'),('Особенности','features'),('Версия и дата','versions')] if sec=='materials' else [('Тип','type'),('Версия и дата','versions')];details=''.join(f'<dt>{esc(l)}</dt><dd>{currency_text(x.get(k) or "нет данных",root,link_materials=True,exclude_slug=(x["slug"] if sec=="materials" else None))}</dd>' for l,k in flds)
  previous=''
  for record in x.get('prior_records',[]):
   fieldhtml=''.join(f'<dt>{esc(k)}</dt><dd>{currency_text(v,root,link_materials=True,exclude_slug=(x['slug'] if sec=='materials' else None))}</dd>' for k,v in record.get('fields',{}).items())
   previous+=f'<details open><summary>Данные по источнику · {esc(record["version"])} · {esc(record["date"])}</summary><p class="small">Предварительно: {esc(record["confidence"])}. Требуется сверка.</p><dl class="fields">{fieldhtml}</dl></details>'
  gallery=''
  if x.get('gallery'):
   parts=[]
   for g in x['gallery']:
    if g.get('image'):parts.append(f'<figure><a href="{root}{esc(g["image"]["path"])}" title="Открыть локальное изображение"><img class="galleryimg" loading="lazy" src="{root}{esc(g["image"]["path"])}" alt="{esc(g["name"])}"></a><figcaption>{esc(g["name"])} · <a href="{esc(g["image"]["retrieved_from"])}">файл источника</a> · <a href="{esc(g["url"])}">страница источника</a>{(" · "+esc(g["image"].get("note", ""))) if g["image"].get("note") else ""}</figcaption></figure>')
    else:parts.append(f'<figure><span>[нет изображения]</span><figcaption>{esc(g["name"])} · <a href="{esc(g["url"])}">источник</a></figcaption></figure>')
   gallery=('<h2>Элементы коллекции</h2>' if sec=='collections' else '<h2>Дополнительные изображения</h2>')+'<div class="gallery">'+''.join(parts)+'</div>'
  refs=''.join(f'<li><a href="{esc(z["url"])}">{esc(z["label"])}</a></li>' for z in x.get('sources',[])) or '<li>нет данных</li>'
  related=[]
  for l in x.get('links',[]):
   if (l.get('category'),l.get('slug')) in by_key:related.append(f'<li><a href="{root}{esc(l["category"])}/{esc(l["slug"])}/index.html">{esc(l["name"])}</a> — {esc(l.get("relation","связано"))}</li>')
  for cat,other,relation in inbound.get((sec,x['slug']),[]):related.append(f'<li><a href="{root}{esc(cat)}/{esc(other["slug"])}/index.html">{esc(other["name"])}</a> — {esc(relation)}</li>')
  relhtml='<ul>'+''.join(related)+'</ul>' if related else '<p>нет проверенных связей — требуется сверка.</p>'
  body=bread(root,[f'<a href="../index.html">{esc(labels[sec])}</a>',esc(title)])+f'<article class="box"><span class="eyebrow">{esc(labels[sec])} · исторические данные</span><div class="itemhead">{photo}<div><h1>{esc(title)}</h1><span class="badge">{esc(x["versions"])}</span></div></div><dl class="fields">{details}</dl>{gallery}{previous}{('<details><summary>Текст источника без реконструкции</summary><p class="source-text">'+currency_text(x.get('source_text'),root,link_materials=True,exclude_slug=(x['slug'] if sec=='materials' else None))+'</p></details>') if x.get('source_text') else ''}<h2>Связанные сущности</h2>{relhtml}<h2>Источники</h2><ul>{refs}</ul></article>'
  write(route,layout(title,body,root,sec))
# Data for file:// must be JS, because browsers block fetch(file://). Derived index, not an independent data source.
write('data/search-index.js','window.SEARCH_INDEX = '+json.dumps(search,ensure_ascii=False,separators=(',',':'))+';\n')
for sec in ('materials','buildings','collections','quests'):
 fields=['name','purchase','sale','obtain','use','versions','sources'] if sec=='materials' else ['name','sources']
 buf=io.StringIO(newline='');w=csv.writer(buf,delimiter=';');w.writerow(fields)
 for x in records.get(sec,[]):w.writerow([(' | '.join(y.get('url','') for y in x.get(k,[])) if k=='sources' else x.get(k,'')) for k in fields])
 content=('\ufeff'+buf.getvalue()).encode('utf-8');target=P/'data'/f'{sec}.csv'
 if not target.exists() or target.read_bytes()!=content:target.write_bytes(content)
print('pages',sum(1 for f in P.rglob('*.html') if not f.is_relative_to(P/'research')),'records',len(search),'sources',len(sources))

#!/usr/bin/env python3
"""Conservative source-page ledger: evidence of use is not evidence of complete review."""
import csv,collections,hashlib,json,pathlib,re,urllib.parse,datetime
P=pathlib.Path(__file__).resolve().parents[1];B=P/'research/session-materials/bulk-research';OUT=P/'research/source-registry';OUT.mkdir(exist_ok=True)
rows={}
def key(url):
 try:
  u=urllib.parse.urlsplit(url.strip());host=u.hostname.lower() if u.hostname else ''
  if u.scheme not in ('http','https') or not host:return None
  return urllib.parse.urlunsplit((u.scheme.lower(),host,u.path or '/',u.query,''))
 except (ValueError,AttributeError):return None
def get(url):
 k=key(url)
 if not k:return None
 if k not in rows:rows[k]={'url':k,'адреса':set(),'id':'','заголовок':'','локальный_файл':'','sha256':'','карточки':set(),'доказательства':set(),'статус':'Не подтверждено изучение','объём_сверки':'','примечание':set()}
 rows[k]['адреса'].add(url);return rows[k]
logs=[json.loads(s) for s in (B/'download-log.jsonl').read_text().splitlines() if s.strip()];byid={}
for e in logs:
 if e.get('status')=='downloaded_unreviewed' and (B/'pages'/f"{e.get('id')}.html").exists():byid[e['id']]=e
for i,e in byid.items():
 r=get(e['final_url']);r.update(id=str(i),заголовок=e.get('title',''),локальный_файл=f'research/session-materials/bulk-research/pages/{i}.html',sha256=hashlib.sha256((B/'pages'/f'{i}.html').read_bytes()).hexdigest());r['доказательства'].add('Сохранена страница; проведена техническая инвентаризация')
# Additional source bytes saved during the current reviewed batch.
extra=P/'research/reviewed-sources/manifest.json'
if extra.exists():
 for e in json.loads(extra.read_text()):
  f=extra.parent/(e['id']+'.html');assert hashlib.sha256(f.read_bytes()).hexdigest()==e['sha256']
  r=get(e['url']);r['доказательства'].add('Сохранена отдельная страница, SHA-256 проверен')
  if not r['локальный_файл']:r.update(локальный_файл=str(f.relative_to(P)),sha256=e['sha256'])
# Explicitly include all 70 source-catalog entries, their structured links, and URLs in their summaries.
catalog=json.loads((P/'data/sources.json').read_text())
source_fields=['номер','название','категория','основной_url','описание_из_каталога','связанные_url']
with (OUT/'каталог-источников.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=source_fields);w.writeheader()
 for x in catalog:
  links=[a.get('url','') for a in x.get('related',[]) if isinstance(a,dict) and a.get('url')]
  links+= [v.rstrip('.,;:!?)]}»') for v in re.findall(r'https?://[^\s<>\"\']+',x.get('summary',''))]
  for address in [x.get('url','')]+links:
   r=get(address)
   if r:r['доказательства'].add(f"Каталог data/sources.json: источник {x.get('number')} — {x.get('name')}; статус страницы отдельно не определён")
  w.writerow({'номер':x.get('number'),'название':x.get('name'),'категория':x.get('category'),'основной_url':x.get('url'),'описание_из_каталога':x.get('summary'),'связанные_url':' | '.join(dict.fromkeys(links))})
# Retain every externally cited page URL from the canonical records; other web pages are out of scope.
for cat in ('quests','locations','buildings','collections','materials','plants','zombies','eggs-trophies','updates','glossary','economy'):
 p=P/'data'/f'{cat}.json'
 if not p.exists():continue
 doc=json.loads(p.read_text());items=doc if isinstance(doc,list) else []
 for x in items:
  if not isinstance(x,dict):continue
  marker=f"{cat}/{x.get('slug','?')}";ids=[]
  for record in x.get('prior_records',[]):
   if not isinstance(record,dict):continue
   m=re.fullmatch(r'(?:cached-story-2016|bulk-moy-quest)-(\d+)(?:-disagreement)?',record.get('original_id',''))
   if m:ids.append(m[1])
  for s in x.get('sources',[]):
   if not isinstance(s,dict):continue
   r=get(s.get('url',''))
   if not r:continue
   r['карточки'].add(marker);label=s.get('label','');low=label.lower()
   evidence=any(t in low for t in ('прочитан','прочитано','отдельная статья квеста','отдельное задание','историческая карточка')) and not any(t in low for t in ('не прочитан','не проверен','отдельный доступ не проверен','отдельная страница не проверена'))
   id_match=bool(r['id'] and r['id'] in ids)
   if evidence or id_match:
    r['статус']='Изучена (подтверждён факт использования)';r['доказательства'].add(('Запись карточки: '+label) if evidence else 'Совпадает ID извлечённой записи карточки')
   else:r['доказательства'].add('Ссылка присутствует в карточке; отдельное изучение не подтверждено')
# Specifically documented matching of two source records, not wholesale verification of each claim.
for i in range(2655,2689):
 if i not in byid:continue
 r=get(byid[i]['final_url'])
 if not r['карточки']:continue
 r['статус']='Сверена с другим источником (частично)'
 if i==2684:r['объём_сверки']='Три цели и награда сопоставлены с ZOMBIA; сюжет противоречит целям.';r['примечание'].add('Противоречие сохранено: упоминание Университета при целях Бизнес-центра.')
 else:r['объём_сверки']='Название и начало описания сопоставлены с существующей записью ZOMBIA; полное совпадение всех фактов не утверждается.'
 r['доказательства'].add('scripts/enrich_upsa_2014.py; scripts/audit_upsa_business_disagreement.py; research/session-materials/pending-notes.md')
# Manually reviewed pirate comparisons: only listed attributes have been cross-compared.
for i,scope in {2273:'Сопоставлены три исторические цены с ZOMBIA; происхождение обычных дублонов от Сильвера не указано.',2304:'Сопоставлены открытие дома и перечисленные Плохая и Тропическая коллекции с ZOMBIA; вероятности не указаны.',2305:'Сопоставлены открытие дома и названия трёх коллекций с ZOMBIA; вероятности не указаны.',2306:'Сопоставлены открытие дома и названия трёх коллекций с ZOMBIA; вероятности не указаны.'}.items():
 if i not in byid:continue
 r=get(byid[i]['final_url']);r['статус']='Сверена с другим источником (частично)';r['объём_сверки']=scope;r['доказательства'].add('scripts/enrich_cached_pirate_treasures.py; отдельная запись ZOMBIA в соответствующей карточке')
# Explicit, limited comparisons: claims, not entire websites, were compared.
reviewed={
'https://www.fatalgame.com/answer/zombiferma/найти-древний-сундук-в-игре-зомби-ферма':'Состав в статье сопоставлен с ZOMBIA: 1000 сердец и 500000 монет; цена 25 голосов указана только ZOMBIA.',
'https://zombi.at.ua/board/materialy/quot_slozhnye_quot_materialy/drevnij_sunduk/7-1-0-741':'Сопоставлен состав древнего сундука с FatalGame; дата правок и независимость не установлены.',
'https://www.fatalgame.com/answer/zombiferma/фантастический-сундук-в-игре-зомби-ферма':'Цена 500 голосов сопоставлена с ZOMBIA; расхождение 1000 против 6000 зомбаксов.',
'https://zombi.at.ua/board/materialy/quot_slozhnye_quot_materialy/krutoj_sunduk/7-1-0-744':'Цена сопоставлена с FatalGame; расхождение 6000 против 1000 зомбаксов.',
'https://www.fatalgame.com/answer/zombiferma/искать-сундук-мертвеца-в-игре-зомби-ферма':'70 дублонов при первом открытии сопоставлены с Zombie-island; независимость неизвестна.',
'https://zombie-island.moy.su/blog/sunduk_mertveca_sokrovishhe_zombie_farm_gde_vzjat_mania/2013-10-30-2315':'70 дублонов за первое открытие сопоставлены с FatalGame; статья отредактирована после даты URL 2013-10-30, поскольку новость 2013-11-22 говорит об увеличении с 50 до 70.',
'https://zombie-island.moy.su/news/22_nojabrja_za_dobychej_trjumy_kapitanov_lomjatsja_ot_nagrablennogo/2013-11-22-130':'Датировка увеличения награды с 50 до 70 сопоставлена со статьёй того же сайта и с FatalGame; это не независимые редакции новости.'}
# Current material batch: compare only the named claim, not the entire article.
new_materials={
'fatal-mel':'Сопоставлен рецепт мела в Школе: 10 цемента и 2 супер-клея; выход одна единица.',
'fatal-tochilka':'Сопоставлен рецепт пяти точилок; в статье о Глобусе описан более ранний выход одной без даты перехода.',
'fatal-neft':'Сопоставлены два входных ингредиента; число результата FatalGame не указывает.',
'fatal-vaza':'Сопоставлены возможные названия коллекций с карточкой Zombie-island; вероятности неизвестны.',
'fatal-khrustal':'Сопоставлены запрет покупки и продажа за 1000 монет с Zombie-island.',
'fatal-fanera':'Сопоставлены покупка за зомбакс и рулетки флагов с Zombie-island.',
'moy-globus-1230':'Статья о Глобусе: утверждение об изменении выхода с 1 до 5 точилок сопоставлено с FatalGame; точная дата перехода неизвестна.',
'moy-tochilka-1231':'Сопоставлен рецепт пяти точилок с FatalGame и описанием Глобуса того же сайта.',
'moy-vaza-2314':'Сопоставлены пять названий коллекций с FatalGame; вероятности и независимость неизвестны.'}
if extra.exists():
 for entry in json.loads(extra.read_text()):
  if entry['id'] in new_materials:reviewed[entry['url']]=new_materials[entry['id']]
for url,scope in reviewed.items():
 r=get(url);r['статус']='Сверена с другим источником (частично)';r['объём_сверки']=scope;r['доказательства'].add('Сохранены статьи и выборочно сопоставлены данные; см. соответствующие карточки.')
for r in rows.values():
 if r['id']=='2262':r['примечание'].add('Сохранённый HTML не содержит распознаваемых title или h1; проверить вручную.')
 if r['id']=='3776':r['примечание'].add('Дата в URL — 2015, индекс относит к цепочке 2016; дата создания/правки неизвестна.')
counts=collections.Counter(r['статус'] for r in rows.values());saved=[r for r in rows.values() if r['локальный_файл']];savedc=collections.Counter(r['статус'] for r in saved)
cols=['url','адреса','id','заголовок','локальный_файл','sha256','статус','объём_сверки','карточки','доказательства','примечание']
with (OUT/'реестр-страниц.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=cols);w.writeheader()
 for r in sorted(rows.values(),key=lambda v:(urllib.parse.urlsplit(v['url']).hostname,v['url'])):
  w.writerow({k:' | '.join(sorted(v)) if isinstance(v,set) else v for k,v in r.items()})
summary=['# Реестр источников: область охвата и методика','','Реестр учитывает все 70 записей каталога data/sources.json (основные адреса, связанные ссылки и URL из описаний), сохранённые HTML-страницы bulk-research и reviewed-sources и URL источников из карточек основных категорий data/*.json. Отдельный каталог-источников.csv сохраняет имена, категории и исходные описания всех 70 записей. Это не полный список страниц интернета или всех материалов каждого сайта; внешние находки, не внесённые в эти данные, могут отсутствовать.','',f'Всего уникальных URL в реестре: {len(rows)}.',f'Из них сохранённые HTML: {len(saved)}.','', '## Статусы']
for k,v in sorted(counts.items()):summary.append(f'- {k}: {v} / {len(rows)} ({100*v/len(rows):.1f}%).')
summary+=['','## Только сохранённые HTML']
for k,v in sorted(savedc.items()):summary.append(f'- {k}: {v} / {len(saved)} ({100*v/len(saved):.1f}%).')
summary+=['','«Не подтверждено изучение» не означает, что страницу точно не изучали: отметка означает недостаток явного подтверждения в выбранных данных. «Изучена» означает зафиксированное использование страницы или явную пометку о чтении, но не полную проверку всех её утверждений. «Сверена» означает частичное документированное сопоставление двух источников; масштаб сверки указан в строке. Сходные сайты могут копировать друг друга, независимость источников не установлена.','', 'Разные хосты и схемы http/https учитываются отдельно, даже когда есть основания подозревать зеркало; возможны дубли одного материала, а адреса не считаются независимыми источниками автоматически. Ссылки из других разделов проекта и внешнего веба, не попавшие в выбранные данные, в охват не включены. Проценты относятся только к перечисленным URL, а не к полному объёму сайтов.','', 'Список автоматически создан скриптом scripts/build_research_registry.py. Внутри репозитория реестр приватный и исключён из публичного сайта вместе с каталогом research.']
summary += ['', '## Единый реестр сайтов', 'Файл единый-реестр-сайтов.csv содержит одну строку на домен: записи каталога и их исходные описания, числа известных URL по статусам, число сохранённых HTML и процент URL с подтверждённым использованием. Процент не является оценкой завершённости изучения всего сайта. Архив web.archive.org указан отдельно от исходных сайтов; разные хосты, схемы и зеркала не объединяются автоматически.']
(OUT/'README.md').write_text('\n'.join(summary)+'\n');print('\n'.join(summary[:20]))
# Site-level rollup uses exactly the same finite page set, not an estimate of whole websites.
sites=collections.defaultdict(collections.Counter)
for r in rows.values():
 host=urllib.parse.urlsplit(r['url']).hostname;sites[host]['всего']+=1;sites[host][r['статус']]+=1;sites[host]['сохранено_HTML']+=bool(r['локальный_файл'])
fields=['домен','всего','сохранено_HTML','Не подтверждено изучение','Изучена (подтверждён факт использования)','Сверена с другим источником (частично)']
with (OUT/'сводка-по-сайтам.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
 for host,c in sorted(sites.items(),key=lambda t:(-t[1]['всего'],t[0])):w.writerow({'домен':host,**{k:c[k] for k in fields[1:]}})
print('Доменов в сводке:',len(sites))
# Unified site-level registry. Counts describe recorded URLs, not site-wide coverage.
catalog_by_host=collections.defaultdict(list)
for item in catalog:
 try:host=urllib.parse.urlsplit(item.get('url','')).hostname
 except ValueError:host=None
 if host:catalog_by_host[host.lower()].append(item)
for host in catalog_by_host:sites.setdefault(host,collections.Counter())
fields=['сайт','адреса_из_каталога','источники_каталога','записей_каталога','известных_URL','подтверждено_использование','сверено_частично','не_подтверждено_изучение','сохранено_HTML','процент_URL_с_подтверждённым_использованием','оценка_статуса','сведения_из_каталога','оговорки']
with (OUT/'единый-реестр-сайтов.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
 for host,c in sorted(sites.items(),key=lambda t:(-t[1]['всего'],t[0])):
  items=catalog_by_host.get(host,[]);n=c['всего'];read=c['Изучена (подтверждён факт использования)'];verified=c['Сверена с другим источником (частично)'];unknown=c['Не подтверждено изучение']
  if read+verified:status='Есть подтверждение использования отдельных URL; изучение сайта целиком не установлено'
  elif items:status='Есть описание в каталоге; изучение конкретных URL требует уточнения'
  else:status='Подтверждение изучения учтённых URL не найдено'
  notes=' | '.join(f"[{x.get('number')}] {x.get('name')}: {x.get('summary','')}" for x in items)
  w.writerow({'сайт':host,'адреса_из_каталога':' | '.join(x.get('url','') for x in items),'источники_каталога':' | '.join(f"[{x.get('number')}] {x.get('name')}" for x in items),'записей_каталога':len(items),'известных_URL':n,'подтверждено_использование':read,'сверено_частично':verified,'не_подтверждено_изучение':unknown,'сохранено_HTML':c['сохранено_HTML'],'процент_URL_с_подтверждённым_использованием':f'{100*(read+verified)/n:.1f}%' if n else 'нет данных','оценка_статуса':status,'сведения_из_каталога':notes,'оговорки':'Доля относится только к известным URL, не к сайту целиком; URL могут быть дублями и зеркалами, независимость не установлена. Сводка каталога может описывать иные страницы, чем основной URL.'})
print('Единый реестр сайтов:',len(sites),'доменов; исходных записей каталога:',sum(map(len,catalog_by_host.values())))

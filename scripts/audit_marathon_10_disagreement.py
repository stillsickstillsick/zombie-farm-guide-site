#!/usr/bin/env python3
"""Preserve documented disagreement on Spring Marathon quest 10."""
import json,pathlib
p=pathlib.Path(__file__).resolve().parents[1]/'data/quests.json';q=json.loads(p.read_text());x=next(x for x in q if x['slug']=='marafon-10');r=next(r for r in x['prior_records'] if r.get('original_id')=='bulk-moy-quest-3549');r['fields']['Расхождение с ZOMBIA']='В отдельной статье Zombie-island третья цель — получить 50 синих сердец; каталог ZOMBIA в другой записи той же карточки указывает 30. Принадлежность к конкретной версии и причина различия не установлены.';p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n');print('Explicitly annotated source discrepancy')

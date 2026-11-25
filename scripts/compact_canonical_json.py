#!/usr/bin/env python3
"""One JSON record per line, no value/image loss. Safe for existing ingest scripts."""
import json,os,tempfile
from pathlib import Path
P=Path(__file__).resolve().parents[1];files=['materials','buildings','collections','quests','locations','plants','zombies','eggs-trophies','updates','economy','glossary','sources'];before=after=0
for name in files:
 p=P/'data'/f'{name}.json'
 if not p.exists():continue
 raw=p.read_bytes();obj=json.loads(raw)
 if not isinstance(obj,list):raise ValueError(f'{name} is not a list')
 new=('[\n'+',\n'.join(json.dumps(x,ensure_ascii=False,separators=(',',':')) for x in obj)+'\n]\n').encode()
 if json.loads(new)!=obj:raise ValueError('roundtrip failure '+name)
 before+=len(raw);after+=len(new)
 if new!=raw:
  tmp=p.with_suffix('.json.tmp');tmp.write_bytes(new);os.replace(tmp,p)
print(f'canonical JSON {before} -> {after} bytes, saved {before-after} bytes')

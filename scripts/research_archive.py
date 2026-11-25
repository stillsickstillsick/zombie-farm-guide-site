#!/usr/bin/env python3
"""Read and verify the unpacked research files; transparently read images.json.gz."""
import argparse,sys,json,gzip,hashlib
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--list',action='store_true');p.add_argument('--verify',action='store_true');p.add_argument('--read',metavar='PATH');p.add_argument('--extract-all',metavar='DIRECTORY')
a=p.parse_args();root=Path(__file__).resolve().parents[1]/'research/history';checks=json.loads((root/'SHA256.json').read_text())
def read(name):
 if name not in checks:raise ValueError('Нет такого файла в перечне: '+name)
 path=(root/name).resolve()
 if not path.is_relative_to(root.resolve()):raise ValueError('Недопустимый путь')
 compressed=Path(str(path)+'.gz')
 if path.is_file():return path.read_bytes()
 if compressed.is_file():return gzip.decompress(compressed.read_bytes())
 raise FileNotFoundError(f'{name}: отсутствует в рабочей копии; см. research/LOCAL_STORAGE_NOTE.md для восстановления')
if a.verify:
 for name,h in checks.items():
  if hashlib.sha256(read(name)).hexdigest()!=h:raise ValueError('Ошибка SHA-256: '+name)
 print('Проверены по SHA-256 файлы исследований:',len(checks))
if a.list:
 for name in checks:print(name+' [gzip]' if Path(str(root/name)+'.gz').exists() else name)
if a.read:sys.stdout.buffer.write(read(a.read))
if a.extract_all:
 dest=Path(a.extract_all).resolve();dest.mkdir(parents=True,exist_ok=True)
 for name in checks:
  target=(dest/name).resolve()
  if not target.is_relative_to(dest):raise ValueError('Недопустимый путь')
  target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(read(name))
 print('Восстановлено файлов:',len(checks),'в',dest)
if not (a.list or a.verify or a.read or a.extract_all):p.print_help()

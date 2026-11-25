from pathlib import Path
import json
P=Path(__file__).resolve().parents[1]; path=P/'data/locations.json'; data=json.loads(path.read_text()); items={x['slug']:x for x in data}
rows=[
('zombicity-island-4168','https://www.youtube.com/watch?v=1luE-dqtcMs','Сбор звёзд на Зимнем лесу, ZombiCity, 20.01.2016','Предпросмотр видео показывает частично пройденную локацию и сбор звёзд. Начальная расстановка не подтверждена.'),
('zombicity-island-4209','https://www.youtube.com/watch?v=iuEIcyM4tsc','Поездка и обзор Королевства льда, ZombiCity, 30.01.2016','Предпросмотр видео показывает путь и покрытую снегом территорию; отдельные фрагменты острова видны после перехода. Степень расчистки и исходное состояние требуют проверки.'),
('zombicity-island-4210','https://www.youtube.com/watch?v=n0RizuTvhbI','Сквозь снег: Снежный Пик, Joker Game Klondike, 22.03.2016','Предпросмотр видео показывает разные фрагменты заснеженной игровой территории. Снято при прохождении продолжения квестов; исходная расстановка не подтверждена.'),
('ptichiy-dvor-2016','https://www.youtube.com/watch?v=UJK0FG3BwwA','Обзор Птичьего двора, ZombiCity, 27.04.2016','Предпросмотр видео показывает переход и фрагменты территории с растительностью и постройками. Состояние до первого посещения не установлено.'),
('gribnaya-polyana-2015','https://www.youtube.com/watch?v=DJWVk-nwHJs','Задания Грибников, ZombiCity, 26.09.2015','По предпросмотру основной упор на диалоги и задания грибников; не считать обзором исходной расстановки острова.'),
]
for slug,url,label,note in rows:
 x=items[slug]
 if not any(s.get('url')==url for s in x['sources']):x['sources'].append({'url':url,'label':label})
 id='video-research-'+slug
 if not any(r.get('original_id')==id for r in x['prior_records']):x['prior_records'].append({'original_id':id,'original_category':'Видео о локации','version':'браузерная социальная версия; сеть не уточнена','date':label.rsplit(', ',1)[-1], 'fields':{'Видео':note},'confidence':'Проверено название и выборочно миниатюры кадров, не полный просмотр. Видеозапись может показывать изменённую карту; исходные координаты не установлены.'})
path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')

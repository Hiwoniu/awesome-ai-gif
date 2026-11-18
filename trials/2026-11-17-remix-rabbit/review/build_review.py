from pathlib import Path
import sys, json, hashlib
from PIL import Image, ImageDraw
sys.path.insert(0,str(Path('skills/wechat-sticker/scripts').resolve()))
import gifkit
from check_assets import white_edge_ratio, loop_seam
ROOT=Path('trials/2026-11-17-remix-rabbit')
SOURCE=Path('trials/2026-11-16-codex-orange-cat')
plan=json.loads((ROOT/'_work/plan.json').read_text())
compare=Image.new('RGB',(480,240*9),'black')
metrics=[]
html=['<!doctype html><meta charset="utf-8"><title>Rabbit remix playback</title><style>body{background:#202020;color:#fff;font:16px sans-serif}section{display:inline-block;margin:8px;vertical-align:top}img{background:black;width:240px;height:240px}h2{font-size:16px}</style><h1>Orange cat / Rabbit</h1>']
for row,item in enumerate(plan['items']):
    name=item['name']
    old,od,oi=gifkit.read_gif(SOURCE/name/'result.gif')
    new,nd,ni=gifkit.read_gif(ROOT/name/'result.gif')
    for col,frame in enumerate((old[0],new[0])):
        compare.paste(gifkit.flatten(frame,(0,0,0)),(col*240,row*240))
    seq=Image.new('RGB',(240*max(len(old),len(new)),480),'black')
    for y,fs in enumerate((old,new)):
        for x,f in enumerate(fs): seq.paste(gifkit.flatten(f,(0,0,0)),(x*240,y*240))
    seq.save(ROOT/'review'/f'{name}-frames.png')
    if name=='wx-009-wave': seq.save(ROOT/'review/wave-frames.png')
    stat=dict(name=name,route=item['route'],original_frames=len(old),new_frames=len(new),original_durations_ms=od,new_durations_ms=nd,original_total_ms=sum(od),new_total_ms=sum(nd),original_loop=oi.get('loop'),new_loop=ni.get('loop'),bytes=(ROOT/name/'result.gif').stat().st_size,motion=item.get('motion'),original_boxes=[f.getchannel('A').getbbox() for f in old],new_boxes=[f.getchannel('A').getbbox() for f in new],max_white_edge_ratio=max(white_edge_ratio(f) or 0 for f in new),opaque_near_white_min=min(sum(1 for r,g,b,a in f.getdata() if a>=128 and min(r,g,b)>=240) for f in new))
    if item['route']=='frames':stat.update(original_loop_seam=loop_seam(old),new_loop_seam=loop_seam(new))
    metrics.append(stat)
    html.append(f'<section><h2>{name}</h2><img src="../../2026-11-16-codex-orange-cat/{name}/result.gif"><img src="../{name}/result.gif"></section>')
compare.save(ROOT/'review/compare.png')
(ROOT/'review/metrics.json').write_text(json.dumps(metrics,ensure_ascii=False,indent=2)+'\n')
(ROOT/'review/playback.html').write_text('\n'.join(html))
assets=Image.new('RGB',(750,680),(0,0,0))
for name,xy in [('cover',(0,0)),('icon',(270,0)),('banner',(0,280))]:
    im=Image.open(ROOT/'assets'/f'{name}.png').convert('RGBA')
    if name=='icon':im=im.resize((200,200),Image.Resampling.NEAREST)
    assets.paste(im,xy,im)
assets.save(ROOT/'review/assets-black.png')
for m in metrics:
    print(m['name'],m['original_frames'],m['new_frames'],m['original_durations_ms'],m['new_durations_ms'],'white_edge',round(m['max_white_edge_ratio'],3),'white_body_min',m['opaque_near_white_min'])

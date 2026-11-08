import importlib.metadata as md
import json
import shutil
import sys
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from atlante.icons import svg_source
from atlante.sections import section_color
data=json.loads((ROOT/'atlante/data/catalog.json').read_text(encoding='utf-8'))
icons_dir=ROOT/'atlante/assets/icons';icons_dir.mkdir(parents=True,exist_ok=True)
for section in data['sections']:
    (icons_dir/(section['id']+'.svg')).write_text(svg_source(section['icon'],section_color(section['id'])),encoding='utf-8')
assets=ROOT/'atlante/assets';assets.mkdir(exist_ok=True)
im=Image.new('RGBA',(256,256),(0,0,0,0));draw=ImageDraw.Draw(im)
draw.rounded_rectangle((4,4,252,252),radius=48,fill='#147d84')
# Sigma costruita geometricamente: nessun font di sistema nel pacchetto.
draw.line([(180,65),(75,65),(128,128),(75,191),(180,191)],fill='#e8ffff',width=15,joint='curve')
im.save(assets/'atlante.ico',sizes=[(16,16),(32,32),(48,48),(128,128),(256,256)])
licenses=ROOT/'LICENZE';licenses.mkdir(exist_ok=True)
summary=[]
for dist in md.distributions():
    name=dist.metadata.get('Name','unknown');row={'name':name,'version':dist.version,'license':dist.metadata.get('License-Expression') or dist.metadata.get('License',''),'home':dist.metadata.get('Home-page','')}
    summary.append(row)
    for item in dist.files or []:
        if ('license' in item.name.lower() or 'copying' in item.name.lower()) and item.suffix.lower() not in ('.py','.pyc'):
            src=Path(dist.locate_file(item))
            if src.is_file():
                dest=licenses/name/item.name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
for name in ('mathjax','@mathjax/mathjax-newcm-font'):
    folder=ROOT/'vendor/node_modules'/name
    dest=licenses/name.replace('/','-');dest.mkdir(exist_ok=True)
    for p in folder.glob('*'):
        if p.is_file() and (p.name.lower().startswith(('license','copying')) or p.name=='package.json'):shutil.copy2(p,dest/p.name)
(licenses/'dipendenze.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print('Icona e licenze preparate.')

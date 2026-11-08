import json
import subprocess
import sys
from pathlib import Path
import pytest
from PyQt6.QtCore import Qt,QByteArray
from PyQt6.QtGui import QImage,QPainter
from PyQt6.QtSvg import QSvgRenderer
from atlante.paths import ROOT
from atlante.icons import PATHS,svg_source,icon

DATA=json.loads((ROOT/'atlante/data/catalog.json').read_text(encoding='utf-8'))

def test_no_personal_degree_interface_or_data():
    raw=(ROOT/'atlante/data/catalog.json').read_text(encoding='utf-8')
    assert '"courses"' not in raw and '"curriculum_sources"' not in raw
    for filename in ('ui.py','render.py','store.py'):
        text=(ROOT/'atlante'/filename).read_text(encoding='utf-8')
        assert '3+2' not in text and 'Uniroma5' not in text and 'LM-32' not in text
    assert sum(s['count'] for s in DATA['sections'])==len(DATA['cards'])==988
    assert len({s['icon'] for s in DATA['sections']})==len(DATA['sections'])==36

@pytest.mark.parametrize('section',DATA['sections'],ids=lambda s:s['id'])
def test_subject_icons_visible(section,qapp):
    from atlante.sections import section_color
    assert section['icon'] in PATHS
    for dark in (False,True):
        renderer=QSvgRenderer(QByteArray(svg_source(section['icon'],section_color(section['id'],dark)).encode()))
        assert renderer.isValid()
        raster=QImage(48,48,QImage.Format.Format_ARGB32);raster.fill(Qt.GlobalColor.transparent);painter=QPainter(raster);renderer.render(painter);painter.end()
        visible=sum(raster.pixelColor(x,y).alpha()>0 for x in range(48) for y in range(48))
        assert visible>100,(section['id'],visible)
        assert not icon(section['icon'],section_color(section['id'],dark)).isNull()

@pytest.mark.parametrize('card',[c for c in DATA['cards'] if c.get('code_example')],ids=lambda c:c['id'])
def test_runnable_programming_examples(card):
    source=card['code_example']['source'];compile(source,card['id'],'exec')
    run=subprocess.run([sys.executable,'-I','-c',source],capture_output=True,text=True,timeout=3)
    assert run.returncode==0,run.stderr

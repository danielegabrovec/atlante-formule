import json
import pytest
from atlante.paths import ROOT
from atlante.engine import numeric
from atlante.plots import PlotWidget,sample_curve

CARDS=json.loads((ROOT/'atlante/data/catalog.json').read_text(encoding='utf-8'))['cards']

def test_all_geometry_figures(qtbot):
    plot=PlotWidget();qtbot.addWidget(plot);plot.resize(900,650)
    failures=[]
    for card in [c for c in CARDS if c['category'] in ('classica','analitica')]:
        plot.set_card(card)
        if plot.caption.text().startswith('Controlla'):failures.append((card['id'],plot.caption.text()))
    assert not failures,failures

def test_triangle_figures_match_formula_parameters(qtbot):
    import math
    import numpy as np
    cards={c['id']:c for c in CARDS};plot=PlotWidget();qtbot.addWidget(plot)
    plot.set_card(cards['classica-013'])
    line=next(line for line in plot.figure.axes[0].lines if line.get_label()=='mediana AM')
    x,y=line.get_data();assert math.hypot(x[-1]-x[0],y[-1]-y[0])==pytest.approx(4)
    plot.set_card(cards['classica-015'])
    line=next(line for line in plot.figure.axes[0].lines if line.get_label()=='mediana AM')
    x,y=line.get_data();assert math.hypot(x[-1]-x[0],y[-1]-y[0])==pytest.approx(9)
    plot.set_card(cards['classica-014'])
    line=next(line for line in plot.figure.axes[0].lines if line.get_label()=='bisettrice AD')
    x,y=line.get_data();D=np.array([x[-1],y[-1]]);B=np.array([6.,0.]);C=np.array([2.,2*math.sqrt(3)])
    assert np.linalg.norm(B-D)/np.linalg.norm(D-C)==pytest.approx(1.5)

@pytest.mark.parametrize('card',[c for c in CARDS if c.get('plot',{} ) and c['plot']['kind']=='sensitivity'],ids=lambda c:c['id'])
def test_sensitivity_samples(card):
    key=card['plot']['variable'];values={f['name']:numeric(f['default']) for f in card['calculator']['inputs']}
    value=values.pop(key)
    low,high=(value*.75,value*1.25) if value>0 else (value-1,value+1)
    x,y=sample_curve(card['calculator']['expression'],key,low,high,points=150,names=values)
    assert len(x)==len(y)==150

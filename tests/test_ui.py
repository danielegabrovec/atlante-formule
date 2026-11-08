import json
import os
from pathlib import Path
import pytest
from PyQt6.QtCore import Qt,QTimer
from PyQt6.QtWidgets import QApplication
QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
from atlante.ui import MainWindow,Editor
from atlante.render import FormulaView
from atlante.jobs import Jobs
from atlante.paths import ROOT

@pytest.fixture
def window(qtbot,tmp_path,monkeypatch):
    monkeypatch.setenv('ATLANTE_DATA_DIR',str(tmp_path))
    w=MainWindow();qtbot.addWidget(w);w.show();qtbot.waitExposed(w)
    w.pages.setCurrentIndex(0)
    yield w
    w.close()

def js(qtbot,view,code):
    result=[];view.page().runJavaScript(code,result.append);qtbot.waitUntil(lambda:bool(result),timeout=20000);return result[0]

def wait_math(qtbot,view):
    state=[]
    def check():
        result=js(qtbot,view,"document.documentElement.dataset.mathReady === 'true' && document.documentElement.dataset.renderId === '"+str(view.generation)+"'")
        return result is True
    qtbot.waitUntil(check,timeout=60000)

def test_formula_offline_all_catalog(window,qtbot):
    from html import escape
    view=window.formula
    body='<h1>Verifica formule del catalogo</h1>'+''.join('<div data-card="'+c['id']+'">\\['+escape(c['latex'])+'\\]</div>' for c in window.store.catalog)
    view.show_body(body);wait_math(qtbot,view)
    errors=js(qtbot,view,"Array.from(document.querySelectorAll('[data-mml-node=\"merror\"]')).map(x=>x.closest('[data-card]').dataset.card+' '+x.textContent)")
    assert not errors,errors
    assert js(qtbot,view,"document.querySelectorAll('mjx-container').length")==len(window.store.catalog)

def test_calculator_notes_search_theme(window,qtbot):
    w=window;w.show_card(w.store.by_id['classica-008']);w.tabs.setCurrentIndex(1)
    w.calc_inputs['a'].setText('300 cm');w.compute_card()
    qtbot.waitUntil(lambda:w.calc_result.text()=='5 m',timeout=20000)
    assert w.plot.inputs['a']==3
    w.notes.setPlainText('Nota con formula: a²+b²=c².');w.show_card(w.store.by_id['base-001'])
    assert w.store.note('classica-008').startswith('Nota')
    w.notes.setPlainText('Nota prima del filtro.');w.refresh();assert w.store.note('base-001')=='Nota prima del filtro.'
    w.show_card(w.store.by_id['classica-008']);w.favorite();assert 'classica-008' in w.store.favorites
    w.toggle_theme();assert w.dark
    w.search.setText('pitagroa');w.refresh();assert w.list.item(0).data(Qt.ItemDataRole.UserRole)['id']=='classica-008'
    w.search.clear();w.refresh();w.show_card(w.store.by_id['analisi-010']);w.show_card(w.store.by_id['classica-008'])
    qtbot.wait(200)

def test_job_cancel_stale_and_error(qtbot):
    job=Jobs();results=[];errors=[];job.done.connect(results.append);job.failed.connect(errors.append)
    job.start({'operation':'integrale','expression':'exp(x^3)*sin(x^5)'})
    job.cancel();qtbot.wait(150);assert not results
    job.start({'operation':'derivata','expression':'x^2'})
    qtbot.waitUntil(lambda:bool(results),timeout=20000);assert results[-1]['text']=='2*x'
    job.start({'operation':'derivata','expression':"__import__('os')"})
    qtbot.waitUntil(lambda:bool(errors),timeout=20000)
    job.start({'operation':'integrale','expression':'exp(x^3)*sin(x^5)'})
    job.timer.start(50);qtbot.waitUntil(lambda:len(errors)>1,timeout=3000)
    assert '15 secondi' in errors[-1]

def test_graph_worker_pipeline(window,qtbot):
    window.lab_plot.set_function('1/x','x',-2,2)
    qtbot.waitUntil(lambda:window.lab_plot.caption.text().startswith('Grafico reale'),timeout=15000)
    window.operation.setCurrentText('superficie 3D');window.expression.setPlainText('x^2+y^2');window.lab_a.setText('-2');window.lab_b.setText('2');window.compute_lab()
    qtbot.waitUntil(lambda:window.lab_plot.caption.text().startswith('Superficie'),timeout=15000)

def test_personal_editor_roundtrip(window,qtbot):
    dialog=Editor(window,window.store.by_id['classica-008'],duplicate=True);qtbot.addWidget(dialog)
    dialog.fields['title'].setText('Pitagora — appunti personali');dialog.save()
    assert window.store.search('appunti personali',category='personali')
    dialog2=Editor(window,window.store.by_id['programmazione-001'],duplicate=True);qtbot.addWidget(dialog2);dialog2.save()
    copies=[c for c in window.store.cards if c['category']=='personali' and c.get('code_example')]
    assert copies and 'class Counter' in copies[0]['code_example']['source']

def test_visual_screenshots(window,qtbot):
    out=ROOT/'verifiche';out.mkdir(exist_ok=True);w=window
    w.show_card(w.store.by_id['classica-008']);wait_math(qtbot,w.formula);w.grab().save(str(out/'01-formula-chiaro.png'))
    w.tabs.setCurrentIndex(2);qtbot.wait(250);w.grab().save(str(out/'02-geometria.png'))
    w.toggle_theme();w.tabs.setCurrentIndex(0);wait_math(qtbot,w.formula);w.grab().save(str(out/'03-formula-scuro.png'))
    w.open_lab();w.operation.setCurrentText('equazione');w.expression.setPlainText('x^2-5*x+6=0');w.compute_lab()
    qtbot.waitUntil(lambda:'Delta' in w.lab_result.last_body or 'Δ' in w.lab_result.last_body,timeout=20000);wait_math(qtbot,w.lab_result);w.grab().save(str(out/'04-laboratorio.png'))
    w.resize(1110,720);qtbot.wait(300);w.grab().save(str(out/'05-finestra-compatta.png'))

def test_sections_and_logic_ui(window,qtbot):
    w=window;w.open_section('bool')
    assert {w.list.item(i).data(Qt.ItemDataRole.UserRole)['category'] for i in range(w.list.count())}=={'bool'}
    w.show_card(w.store.by_id['bool-008']);w.transfer_lab();assert w.operation.currentText()=='equivalenza booleana';w.compute_lab()
    assert w.list.currentItem().data(Qt.ItemDataRole.UserRole)['id']=='bool-008'
    assert 'XOR' in w.syntax_label.text() and not w.variables.isVisible()
    qtbot.waitUntil(lambda:'Le espressioni sono equivalenti.' in w.lab_result.last_body,timeout=15000)
    assert '<table>' in w.lab_result.last_body
    wait_math(qtbot,w.lab_result);w.grab().save(str(ROOT/'verifiche/06-logica-equivalenza.png'))
    w.operation.setCurrentText('mappa di Karnaugh');w.expression.setPlainText('(A & B) | (~A & C)');w.compute_lab()
    qtbot.waitUntil(lambda:'Mappa di Karnaugh' in w.lab_result.last_body,timeout=15000);wait_math(qtbot,w.lab_result);w.grab().save(str(ROOT/'verifiche/07-karnaugh.png'))
    w.open_section('digitale');w.show_card(w.store.by_id['digitale-011']);wait_math(qtbot,w.formula);w.grab().save(str(ROOT/'verifiche/08-digitale-colori.png'))

def test_home_icons_and_subject_navigation(window,qtbot):
    w=window;w.open_home();assert w.pages.currentIndex()==2
    assert len(w.home_buttons)==36 and all(not b.icon().isNull() for b in w.home_buttons.values())
    w.area_filter.setCurrentText('Informatica');qtbot.wait(200);w.grab().save(str(ROOT/'verifiche/09-sezioni-informatica.png'))
    qtbot.mouseClick(w.home_buttons['basi_dati'],Qt.MouseButton.LeftButton)
    assert w.category=='basi_dati' and w.list.count()==18
    w.open_section('programmazione');w.show_card(w.store.by_id['programmazione-001']);wait_math(qtbot,w.formula)
    assert '<pre><code>' in w.formula.last_body
    w.grab().save(str(ROOT/'verifiche/10-programmazione.png'))
    w.open_home();w.toggle_theme();w.grab().save(str(ROOT/'verifiche/11-sezioni-tema.png'))

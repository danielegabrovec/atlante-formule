"""Richiamato dall'app con --qa-report: prova i processi dell'EXE windowed."""
import json
import sys
from datetime import datetime,timezone
from pathlib import Path
from PyQt6.QtCore import QTimer

def begin(window,app,path):
    report={'errors':[],'frozen':bool(getattr(sys,'frozen',False)),'executable':sys.executable,'utc':datetime.now(timezone.utc).isoformat(),'catalog_size':len(window.store.catalog)};output=Path(path);output.parent.mkdir(parents=True,exist_ok=True)
    report['sections']=len(window.store.sections)==36 and len(window.home_buttons)==36
    report['icons']=all(not button.icon().isNull() for button in window.home_buttons.values()) and len({s['icon'] for s in window.store.sections})==36
    def finish():
        report['ok']=bool(not report['errors'] and report.get('calculator') and report.get('symbolic') and report.get('mathjax') and report.get('boolean') and report.get('karnaugh') and report.get('integer64') and report.get('sections') and report.get('icons') and report.get('section_navigation') and report['catalog_size']==988)
        output.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');window.close();app.quit()
    def fail(message):report['errors'].append(message);finish()
    window.jobs.failed.connect(fail)
    def home():
        window.open_home();window.area_filter.setCurrentText('Informatica');window.grab().save(str(output.with_name('exe-sezioni.png')))
        window.home_buttons['basi_dati'].click();report['section_navigation']=window.category=='basi_dati' and window.list.count()==18
        window.show_card(window.store.by_id['classica-008'])
    def mathcheck(state):
        report['mathjax']=bool(state and state.get('ready') and state.get('count')==1 and state.get('errors')==0)
        if not report['mathjax']:report['errors'].append('Rendering MathJax non completo: '+str(state))
        window.show_card(window.store.by_id['classica-008']);window.pending_kind='calculator'
        window.jobs.done.connect(calculated);window.compute_card()
    def calculated(result):
        window.jobs.done.disconnect(calculated);report['calculator']=abs(result.get('value',0)-5)<1e-10
        window.tabs.setCurrentIndex(2);window.grab().save(str(output.with_name('exe-geometria.png')))
        window.show_card(window.store.by_id['digitale-009']);window.calc_inputs['n'].setText('64');window.jobs.done.connect(binary);window.compute_card()
    def binary(result):
        window.jobs.done.disconnect(binary);report['integer64']=result.get('exact')=='18446744073709551615'
        window.open_lab();window.operation.setCurrentText('equazione');window.expression.setPlainText('x^2-5*x+6=0');window.jobs.done.connect(symbolic);window.compute_lab()
    def symbolic(result):
        window.jobs.done.disconnect(symbolic);report['symbolic']=result.get('text')=='{2, 3}'
        window.operation.setCurrentText('equivalenza booleana');window.expression.setPlainText('~(A & B); ~A | ~B');window.jobs.done.connect(boolean);window.compute_lab()
    def boolean(result):
        window.jobs.done.disconnect(boolean);report['boolean']=result.get('equivalent') is True and len(result.get('table',{}).get('rows',[]))==4
        window.operation.setCurrentText('mappa di Karnaugh');window.expression.setPlainText('(A & B) | (~A & C)');window.jobs.done.connect(karnaugh);window.compute_lab()
    def karnaugh(result):
        window.jobs.done.disconnect(karnaugh);report['karnaugh']=result.get('kmap',{}).get('columns')==['00','01','11','10']
        QTimer.singleShot(2000,lambda:(window.grab().save(str(output.with_name('exe-laboratorio.png'))),finish()))
    def inspect():window.formula.page().runJavaScript('({ready:document.documentElement.dataset.mathReady==="true",count:document.querySelectorAll("mjx-container").length,errors:document.querySelectorAll("[data-mml-node=merror]").length})',mathcheck)
    QTimer.singleShot(1800,home);QTimer.singleShot(7000,inspect)
    QTimer.singleShot(45000,lambda:fail('Timeout della verifica pacchetto.'))

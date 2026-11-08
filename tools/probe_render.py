import sys,json
import traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer,Qt
print('Qt importato',flush=True)
QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
from atlante.ui import MainWindow
print('UI importata',flush=True)
app=QApplication(['AtlanteProbe'])
print('QApplication creata',flush=True)
def hook(typ,value,tb):
    text=''.join(traceback.format_exception(typ,value,tb));Path('verifiche/probe-error.txt').write_text(text,encoding='utf-8');print(text,flush=True)
sys.excepthook=hook
w=MainWindow();w.show()
print('Finestra visibile',flush=True)
def probe():
    w.formula.page().runJavaScript('JSON.stringify({ready:document.documentElement.dataset.mathReady,error:document.documentElement.dataset.mathError,mjx:document.querySelectorAll("mjx-container").length,math:typeof MathJax,body:document.body.innerText.slice(0,120)})',done)
def done(data):
    print(data,flush=True);w.close();app.quit()
QTimer.singleShot(8000,probe);QTimer.singleShot(20000,app.quit)
app.exec()

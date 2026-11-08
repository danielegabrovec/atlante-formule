import json
import sys
import tempfile
from pathlib import Path
from PyQt6.QtCore import QObject,QProcess,QTimer,pyqtSignal
from atlante.paths import ROOT

class Jobs(QObject):
    done=pyqtSignal(dict)
    failed=pyqtSignal(str)
    busy=pyqtSignal(bool)
    def __init__(self,parent=None):
        super().__init__(parent);self.process=None;self.generation=0;self.workdir=None
        self.timer=QTimer(self);self.timer.setSingleShot(True);self.timer.timeout.connect(self.timeout)
    def start(self,request):
        self.cancel();self.generation+=1;generation=self.generation
        proc=QProcess(self);self.process=proc
        self.workdir=tempfile.TemporaryDirectory(prefix='atlante-job-');job=Path(self.workdir.name)
        (job/'request.json').write_text(json.dumps(request,ensure_ascii=True),encoding='utf-8')
        proc.setProgram(sys.executable)
        proc.setArguments((['--worker'] if getattr(sys,'frozen',False) else [str(ROOT/'main.py'),'--worker'])+['--job',str(job)])
        proc.finished.connect(lambda code,status:self.finished(proc,generation,code))
        proc.errorOccurred.connect(lambda error:self.error(proc,generation))
        self.busy.emit(True);proc.start();self.timer.start(15000)
    def send(self,proc,request):
        proc.write(json.dumps(request,ensure_ascii=True).encode('utf-8'));proc.closeWriteChannel()
    def finished(self,proc,generation,code):
        if generation!=self.generation:return
        self.timer.stop();self.process=None;self.busy.emit(False)
        try:
            payload=json.loads((Path(self.workdir.name)/'response.json').read_text(encoding='utf-8'))
            self.cleanup()
            if payload.get('ok'):self.done.emit(payload['result'])
            else:self.failed.emit(payload.get('error','Calcolo non riuscito.'))
        except Exception:
            self.cleanup();self.failed.emit('Processo di calcolo terminato senza un risultato leggibile.')
        proc.deleteLater()
    def cleanup(self):
        if self.workdir:self.workdir.cleanup();self.workdir=None
    def error(self,proc,generation):
        if generation==self.generation and proc.error()==QProcess.ProcessError.FailedToStart:
            self.timer.stop();self.process=None;self.busy.emit(False);self.failed.emit('Impossibile avviare il processo di calcolo.');self.cleanup();proc.deleteLater()
    def timeout(self):
        self.cancel();self.failed.emit('Tempo massimo di 15 secondi raggiunto. Riduci la complessità o l’intervallo del problema.')
    def cancel(self):
        self.generation+=1;self.timer.stop()
        if self.process:
            proc=self.process;self.process=None
            proc.kill();proc.waitForFinished(1000);proc.deleteLater()
        self.cleanup()
        self.busy.emit(False)

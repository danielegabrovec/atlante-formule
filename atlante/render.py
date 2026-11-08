"""Documento locale: MathJax, font e script non richiedono connessioni."""
import html
import json
from PyQt6.QtGui import QColor
from PyQt6.QtCore import QUrl,pyqtSignal
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage,QWebEngineSettings,QWebEngineUrlRequestInterceptor
from atlante.paths import ROOT
from atlante.sections import section_color

class LocalOnly(QWebEngineUrlRequestInterceptor):
    def interceptRequest(self,info):
        if info.requestUrl().scheme() not in ('file','data','qrc','about','blob'):
            info.block(True)

class Page(QWebEnginePage):
    linked=pyqtSignal(str)
    def acceptNavigationRequest(self,url,kind,main):
        if url.scheme()=='atlas':self.linked.emit(url.path().strip('/'));return False
        if kind==QWebEnginePage.NavigationType.NavigationTypeLinkClicked:
            # I riferimenti si aprono solo dopo un'azione esplicita sull'apposito bottone Qt.
            return False
        return url.scheme() in ('file','data','about','qrc')

class FormulaView(QWebEngineView):
    ready=pyqtSignal()
    def __init__(self,parent=None):
        super().__init__(parent)
        self.local_page=Page(self);self.setPage(self.local_page)
        self.blocker=LocalOnly(self);self.page().profile().setUrlRequestInterceptor(self.blocker)
        self.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls,False)
        self.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls,True)
        self.settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows,False)
        self.setContextMenuPolicy(__import__('PyQt6.QtCore',fromlist=['Qt']).Qt.ContextMenuPolicy.NoContextMenu)
        self.dark=False;self.font_size=16;self.last_body='';self.html_source='';self.generation=0;self.section='personali'
    def show_body(self,body):
        self.last_body=body
        self.generation+=1
        bg='#111d2b' if self.dark else '#ffffff';fg='#e9f1f5' if self.dark else '#203446'
        self.page().setBackgroundColor(QColor(bg))
        accent=section_color(self.section,self.dark)
        muted='#b0c4d3' if self.dark else '#526679';panel='#192d3b' if self.dark else '#eff7f7'
        script=(ROOT/'vendor/node_modules/mathjax/tex-svg.js').as_uri()
        font=(ROOT/'vendor/node_modules/@mathjax/mathjax-newcm-font').as_uri()
        loader=(ROOT/'vendor/node_modules/mathjax').as_uri()
        config={'loader':{'paths':{'mathjax':loader,'mathjax-newcm':font}},
                'tex':{'inlineMath':[['\\(','\\)']],'displayMath':[['\\[','\\]']],'packages':{'[+]':[]}},
                'svg':{'fontCache':'local','fontPath':font+'/svg'},
                'options':{'enableMenu':False},'startup':{'typeset':True}}
        jsconfig=json.dumps(config)
        self.html_source=f'''<!doctype html><html lang="it" data-render-id="{self.generation}"><head><meta charset="utf-8">
        <meta http-equiv="Content-Security-Policy" content="default-src 'self' file: data:; script-src 'unsafe-inline' 'unsafe-eval' file:; worker-src blob: file:; style-src 'unsafe-inline' file:; img-src file: data:; font-src file: data:; connect-src file:;">
        <style>body{{background:{bg};color:{fg};font:{self.font_size}px 'Segoe UI',sans-serif;margin:0;padding:28px 36px;line-height:1.75;}}
        h1{{font-size:29px;line-height:1.25;letter-spacing:-.5px;margin:6px 0 18px}}h2{{font-size:17px;margin:28px 0 9px;color:{fg}}}
        p{{margin:8px 0 14px;max-width:78ch}}.eyebrow{{color:{accent};font-size:12px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase}}
        .formula{{background:{panel};border-left:4px solid {accent};border-radius:8px;padding:16px 22px;margin:22px 0;overflow-x:auto;font-size:1.2em;}}
        .muted{{color:{muted}}}.condition{{padding:12px 16px;border:1px solid #718e9455;border-radius:8px;background:{panel}}}
        .example{{padding:14px 18px;border-left:3px solid #c59541;background:{panel};border-radius:5px}}
        .badge{{font-size:12px;background:{panel};padding:4px 10px;border-radius:12px;color:{muted};margin-right:6px}}
        .section-badge{{color:{accent};border:1px solid {accent};background:transparent}}table{{border-collapse:collapse;margin:12px 0 24px;min-width:240px}}th,td{{border:1px solid #7b96a466;padding:8px 14px;text-align:center}}th{{background:{panel};color:{accent}}}tr:nth-child(even){{background:{panel}}}
        pre{{background:{panel};border:1px solid #7b96a444;border-radius:8px;padding:16px;overflow-x:auto;line-height:1.55;}}pre code{{font:14px Consolas,monospace;}}
        a{{color:#12858a}}li{{margin:7px 0}}code{{font-family:Consolas,monospace}}mjx-container[jax="SVG"]{{max-width:none!important}}
        ::selection{{background:#b6e6e5;color:#15343b}}::-webkit-scrollbar{{width:9px;height:9px}}::-webkit-scrollbar-thumb{{background:#78909b77;border-radius:6px}}
        </style><script>window.MathJax={jsconfig}; window.MathJax.startup.pageReady=()=>MathJax.startup.defaultPageReady().then(()=>{{document.documentElement.dataset.mathReady='true'}}).catch(e=>{{document.documentElement.dataset.mathError=String(e)}});</script>
        <script defer src="{script}"></script></head><body>{body}</body></html>'''
        self.setHtml(self.html_source,QUrl.fromLocalFile(str(ROOT)+ '/'))
    def card(self,c):
        e=html.escape
        self.section=c.get('category','personali')
        body=f'<div class="eyebrow">{e(c["category_label"])}</div><h1>{e(c["title"])}</h1><span class="badge">{e(c["level"])}</span>'
        body+=f'<span class="badge section-badge">{e(c.get("topic",c["category_label"]))}</span>'
        if c.get('calculator'):body+='<span class="badge">Calcolatore</span>'
        if c.get('plot'):body+='<span class="badge">Visualizzazione</span>'
        if c.get('logic'):body+='<span class="badge">Logica · tabelle di verità</span>'
        if c.get('kind')=='concetto':body+='<span class="badge">Concetto</span>'
        body+=f'<div class="formula">\\[{e(c["latex"])}\\]</div><h2>Come si interpreta</h2><p>{e(c["explanation"])}</p><h2>Simboli e unità</h2><p class="muted">{e(c["symbols"])}</p>'
        if c.get('calculator'):
            body+='<ul>'+''.join(f'<li><strong>{e(f["name"])}</strong> — {e(f["label"])}{(" · "+e(f["unit"])) if f["unit"] else ""}</li>' for f in c['calculator']['inputs'])+'</ul>'
        body+=f'<h2>Condizioni di validità</h2><div class="condition">{e(c["conditions"])}</div><h2>Esempio svolto</h2><div class="example">{e(c["example"])}</div>'
        if c.get('code_example'):
            code=c['code_example'];body+='<h2>Esempio di codice · '+e(code.get('language',''))+'</h2><pre><code>'+e(code['source'])+'</code></pre>'
        if c.get('prerequisites'):body+='<h2>Prerequisiti</h2><p class="muted">'+e(c['prerequisites'])+'</p>'
        if c.get('sources'):
            body+='<h2>Per approfondire</h2><p class="muted">'+ '<br>'.join(e(r['title']) for r in c['sources'])+'</p><p class="muted">I riferimenti online sono facoltativi: usa il pulsante «Fonti» per aprirli nel browser.</p>'
        self.show_body(body)
    def result(self,res):
        e=html.escape
        self.section='bool' if res.get('table') else 'ottimizzazione'
        body='<div class="eyebrow">Laboratorio · risultato</div><h1>Dal problema alla soluzione</h1>'
        body+=f'<div class="formula">\\[{e(res["latex"])}\\]</div>'
        if res.get('unresolved'):body+='<div class="condition">Il motore ha lasciato una forma non risolta: non è una soluzione esplicita completa.</div>'
        body+='<h2>Procedimento</h2><ol>'+''.join(f'<li>{e(v)}</li>' for v in res.get('steps',[]))+'</ol>'
        if res.get('kmap'):
            k=res['kmap'];body+='<h2>Mappa di Karnaugh · ordine Gray</h2><p>Righe: '+e(k['row_variables'])+' · Colonne: '+e(k['column_variables'])+'</p>'
            body+='<table><thead><tr><th></th>'+''.join('<th>'+e(c)+'</th>' for c in k['columns'])+'</tr></thead><tbody>'
            body+=''.join('<tr><th>'+e(label)+'</th>'+''.join('<td>'+str(v)+'</td>' for v in row)+'</tr>' for label,row in zip(k['rows'],k['values']))+'</tbody></table>'
        if res.get('table'):
            t=res['table'];body+='<h2>Tabella di verità</h2><table><thead><tr>'+''.join('<th>'+e(h)+'</th>' for h in t['headers'])+'</tr></thead><tbody>'
            body+=''.join('<tr>'+''.join('<td>'+str(v)+'</td>' for v in row)+'</tr>' for row in t['rows'])+'</tbody></table>'
        body+=f'<h2>Condizioni e lettura del risultato</h2><p>{e(res.get("conditions",""))}</p>'
        self.show_body(body)

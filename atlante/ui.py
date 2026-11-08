import html
import json
import os
import sys
from pathlib import Path
from PyQt6.QtCore import Qt,QTimer,QSize,QUrl,QByteArray,pyqtSignal
from PyQt6.QtGui import QFont,QIcon,QPixmap,QPainter,QColor,QAction,QKeySequence,QDesktopServices,QPalette
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtWidgets import (QApplication,QMainWindow,QWidget,QLabel,QLineEdit,QPushButton,QToolButton,
    QVBoxLayout,QHBoxLayout,QGridLayout,QFormLayout,QSplitter,QTreeWidget,QTreeWidgetItem,QListWidget,QListWidgetItem,
    QTabWidget,QStackedWidget,QComboBox,QSpinBox,QDoubleSpinBox,QPlainTextEdit,QScrollArea,QDialog,
    QDialogButtonBox,QMessageBox,QFileDialog,QMenu,QFrame,QAbstractItemView,QStyledItemDelegate,QStyle)
from atlante.store import Store
from atlante.render import FormulaView
from atlante.jobs import Jobs
from atlante.plots import PlotWidget
from atlante.paths import ROOT,user_dir
from atlante.sections import section_color,family

from atlante.icons import icon

def button(text,callback=None,name=None):
    b=QPushButton(text)
    if not name:name={'Calcola risultato':'calculator','Esegui':'lab','Annulla':'stop','Valori iniziali':'reset','Chiudi':'arrow'}.get(text)
    if name:b.setIcon(icon(name))
    if callback:b.clicked.connect(callback)
    b.setCursor(Qt.CursorShape.PointingHandCursor)
    return b

class CardsDelegate(QStyledItemDelegate):
    def paint(self,p,option,index):
        card=index.data(Qt.ItemDataRole.UserRole)
        if not card:return
        dark=self.parent().property('dark') or False
        selected=bool(option.state & QStyle.StateFlag.State_Selected)
        rect=option.rect.adjusted(4,4,-4,-4);p.save();p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(QColor('#21878d' if selected else '#33485a' if dark else '#e1e9ed'));p.setBrush(QColor('#163e4b' if dark and selected else '#e9f5f4' if selected else '#162535' if dark else '#ffffff'));p.drawRoundedRect(rect,8,8)
        accent=QColor(section_color(card['category'],dark));p.setPen(Qt.PenStyle.NoPen);p.setBrush(accent);p.drawRoundedRect(rect.adjusted(1,6,-rect.width()+5,-6),2,2)
        titlefont=QFont('Segoe UI',10);titlefont.setWeight(QFont.Weight.DemiBold);p.setFont(titlefont);p.setPen(QColor('#e6f0f4' if dark else '#223d4c'))
        p.drawPixmap(rect.x()+13,rect.y()+10,21,21,icon(card.get('section_icon','notes'),accent.name()).pixmap(32,32))
        tr=rect.adjusted(40,10,-10,-48);p.drawText(tr,Qt.AlignmentFlag.AlignLeft|Qt.TextFlag.TextWordWrap,card['title'])
        p.setFont(QFont('Segoe UI',8));p.setPen(QColor('#aac0cd' if dark else '#5b707f'))
        p.setPen(accent);p.drawText(rect.adjusted(13,0,-9,-28),Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignLeft,p.fontMetrics().elidedText(card['category_label'],Qt.TextElideMode.ElideRight,rect.width()-26))
        p.setPen(QColor('#aac0cd' if dark else '#5b707f'));info=('CALCOLO  ·  ' if card.get('calculator') else '')+('LOGICA  ·  ' if card.get('logic') else 'FIGURA  ·  ' if card.get('plot') else '')+card['level']
        p.drawText(rect.adjusted(13,0,-9,-9),Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignLeft,p.fontMetrics().elidedText(info,Qt.TextElideMode.ElideRight,rect.width()-26))
        p.restore()
    def sizeHint(self,option,index):return QSize(260,112)

class Editor(QDialog):
    saved=pyqtSignal(dict)
    def __init__(self,parent,card=None,duplicate=False):
        super().__init__(parent);self.setWindowTitle('Scheda personale · editor');self.resize(1100,810)
        self.source_card=card or {};self.code_language=self.source_card.get('code_example',{}).get('language','Codice')
        self.original=card if card and not duplicate and card['id'].startswith('user-') else None
        root=QVBoxLayout(self);root.addWidget(QLabel('Crea una scheda da conservare nel tuo archivio. I campi con * sono obbligatori.'))
        split=QSplitter();left=QWidget();form=QFormLayout(left);self.fields={}
        for key,label in [('title','Titolo *'),('latex','Formula LaTeX *'),('explanation','Spiegazione *'),('symbols','Simboli e unità'),('conditions','Condizioni *'),('example','Esempio svolto *'),('code','Codice (facoltativo)'),('tags','Tag, separati da virgola')]:
            w=QLineEdit() if key in ('title','tags') else QPlainTextEdit()
            if isinstance(w,QPlainTextEdit):w.setMaximumHeight(100 if key=='explanation' else 80)
            value=(card or {}).get(key,'')
            if key=='code':value=self.source_card.get('code_example',{}).get('source','')
            if isinstance(value,list):value=', '.join(value)
            if key=='title' and duplicate:value+=' — personale'
            w.setText(value) if isinstance(w,QLineEdit) else w.setPlainText(value)
            w.setAccessibleName(label);form.addRow(label,w);self.fields[key]=w
        left_scroll=QScrollArea();left_scroll.setWidgetResizable(True);left_scroll.setWidget(left);self.preview=FormulaView();split.addWidget(left_scroll);split.addWidget(self.preview);split.setSizes([520,550]);root.addWidget(split,1)
        self.error=QLabel('');self.error.setObjectName('error');self.error.setWordWrap(True);root.addWidget(self.error)
        buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Save|QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Save).setText('Salva scheda');buttons.button(QDialogButtonBox.StandardButton.Cancel).setText('Annulla')
        buttons.accepted.connect(self.save);buttons.rejected.connect(self.reject);root.addWidget(buttons)
        self.debounce=QTimer(self);self.debounce.setSingleShot(True);self.debounce.setInterval(400);self.debounce.timeout.connect(self.refresh)
        for w in self.fields.values():w.textChanged.connect(lambda:self.debounce.start())
        self.preview.dark=parent.dark;self.refresh()
    def data(self):
        c={k:(w.text() if isinstance(w,QLineEdit) else w.toPlainText()) for k,w in self.fields.items()}
        c['tags']=[v.strip() for v in c['tags'].split(',') if v.strip()]
        source=c.pop('code')
        if source.strip():c['code_example']={'language':self.code_language,'source':source}
        c['kind']=self.source_card.get('kind','formula')
        if self.original:c['id']=self.original['id']
        return c
    def refresh(self):
        c=self.data();c.update(category_label='Schede personali',level='Personale',calculator=None,plot=None,sources=[])
        self.preview.card(c)
    def save(self):
        try:
            card=self.parent().store.save_card(self.data());self.saved.emit(card);self.accept()
        except Exception as e:self.error.setText(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__();self.store=Store();self.dark=self.store.setting('theme','light')=='dark'
        self.current=None;self.category=None;self.topic=None;self.mode='all';self.history=[];self.going_back=False;self.calc_inputs={};self.pending_kind=None
        self.setWindowTitle('Atlante Formule · Matematica, Fisica, Informatica e AI');self.setWindowIcon(icon('sigma'));self.resize(1510,950);self.setMinimumSize(1110,720)
        self.jobs=Jobs(self);self.jobs.done.connect(self.job_done);self.jobs.failed.connect(self.job_failed);self.jobs.busy.connect(self.busy)
        shell=QWidget();self.setCentralWidget(shell);root=QVBoxLayout(shell);root.setContentsMargins(0,0,0,0);root.setSpacing(0)
        header=QWidget();header.setObjectName('header');hr=QHBoxLayout(header);hr.setContentsMargins(22,16,22,16)
        mark=QLabel();mark.setPixmap(icon('sigma','#e2ffff').pixmap(31,31));mark.setObjectName('brandMark');mark.setFixedSize(47,47);mark.setAlignment(Qt.AlignmentFlag.AlignCenter);hr.addWidget(mark)
        brand=QVBoxLayout();name=QLabel('Atlante Formule');name.setObjectName('brand');brand.addWidget(name);small=QLabel('MATEMATICA · FISICA · INFORMATICA · AI');small.setObjectName('eyebrow');brand.addWidget(small);hr.addLayout(brand);hr.addSpacing(14)
        self.sections_button=button('Sezioni',self.open_home,'home');hr.addWidget(self.sections_button)
        self.search=QLineEdit();self.search.setObjectName('search');self.search.setPlaceholderText('Cerca una formula, un teorema o un argomento…   Ctrl+K');self.search.setAccessibleName('Cerca nel catalogo');self.search.addAction(icon('search'),QLineEdit.ActionPosition.LeadingPosition);self.search.setClearButtonEnabled(True);self.search.setMinimumHeight(44);hr.addWidget(self.search,1)
        self.theme=button('Tema scuro' if not self.dark else 'Tema chiaro',self.toggle_theme,'sun');hr.addWidget(self.theme)
        self.menu_button=button('Archivio',self.archive_menu,'folder');hr.addWidget(self.menu_button);root.addWidget(header)
        self.pages=QStackedWidget();root.addWidget(self.pages,1)
        browse=QWidget();browse_layout=QHBoxLayout(browse);browse_layout.setContentsMargins(0,0,0,0);browse_layout.setSpacing(0)
        self.nav=QTreeWidget();self.nav.setHeaderHidden(True);self.nav.setObjectName('navigation');self.nav.setIndentation(14);self.nav.setMinimumWidth(220);self.nav.setMaximumWidth(330)
        self.make_nav();self.nav.itemClicked.connect(self.navigate)
        self.main_split=QSplitter();self.main_split.addWidget(self.nav)
        listpane=QWidget();ll=QVBoxLayout(listpane);ll.setContentsMargins(14,20,12,14);ll.setSpacing(10)
        self.section_title=QLabel('Tutte le formule');self.section_title.setObjectName('sectionTitle');self.section_title.setWordWrap(True);ll.addWidget(self.section_title)
        self.count=QLabel('');self.count.setObjectName('muted');ll.addWidget(self.count)
        self.level=QComboBox();self.level.addItems(['Tutti i livelli','Fondamenti','Università','Avanzato','Personale']);self.level.setAccessibleName('Filtra per livello');ll.addWidget(self.level)
        self.capability=QComboBox();self.capability.addItems(['Tutti gli strumenti','Con calcolatore','Con visualizzazione','Con logica booleana']);self.capability.setAccessibleName('Filtra per strumenti');ll.addWidget(self.capability)
        self.list=QListWidget();self.list.setObjectName('cards');self.list.setItemDelegate(CardsDelegate(self.list));self.list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff);self.list.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel);self.list.currentItemChanged.connect(self.select_item);ll.addWidget(self.list,1)
        self.empty=QLabel('Nessun risultato. Prova un termine diverso o rimuovi i filtri.');self.empty.setWordWrap(True);self.empty.hide();ll.addWidget(self.empty)
        self.main_split.addWidget(listpane)
        detail=QWidget();dl=QVBoxLayout(detail);dl.setContentsMargins(0,14,18,14)
        actions=QHBoxLayout();self.back=button('',self.back_card,'arrow');self.back.setToolTip('Scheda precedente · Alt+Sinistra');self.back.setAccessibleName('Scheda precedente');actions.addWidget(self.back)
        self.path_label=QLabel('Biblioteca');self.path_label.setObjectName('muted');actions.addWidget(self.path_label,1)
        self.fav=button('Preferito',self.favorite,'star');actions.addWidget(self.fav)
        self.copy=button('LaTeX',self.copy_latex,'copy');actions.addWidget(self.copy)
        more=button('',self.card_menu,'more');more.setToolTip('Altre azioni sulla scheda');more.setAccessibleName('Altre azioni sulla scheda');actions.addWidget(more);dl.addLayout(actions)
        self.tabs=QTabWidget();self.formula=FormulaView();self.formula.font_size=int(self.store.setting('font_size','16'));self.tabs.addTab(self.formula,icon('book'),'Spiegazione')
        self.calc_page=QWidget();self.calc_layout=QVBoxLayout(self.calc_page);self.calc_layout.setContentsMargins(24,24,24,24);self.tabs.addTab(self.calc_page,icon('calculator'),'Calcolatore')
        self.plot=PlotWidget();self.tabs.addTab(self.plot,icon('plot'),'Visualizzazione')
        notes=QWidget();nl=QVBoxLayout(notes);nl.setContentsMargins(24,24,24,24);nl.addWidget(QLabel('Annotazioni personali · salvate automaticamente su questo computer'))
        self.notes=QPlainTextEdit();self.notes.setPlaceholderText('Aggiungi osservazioni, dubbi o collegamenti…');self.notes.setAccessibleName('Annotazioni personali');nl.addWidget(self.notes);self.tabs.addTab(notes,icon('notes'),'Note');dl.addWidget(self.tabs,1)
        bottom=QHBoxLayout();self.to_lab=button('Apri nel laboratorio',self.transfer_lab,'lab');bottom.addWidget(self.to_lab);bottom.addStretch();self.related=QComboBox();self.related.setMinimumWidth(200);self.related.setAccessibleName('Formule collegate');self.related.activated.connect(self.open_related);bottom.addWidget(self.related)
        smaller=button('A−',lambda:self.font_scale(-1));larger=button('A+',lambda:self.font_scale(1));smaller.setAccessibleName('Riduci dimensione del testo');larger.setAccessibleName('Aumenta dimensione del testo');bottom.addWidget(smaller);bottom.addWidget(larger);dl.addLayout(bottom)
        self.main_split.addWidget(detail);self.main_split.setSizes([225,320,945]);self.main_split.setStretchFactor(2,1);self.main_split.setChildrenCollapsible(False);browse_layout.addWidget(self.main_split);self.pages.addWidget(browse)
        self.build_lab()
        self.build_home()
        footer=QWidget();footer.setObjectName('footer');fl=QHBoxLayout(footer);fl.setContentsMargins(22,7,22,7)
        self.status=QLabel('Pronto');fl.addWidget(self.status,1);fl.addWidget(QLabel(f'{len(self.store.catalog)} schede  ·  {len(self.store.sections)} sezioni  ·  v{self.store.catalog_version}'));root.addWidget(footer)
        self.debounce=QTimer(self);self.debounce.setSingleShot(True);self.debounce.setInterval(160);self.debounce.timeout.connect(self.refresh)
        self.search.textChanged.connect(self.search_changed);self.level.currentIndexChanged.connect(self.refresh);self.capability.currentIndexChanged.connect(self.refresh)
        self.note_timer=QTimer(self);self.note_timer.setInterval(500);self.note_timer.setSingleShot(True);self.note_timer.timeout.connect(self.flush_note);self.notes.textChanged.connect(lambda:self.note_timer.start())
        for shortcut,callback in [('Ctrl+K',self.focus_search),('Ctrl+L',self.open_lab),('Alt+Left',self.back_card)]:
            a=QAction(self);a.setShortcut(QKeySequence(shortcut));a.triggered.connect(callback);self.addAction(a)
        self.apply_theme();self.refresh()
        index=next((i for i in range(self.list.count()) if self.list.item(i).data(Qt.ItemDataRole.UserRole)['id']=='classica-008'),0)
        self.list.setCurrentRow(index)
        self.open_home()
    def build_home(self):
        page=QWidget();layout=QVBoxLayout(page);layout.setContentsMargins(28,24,28,12)
        title=QLabel('Esplora le sezioni');title.setObjectName('homeTitle');layout.addWidget(title)
        subtitle=QLabel('Formule, spiegazioni ed esempi organizzati per materia. Dai fondamenti agli argomenti universitari di ingegneria informatica e intelligenza artificiale.');subtitle.setWordWrap(True);subtitle.setObjectName('muted');layout.addWidget(subtitle)
        quick=QHBoxLayout();quick.addWidget(button('Tutte le schede',lambda:self.open_section(None),'book'));quick.addWidget(button('Laboratorio',self.open_lab,'lab'));quick.addStretch()
        self.area_filter=QComboBox();self.area_filter.addItems(['Tutte le aree',*dict.fromkeys(s['family'] for s in self.store.sections)]);self.area_filter.setAccessibleName('Filtra le aree disciplinari');quick.addWidget(self.area_filter);layout.addLayout(quick)
        scroll=QScrollArea();scroll.setWidgetResizable(True);inner=QWidget();groups=QVBoxLayout(inner);groups.setSpacing(22);self.home_groups={};self.home_buttons={}
        for family_name in dict.fromkeys(s['family'] for s in self.store.sections):
            container=QWidget();box=QVBoxLayout(container);box.setContentsMargins(0,5,0,5);heading=QLabel(family_name);heading.setObjectName('sectionTitle');box.addWidget(heading);grid=QGridLayout();grid.setSpacing(14);box.addLayout(grid)
            for i,section in enumerate(s for s in self.store.sections if s['family']==family_name):
                card=QFrame();card.setObjectName('sectionCard');column=QVBoxLayout(card);column.setSpacing(7)
                choose=QToolButton();choose.setObjectName('sectionChoice');choose.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon);choose.setIconSize(QSize(34,34));choose.setText(__import__('textwrap').fill(section['title'],27));choose.setToolTip(section['title']+' — '+section['summary']);choose.setMinimumHeight(58);choose.setSizePolicy(__import__('PyQt6.QtWidgets',fromlist=['QSizePolicy']).QSizePolicy.Policy.Expanding,__import__('PyQt6.QtWidgets',fromlist=['QSizePolicy']).QSizePolicy.Policy.Preferred);choose.setCursor(Qt.CursorShape.PointingHandCursor);choose.setAccessibleName('Apri sezione '+section['title']);choose.clicked.connect(lambda checked=False,key=section['id']:self.open_section(key));column.addWidget(choose)
                summary=QLabel(section['summary']);summary.setWordWrap(True);summary.setObjectName('muted');summary.setMinimumHeight(48);column.addWidget(summary)
                count=QLabel(f'{section["count"]} schede · {len(section["topics"])} argomenti');count.setObjectName('sectionCount');column.addWidget(count);grid.addWidget(card,i//3,i%3);self.home_buttons[section['id']]=choose
            groups.addWidget(container);self.home_groups[family_name]=container
        groups.addStretch();scroll.setWidget(inner);layout.addWidget(scroll,1);self.pages.addWidget(page)
        self.area_filter.currentTextChanged.connect(lambda text:[widget.setVisible(text=='Tutte le aree' or name==text) for name,widget in self.home_groups.items()])
    def open_home(self):
        if not hasattr(self,'home_buttons'):return
        self.flush_note();self.jobs.cancel();self.plot.jobs.cancel();self.lab_plot.jobs.cancel();self.pages.setCurrentIndex(2)
        if hasattr(self,'status'):self.status.setText('Scegli una materia o cerca nel catalogo')
    def open_section(self,key):
        self.flush_note();self.jobs.cancel();self.category=key;self.topic=None;self.mode='all';self.search.blockSignals(True);self.search.clear();self.search.blockSignals(False);self.level.blockSignals(True);self.capability.blockSignals(True);self.level.setCurrentIndex(0);self.capability.setCurrentIndex(0);self.level.blockSignals(False);self.capability.blockSignals(False);self.section_title.setText(self.store.section_by_id[key]['title'] if key else 'Tutte le schede');self.pages.setCurrentIndex(0);self.refresh()
    def make_nav(self):
        def node(text,kind,value='',parent=None,ico='book'):
            n=QTreeWidgetItem(parent or self.nav,[text]);n.setData(0,Qt.ItemDataRole.UserRole,(kind,value));n.setIcon(0,icon(ico));n.setSizeHint(0,QSize(200,37));n.setToolTip(0,text);return n
        node('Sezioni','home',ico='home');node('Tutte le schede','all');node('Preferiti','favorites',ico='star');node('Recenti','recent',ico='clock');node('Schede personali','cat','personali',ico='notes');node('Laboratorio','lab',ico='lab')
        family_icons={'Matematica':'math','Fisica':'atom','Elettronica e sistemi':'circuit','Informatica':'cpu','Intelligenza artificiale':'neural'}
        families={label:node(label,'heading',label,ico=family_icons[label]) for label in dict.fromkeys(s['family'] for s in self.store.sections)}
        for section in self.store.sections:
            key=section['id'];category=node(section['title'],'cat',key,families[section['family']],section['icon']);category.setIcon(0,icon(section['icon'],section_color(key,self.dark)))
            topics=section['topics']
            for topic in topics:
                if topic:node(topic,'topic',key+'/'+topic,category)
        families['Informatica'].setExpanded(True)
    def navigate(self,item,column=0):
        kind,value=item.data(0,Qt.ItemDataRole.UserRole)
        if kind=='heading':return
        self.flush_note();self.jobs.cancel()
        if kind=='lab':self.open_lab();return
        if kind=='home':self.open_home();return
        self.pages.setCurrentIndex(0);self.category=value if kind=='cat' else value.split('/')[0] if kind=='topic' else None;self.topic=value.split('/',1)[1] if kind=='topic' else None;self.mode=kind if kind in ('favorites','recent') else 'all';self.section_title.setText(item.text(0));self.refresh()
    def search_changed(self):
        if self.pages.currentIndex()==2:
            self.category=None;self.topic=None;self.mode='all';self.section_title.setText('Risultati di ricerca');self.level.blockSignals(True);self.capability.blockSignals(True);self.level.setCurrentIndex(0);self.capability.setCurrentIndex(0);self.level.blockSignals(False);self.capability.blockSignals(False)
        self.pages.setCurrentIndex(0);self.debounce.start()
    def refresh(self,*args):
        current_id=self.current['id'] if self.current else None
        cards=self.store.search(self.search.text(),self.category,self.level.currentText(),self.capability.currentText(),self.mode,topic=self.topic)
        self.list.blockSignals(True);self.list.clear()
        selected=-1
        for i,c in enumerate(cards):
            item=QListWidgetItem(c['title']);item.setData(Qt.ItemDataRole.UserRole,c);item.setToolTip(c['title']+'\n'+c['category_label']);self.list.addItem(item)
            if c['id']==current_id:selected=i
        self.list.blockSignals(False);self.count.setText(f'{len(cards)} schede disponibili');self.empty.setVisible(not cards)
        if cards:self.list.setCurrentRow(selected if selected>=0 else 0)
        else:
            self.flush_note();self.jobs.cancel();self.current=None;self.formula.show_body('<h1>Nessuna scheda in questa vista</h1><p>Modifica la ricerca, cambia i filtri oppure crea una scheda personale dal menu Archivio.</p>');self.tabs.setTabEnabled(1,False);self.tabs.setTabEnabled(2,False);self.notes.blockSignals(True);self.notes.clear();self.notes.blockSignals(False);self.related.clear()
    def select_item(self,item,old=None):
        if item:self.show_card(item.data(Qt.ItemDataRole.UserRole))
    def show_card(self,card):
        if self.current:self.flush_note()
        if self.current and self.current['id']!=card['id']:
            if not self.going_back:self.history.append(self.current['id'])
        self.jobs.cancel();self.plot.jobs.cancel();self.current=card;self.store.visit(card['id']);self.formula.card(card);self.path_label.setText(card['category_label']);self.fav.setText('Nei preferiti' if card['id'] in self.store.favorites else 'Preferito')
        selected=next((i for i in range(self.list.count()) if self.list.item(i).data(Qt.ItemDataRole.UserRole)['id']==card['id']),-1)
        self.list.blockSignals(True);self.list.setCurrentRow(selected)
        if selected>=0:self.list.scrollToItem(self.list.item(selected),QAbstractItemView.ScrollHint.EnsureVisible)
        self.list.blockSignals(False)
        self.path_label.setStyleSheet(f'color:{section_color(card["category"],self.dark)};font-weight:600;')
        self.copy.setText('Codice' if card.get('code_example') else 'LaTeX');self.copy.setToolTip('Copia esempio di codice' if card.get('code_example') else 'Copia formula LaTeX')
        self.to_lab.setText('Apri tabella di verità' if card.get('logic') else 'Apri nel laboratorio')
        self.notes.blockSignals(True);self.notes.setPlainText(self.store.note(card['id']));self.notes.blockSignals(False)
        self.note_timer.stop() if hasattr(self,'note_timer') else None
        self.related.clear();self.related.addItem('Formule collegate…','')
        for cid in card.get('related',[]):
            if cid in self.store.by_id:self.related.addItem(self.store.by_id[cid]['title'],cid)
        self.tabs.setCurrentIndex(0);self.build_calculator(card);self.tabs.setTabEnabled(2,bool(card.get('plot')))
        if card.get('plot'):self.plot.set_card(card)
        self.status.setText(card['title']);self.back.setEnabled(bool(self.history))
    def build_calculator(self,card):
        while self.calc_layout.count():
            item=self.calc_layout.takeAt(0)
            if item.widget():item.widget().deleteLater()
        self.calc_inputs={};calc=card.get('calculator');self.tabs.setTabEnabled(1,bool(calc))
        self.compute=None
        if not calc:return
        title=QLabel('Prova con i tuoi valori');title.setObjectName('sectionTitle');self.calc_layout.addWidget(title)
        helptext=QLabel('Usa le unità indicate, oppure scrivi una quantità compatibile, ad esempio «20 cm». Gli angoli sono in radianti; puoi inserire pi/3.');helptext.setWordWrap(True);helptext.setObjectName('muted');self.calc_layout.addWidget(helptext)
        scroll=QScrollArea();scroll.setWidgetResizable(True);inner=QWidget();form=QFormLayout(inner);form.setVerticalSpacing(14)
        for field in calc['inputs']:
            w=QLineEdit(field['default']);w.setAccessibleName(field['label']);w.setPlaceholderText(field['default']);w.setMinimumHeight(38);w.textEdited.connect(self.invalidate_calculation)
            label=QLabel(field['name']+' · '+field['label']+(' ['+field['unit']+']' if field['unit'] else ''));label.setWordWrap(True);form.addRow(label,w);self.calc_inputs[field['name']]=w
        self.precision=QSpinBox();self.precision.setRange(3,15);self.precision.setValue(8);form.addRow('Cifre significative',self.precision);scroll.setWidget(inner);self.calc_layout.addWidget(scroll,1)
        row=QHBoxLayout();self.compute=button('Calcola risultato',self.compute_card);self.compute.setObjectName('primary');row.addWidget(self.compute);self.calc_cancel=button('Annulla',self.cancel_job);row.addWidget(self.calc_cancel);reset=button('Valori iniziali',self.reset_calc);row.addWidget(reset);self.calc_layout.addLayout(row)
        self.calc_result=QLabel('Inserisci i valori e premi Calcola.');self.calc_result.setObjectName('result');self.calc_result.setWordWrap(True);self.calc_result.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse);self.calc_layout.addWidget(self.calc_result)
        self.calc_error=QLabel('');self.calc_error.setObjectName('error');self.calc_error.setWordWrap(True);self.calc_layout.addWidget(self.calc_error)
    def invalidate_calculation(self):
        self.jobs.cancel()
        if hasattr(self,'calc_result'):self.calc_result.setText('Dati modificati: ricalcola il risultato.')
    def reset_calc(self):
        self.jobs.cancel()
        for f in self.current['calculator']['inputs']:self.calc_inputs[f['name']].setText(f['default'])
        self.calc_result.setText('Valori iniziali ripristinati.');self.calc_error.clear()
        if self.current.get('plot'):self.plot.set_card(self.current)
    def compute_card(self):
        if not self.current or not self.current['calculator']:return
        self.flush_note();self.pending_kind='calculator';self.calc_error.clear();self.calc_result.setText('Calcolo in corso…')
        self.jobs.start({'kind':'calculator','card':self.current,'inputs':{k:w.text() for k,w in self.calc_inputs.items()},'precision':self.precision.value()})
    def busy(self,busy):
        if hasattr(self,'status'):self.status.setText('Calcolo in corso · annullabile · massimo 15 s' if busy else 'Pronto')
        if getattr(self,'compute',None):self.compute.setEnabled(not busy)
        if hasattr(self,'lab_compute'):self.lab_compute.setEnabled(not busy)
    def job_done(self,result):
        if self.pending_kind=='calculator':
            self.calc_result.setText(result['text']);self.calc_error.setText(' · '.join(result.get('conversions',[])))
            if self.current and self.current.get('plot'):
                try:self.plot.set_card(self.current,result.get('normalized',{}))
                except Exception as exc:self.calc_error.setText('Risultato calcolato; grafico: '+str(exc))
        elif self.pending_kind=='surface':self.lab_plot.surface(result,self.expression.toPlainText());self.lab_feedback.clear();self.lab_tabs.setCurrentIndex(1)
        else:self.lab_result.result(result);self.lab_feedback.clear()
        self.status.setText('Calcolo completato')
    def job_failed(self,message):
        if self.pending_kind=='calculator' and hasattr(self,'calc_error'):self.calc_error.setText(message);self.calc_result.setText('Nessun risultato valido.')
        else:self.lab_feedback.setText(message)
        self.status.setText('Controlla i dati del problema')
    def cancel_job(self):
        self.jobs.cancel();self.status.setText('Calcolo annullato')
        if self.pending_kind=='calculator' and hasattr(self,'calc_result'):self.calc_result.setText('Calcolo annullato.')
        else:self.lab_feedback.setText('Calcolo annullato.')
    def build_lab(self):
        page=QWidget();root=QVBoxLayout(page);root.setContentsMargins(24,20,24,18)
        top=QHBoxLayout();top.addWidget(button('Torna al catalogo',lambda:self.pages.setCurrentIndex(0),'arrow'));labtitle=QLabel('Laboratorio matematico');labtitle.setObjectName('sectionTitle');top.addWidget(labtitle);top.addStretch();root.addLayout(top)
        split=QSplitter();inputpane=QWidget();form=QVBoxLayout(inputpane);form.setContentsMargins(0,12,20,0)
        form.addWidget(QLabel('Operazione'))
        self.operation=QComboBox();self.operation.addItems(['semplifica','sviluppa','fattorizza','equazione','sistema','derivata','integrale','integrale definito','limite','taylor','determinante','rango','inversa','riduzione','autovalori','trasposta','retta per due punti','distanza punto-retta','circonferenza','intersezione retta-conica','grafico 2D','superficie 3D','tabella di verità','semplifica Boole','equivalenza booleana','forma CNF','mappa di Karnaugh']);form.addWidget(self.operation)
        form.addWidget(QLabel('Espressione o dati'))
        self.expression=QPlainTextEdit('x^3 - 3*x');self.expression.setMaximumHeight(170);self.expression.setAccessibleName('Espressione del laboratorio');form.addWidget(self.expression)
        self.lab_help=QLabel('');self.lab_help.setWordWrap(True);self.lab_help.setObjectName('muted');form.addWidget(self.lab_help)
        self.variables=QLineEdit('x');self.variables.setAccessibleName('Variabile di calcolo');self.variables.setMaximumWidth(100)
        sub=QFormLayout();sub.addRow('Variabile',self.variables)
        self.lab_a=QLineEdit('0');self.lab_b=QLineEdit('1');sub.addRow('Punto / estremo a',self.lab_a);sub.addRow('Estremo b',self.lab_b)
        self.direction=QComboBox();self.direction.addItem('Bilatero','+-');self.direction.addItem('Da destra','+');self.direction.addItem('Da sinistra','-');sub.addRow('Direzione del limite',self.direction)
        self.order=QSpinBox();self.order.setRange(1,20);self.order.setValue(6);sub.addRow('Ordine Taylor (resto incluso)',self.order);form.addLayout(sub);self.lab_parameters=sub
        self.syntax_label=QLabel('Sintassi: x^2, 2*x, sin(x), sqrt(x), log(x), exp(x), pi, E, oo. Usa * per moltiplicare.');self.syntax_label.setWordWrap(True);form.addWidget(self.syntax_label)
        row=QHBoxLayout();self.lab_compute=button('Esegui',self.compute_lab);self.lab_compute.setObjectName('primary');row.addWidget(self.lab_compute);row.addWidget(button('Annulla',self.cancel_job));form.addLayout(row)
        self.lab_feedback=QLabel('');self.lab_feedback.setWordWrap(True);self.lab_feedback.setObjectName('error');form.addWidget(self.lab_feedback);form.addStretch();input_scroll=QScrollArea();input_scroll.setWidgetResizable(True);input_scroll.setWidget(inputpane);input_scroll.setMinimumWidth(310);split.addWidget(input_scroll)
        self.lab_tabs=QTabWidget();self.lab_result=FormulaView();self.lab_tabs.addTab(self.lab_result,'Risultato e passaggi');self.lab_plot=PlotWidget();self.lab_tabs.addTab(self.lab_plot,'Grafico');split.addWidget(self.lab_tabs);split.setSizes([390,1050]);root.addWidget(split,1);self.pages.addWidget(page)
        self.operation.currentTextChanged.connect(self.operation_changed);self.expression.textChanged.connect(self.invalidate_lab)
        for w in (self.lab_a,self.lab_b,self.variables):w.textChanged.connect(self.invalidate_lab)
        self.direction.currentIndexChanged.connect(self.invalidate_lab);self.order.valueChanged.connect(self.invalidate_lab)
        self.operation_changed();self.lab_result.show_body('<div class="eyebrow">Spazio di lavoro</div><h1>Esplora una relazione</h1><p>Inserisci un’espressione, scegli uno strumento e avvia il calcolo. I passaggi guidati compaiono per le operazioni supportate; le altre restituiscono il risultato simbolico con le relative condizioni.</p>')
    def invalidate_lab(self,*args):
        self.jobs.cancel()
        self.lab_plot.jobs.cancel()
        if hasattr(self,'lab_feedback'):self.lab_feedback.setText('Dati modificati: esegui nuovamente il calcolo.')
    def operation_changed(self,*args):
        op=self.operation.currentText();examples={
        'equazione':('x^2-5*x+6=0','Usa = per l’uguaglianza. Le soluzioni sono cercate nei reali.'),
        'sistema':('x+y=3; x-y=1','Equazioni lineari separate da ;. Il risultato indica l’ordine delle incognite.'),
        'determinante':('1,2;3,4','Matrice: colonne separate da virgole, righe da ;. Massimo 10×10.'),
        'rango':('1,2;2,4','Matrice rettangolare ammessa.'),'inversa':('1,2;3,4','Serve una matrice quadrata non singolare.'),
        'riduzione':('1,1,3;2,1,4','Puoi inserire una matrice aumentata per seguire le operazioni di Gauss-Jordan.'),
        'autovalori':('2,1;1,2','Matrice quadrata; vengono indicate le molteplicità.'),'trasposta':('1,2,3;4,5,6','Matrice rettangolare ammessa.'),
        'retta per due punti':('0;0;2;3','Formato: x1; y1; x2; y2. Gestisce anche rette verticali.'),
        'distanza punto-retta':('0;0;3;4;-10','Formato: x0; y0; a; b; c per la retta ax+by+c=0.'),
        'circonferenza':('1;-2;3','Formato: xc; yc; r. Il raggio deve essere positivo.'),
        'intersezione retta-conica':('y-x; x^2+y^2-2','Due espressioni uguali a zero separate da ;. Prima la retta, poi la conica.'),
        'grafico 2D':('sin(x)/x','Gli estremi a e b definiscono l’intervallo. Le discontinuità interrompono la curva.'),
        'superficie 3D':('x^2+y^2','Usa x e y. Gli estremi a e b delimitano entrambe le coordinate.'),
        'derivata':('x^3*sin(x)','Passaggi per linearità, prodotto, potenze e catena; risultato simbolico negli altri casi.'),
        'limite':('sin(x)/x','Punto a e direzione del limite. Per infinito usa oo o -oo.'),
        'integrale definito':('x^2','Usa a e b come estremi; il motore può segnalare integrali non risolti.'),
        'taylor':('exp(x)','Sviluppo nel punto a fino al termine precedente all’ordine del resto.'),
        'integrale':('2*x*cos(x^2)','Aggiungere sempre la costante C alle primitive su un intervallo.'),
        'semplifica':('(x^2-1)/(x-1)','La semplificazione non estende automaticamente il dominio originario.'),
        'tabella di verità':('A ^ B','Bit 0/1, variabili a una lettera: & AND, | OR, ~ NOT, ^ XOR. Massimo 6 variabili.'),
        'semplifica Boole':('(A & B) | (A & ~B)','Semplificazione logica in forma DNF; + e * sono anche ammessi come OR e AND.'),
        'equivalenza booleana':('~(A & B); ~A | ~B','Separa le due espressioni con ;. La verifica enumera tutte le assegnazioni e mostra un controesempio se non sono equivalenti.'),
        'forma CNF':('A ^ B','Forma congiuntiva: AND di clausole OR. La tabella permette di confrontare con l’originale.'),
        'mappa di Karnaugh':('(A & B) | (~A & C)','Da 1 a 4 variabili; righe e colonne in ordine Gray, bordi opposti adiacenti. Nessun don’t care implicito.'),
        'sviluppa':('(x+1)^4','Espandi prodotti e potenze.'),'fattorizza':('x^2-5*x+6','Scomponi il polinomio in fattori.')}
        default,helptext=examples[op];self.lab_help.setText('Esempio: '+default+'\n'+helptext)
        logic=op in ('tabella di verità','semplifica Boole','equivalenza booleana','forma CNF','mappa di Karnaugh')
        for control in (self.variables,self.lab_a,self.lab_b,self.direction,self.order):self.lab_parameters.setRowVisible(control,not logic)
        self.variables.setEnabled(not logic)
        self.syntax_label.setText('Logica: ~ NOT · & AND · | OR · ^ XOR. Bit 0/1 e variabili a una lettera; usa parentesi. Due espressioni si separano con ;.' if logic else 'Aritmetica: x^2, 2*x, sin(x), sqrt(x), log(x), exp(x), pi, E, oo. Usa * per moltiplicare; ^ indica potenza.')
        self.expression.setPlaceholderText(default)
        # Il cambio di operazione non cancella l'espressione dell'utente.
        self.lab_a.setEnabled(op in ('limite','integrale definito','taylor','grafico 2D','superficie 3D'));self.lab_b.setEnabled(op in ('integrale definito','grafico 2D','superficie 3D'));self.direction.setEnabled(op=='limite');self.order.setEnabled(op=='taylor');self.invalidate_lab()
    def compute_lab(self):
        op=self.operation.currentText();self.lab_feedback.clear()
        if op in ('grafico 2D','superficie 3D'):
            try:
                from atlante.engine import numeric,parse
                a,b=numeric(self.lab_a.text()),numeric(self.lab_b.text())
                if b<=a:raise ValueError('b deve essere maggiore di a.')
                if op=='grafico 2D':self.lab_plot.set_function(self.expression.toPlainText(),self.variables.text(),a,b)
                else:
                    self.pending_kind='surface';self.jobs.start({'kind':'plot3d','expression':self.expression.toPlainText(),'start':a,'end':b})
                self.lab_tabs.setCurrentIndex(1)
            except Exception as exc:self.lab_feedback.setText(str(exc))
            return
        self.pending_kind='lab';self.lab_tabs.setCurrentIndex(0)
        self.jobs.start({'kind':'lab','operation':op,'expression':self.expression.toPlainText(),'variable':self.variables.text(),'a':self.lab_a.text(),'b':self.lab_b.text(),'direction':self.direction.currentData(),'order':self.order.value()})
    def open_lab(self):self.flush_note();self.pages.setCurrentIndex(1)
    def transfer_lab(self):
        if not self.current:return
        if self.current.get('logic'):
            logic=self.current['logic'];self.operation.setCurrentText('equivalenza booleana' if logic.get('equivalent_to') else 'tabella di verità');self.expression.setPlainText(logic['expression']+('; '+logic['equivalent_to'] if logic.get('equivalent_to') else ''))
        elif self.current.get('calculator'):self.expression.setPlainText(self.current['calculator']['expression']);self.operation.setCurrentText('semplifica')
        elif self.current['category']=='analitica':
            t=self.current['title'].lower()
            op='circonferenza' if 'circonferenza'in t else 'intersezione retta-conica' if 'intersezione'in t else 'distanza punto-retta' if 'distanza punto-retta'in t else 'retta per due punti'
            self.operation.setCurrentText(op);self.expression.setPlainText({'circonferenza':'0;0;3','intersezione retta-conica':'y-x;x^2+y^2-2','distanza punto-retta':'0;0;3;4;-10','retta per due punti':'0;0;2;3'}[op])
        elif self.current['category']=='lineare':self.operation.setCurrentText('riduzione');self.expression.setPlainText('1,1,3;2,1,4')
        else:self.operation.setCurrentText('derivata');self.expression.setPlainText('x^2')
        self.open_lab()
    def focus_search(self):self.pages.setCurrentIndex(0);self.search.setFocus();self.search.selectAll()
    def open_related(self,index):
        cid=self.related.itemData(index)
        if cid in self.store.by_id:self.show_card(self.store.by_id[cid])
    def back_card(self):
        if not self.history:return
        cid=self.history.pop();self.going_back=True
        if cid in self.store.by_id:self.show_card(self.store.by_id[cid])
        self.going_back=False
    def favorite(self):
        if self.current:
            self.store.favorite(self.current['id']);self.fav.setText('Nei preferiti' if self.current['id'] in self.store.favorites else 'Preferito')
            if self.mode=='favorites':self.refresh()
    def copy_latex(self):
        if self.current:
            code=self.current.get('code_example');QApplication.clipboard().setText(code['source'] if code else self.current['latex']);self.status.setText('Codice copiato' if code else 'Formula LaTeX copiata')
    def flush_note(self):
        if self.current and hasattr(self,'notes'):self.store.save_note(self.current['id'],self.notes.toPlainText())
        if hasattr(self,'note_timer'):self.note_timer.stop()
    def font_scale(self,delta):
        self.formula.font_size=max(13,min(26,self.formula.font_size+delta));self.store.set_setting('font_size',self.formula.font_size)
        if self.current:self.formula.card(self.current)
    def toggle_theme(self):
        self.dark=not self.dark;self.store.set_setting('theme','dark' if self.dark else 'light');self.apply_theme()
        if self.current:self.formula.card(self.current)
        self.lab_result.show_body(self.lab_result.last_body)
    def apply_theme(self):
        bg='#0d1723' if self.dark else '#f4f7fa';surface='#111d2b' if self.dark else '#ffffff';fg='#e5eef5' if self.dark else '#203747';muted='#a9becc' if self.dark else '#536b7b';border='#2c4051' if self.dark else '#dce5ea';hover='#203745' if self.dark else '#e9f3f4';accent='#168b92'
        palette=QPalette()
        for role,color in ((QPalette.ColorRole.Window,bg),(QPalette.ColorRole.Base,surface),(QPalette.ColorRole.WindowText,fg),(QPalette.ColorRole.Text,fg),(QPalette.ColorRole.Button,surface),(QPalette.ColorRole.ButtonText,fg),(QPalette.ColorRole.Highlight,accent),(QPalette.ColorRole.HighlightedText,'#ffffff')):palette.setColor(role,QColor(color))
        QApplication.instance().setPalette(palette)
        self.setStyleSheet(f'''
        QWidget{{font-family:'Segoe UI';font-size:13px;color:{fg};}}QMainWindow,QWidget#qt_scrollarea_viewport{{background:{bg};}}
        QWidget#header,QWidget#footer{{background:{surface};border-bottom:1px solid {border};}}QWidget#footer{{border-top:1px solid {border};}}
        QLabel#brand{{font-size:21px;font-weight:650;}}QLabel#brandMark{{background:#167780;border-radius:11px;}}QLabel#eyebrow{{font-size:10px;font-weight:650;letter-spacing:2px;color:{muted};}}
        QLabel#sectionTitle{{font-size:21px;font-weight:650;}}QLabel#muted{{color:{muted};}}QLabel#error{{color:{'#ffb5a9' if self.dark else '#a63325'};padding:6px;}}
        QLabel#homeTitle{{font-size:29px;font-weight:650;padding:0 0 6px 0;}}
        QFrame#sectionCard{{background:{surface};border:1px solid {border};border-radius:10px;padding:9px;}}
        QToolButton#sectionChoice{{font-size:15px;font-weight:650;text-align:left;padding:4px;}}
        QToolButton#sectionChoice:hover{{background:{hover};border-radius:7px;}}
        QLabel#sectionCount{{color:{muted};font-size:12px;padding-top:6px;}}
        QLineEdit,QPlainTextEdit,QComboBox,QSpinBox,QDoubleSpinBox{{background:{surface};border:1px solid {border};border-radius:7px;padding:8px;selection-background-color:#168b92;selection-color:white;}}
        QLineEdit:focus,QPlainTextEdit:focus,QComboBox:focus,QPushButton:focus{{border:2px solid #168b92;}}
        QLineEdit#search{{font-size:14px;background:{bg};}}QComboBox::drop-down{{border:0;width:20px;}}
        QComboBox QAbstractItemView{{background:{surface};selection-background-color:{hover};color:{fg};}}
        QPushButton{{background:{surface};border:1px solid {border};border-radius:7px;padding:9px 13px;font-weight:550;}}QPushButton:hover{{background:{hover};border-color:#5b9296;}}QPushButton:pressed{{background:#307980;color:white;}}QPushButton:disabled{{color:{muted};background:{bg};}}
        QPushButton#primary{{background:#147d84;color:white;border:1px solid #147d84;}}QPushButton#primary:hover{{background:#106970;}}
        QTreeWidget#navigation{{background:{surface};border:0;border-right:1px solid {border};padding:14px 7px;outline:0;}}QTreeWidget::item{{padding:6px 3px;}}QTreeWidget::item:selected{{background:{hover};color:{fg};border-radius:5px;}}QTreeWidget::item:hover{{background:{hover};}}
        QListWidget#cards{{background:transparent;border:0;outline:0;}}QSplitter::handle{{background:{border};width:2px;}}
        QTabWidget::pane{{background:{surface};border:1px solid {border};border-radius:8px;}}QTabBar::tab{{background:{bg};color:{muted};padding:11px 18px;border-bottom:2px solid transparent;}}QTabBar::tab:selected{{color:{accent};font-weight:650;border-bottom:2px solid {accent};background:{surface};}}QTabBar::tab:disabled{{color:#82919c;}}
        QScrollArea{{border:0;background:{surface};}}QMenu{{background:{surface};border:1px solid {border};padding:6px;}}QMenu::item{{padding:9px 20px;}}QMenu::item:selected{{background:{hover};}}
        QLabel#result{{background:{hover};border:1px solid {border};border-radius:8px;padding:20px;font-size:22px;font-weight:600;}}
        QToolBar{{background:{surface};border:0;}}QToolButton{{background:{surface};border:0;padding:5px;}}QToolButton:hover{{background:{hover};}}QDialog{{background:{bg};}}
        QScrollBar:vertical{{background:{bg};width:10px;margin:0;}}QScrollBar::handle:vertical{{background:#839aa977;min-height:26px;border-radius:5px;}}QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{{height:0;}}QScrollBar::add-page:vertical,QScrollBar::sub-page:vertical{{background:transparent;}}
        ''')
        self.theme.setText('Tema chiaro' if self.dark else 'Tema scuro');self.list.setProperty('dark',self.dark);self.list.viewport().update()
        self.theme.setIcon(icon('sun' if self.dark else 'moon', '#b8dce5' if self.dark else '#237b85'))
        for key,choose in self.home_buttons.items():
            choose.setIcon(icon(self.store.section_by_id[key]['icon'],section_color(key,self.dark)))
            choose.setStyleSheet('color:'+section_color(key,self.dark)+';')
        for i,name in enumerate(('book','calculator','plot','notes')):
            self.tabs.setTabIcon(i,icon(name,'#c1d8e4' if self.dark else '#376a7b'))

        def tint(item):
            kind,value=item.data(0,Qt.ItemDataRole.UserRole)
            if kind in ('cat','topic'):
                key=value.split('/')[0];entry=self.store.section_by_id.get(key);item.setIcon(0,icon(entry['icon'] if entry else 'notes',section_color(key,self.dark)));item.setForeground(0,QColor(section_color(key,self.dark)))
            for i in range(item.childCount()):tint(item.child(i))
        for i in range(self.nav.topLevelItemCount()):tint(self.nav.topLevelItem(i))
        if self.current:self.path_label.setStyleSheet(f'color:{section_color(self.current["category"],self.dark)};font-weight:600;')
        for view in (self.formula,self.lab_result):view.dark=self.dark
        for plot in (self.plot,self.lab_plot):plot.dark=self.dark;plot.style_axes();plot.canvas.draw_idle()
    def card_menu(self):
        if not self.current:return
        menu=QMenu(self);menu.addAction(icon('copy'),'Crea copia personale',lambda:self.edit_card(True));menu.addAction(icon('web'),'Fonti online',self.sources)
        if self.current['id'].startswith('user-'):
            menu.addAction(icon('edit'),'Modifica scheda',lambda:self.edit_card(False));menu.addAction(icon('trash'),'Elimina scheda personale',self.delete_personal)
        menu.exec(self.cursor().pos())
    def sources(self):
        if not self.current:return
        menu=QMenu(self)
        for source in self.current['sources']:menu.addAction(source['title'],lambda checked=False,url=source['url']:QDesktopServices.openUrl(QUrl(url)))
        if not self.current['sources']:menu.addAction('Nessuna fonte associata').setEnabled(False)
        menu.exec(self.cursor().pos())
    def edit_card(self,duplicate=False,new=False):
        dialog=Editor(self,None if new else self.current,duplicate);dialog.saved.connect(self.personal_saved);dialog.exec()
    def personal_saved(self,card):
        self.category='personali';self.topic=None;self.mode='all';self.search.clear();self.level.setCurrentIndex(0);self.capability.setCurrentIndex(0);self.section_title.setText('Schede personali');self.refresh();self.show_card(card)
    def delete_personal(self):
        if not self.current or not self.current['id'].startswith('user-'):return
        if QMessageBox.question(self,'Elimina scheda','Eliminare questa scheda personale e le sue annotazioni?',QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No)==QMessageBox.StandardButton.Yes:
            self.store.delete_card(self.current['id']);self.current=None;self.refresh()
    def archive_menu(self):
        menu=QMenu(self);menu.addAction(icon('plus'),'Nuova scheda personale',lambda:self.edit_card(new=True));menu.addSeparator();menu.addAction(icon('export'),'Esporta archivio e annotazioni…',self.export_data);menu.addAction(icon('import'),'Importa archivio…',self.import_data);menu.addSeparator();menu.addAction(icon('legend'),'Legenda delle sezioni',self.color_legend);menu.addAction(icon('book'),'Materie e contenuti',lambda:self.open_document('MATERIE.md'));menu.addAction(icon('check'),'Controllo delle formule',lambda:self.open_document('AUDIT_FORMULE.md'));menu.addAction(icon('folder'),'Apri cartella dati',lambda:QDesktopServices.openUrl(QUrl.fromLocalFile(str(user_dir()))));menu.addAction(icon('help'),'Guida e informazioni',self.about);menu.exec(self.menu_button.mapToGlobal(self.menu_button.rect().bottomLeft()))
    def open_document(self,name):
        base=Path(sys.executable).parent if getattr(sys,'frozen',False) else ROOT
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(base/name)))
    def color_legend(self):
        dialog=QDialog(self);dialog.setWindowTitle('Codice colore · sezioni');dialog.resize(570,680);layout=QVBoxLayout(dialog)
        info=QLabel('Ogni sezione è identificata da nome e colore. I colori si adattano al tema; il nome resta sempre visibile.');info.setWordWrap(True);layout.addWidget(info)
        scroll=QScrollArea();scroll.setWidgetResizable(True);inner=QWidget();rows=QVBoxLayout(inner)
        categories={c['category']:c['category_label'] for c in self.store.catalog}
        for key,title in categories.items():
            color=section_color(key,self.dark);row=QHBoxLayout();symbol=QLabel();symbol.setPixmap(icon(self.store.section_by_id[key]['icon'],color).pixmap(28,28));row.addWidget(symbol)
            label=QLabel(title+'\n'+family(key));label.setStyleSheet('color:'+color+';padding:7px;');row.addWidget(label,1);rows.addLayout(row)
        scroll.setWidget(inner);layout.addWidget(scroll);close=button('Chiudi',dialog.accept);layout.addWidget(close);dialog.exec()
    def export_data(self):
        self.flush_note();path,_=QFileDialog.getSaveFileName(self,'Esporta archivio','atlante-backup.json','Archivio JSON (*.json)')
        if path:
            try:Path(path).write_text(json.dumps(self.store.export(),ensure_ascii=False,indent=2),encoding='utf-8');self.status.setText('Archivio esportato: '+path)
            except Exception as e:QMessageBox.warning(self,'Esportazione',str(e))
    def import_data(self):
        path,_=QFileDialog.getOpenFileName(self,'Importa archivio','','Archivio JSON (*.json)')
        if path:
            try:
                if Path(path).stat().st_size>20_000_000:raise ValueError('Archivio troppo grande: massimo 20 MB.')
                self.flush_note();before=self.store.export();backup=user_dir()/'prima-importazione.json';backup.write_text(json.dumps(before,ensure_ascii=False,indent=2),encoding='utf-8')
                n=self.store.import_data(json.loads(Path(path).read_text(encoding='utf-8')));self.refresh();self.status.setText(f'Importate {n} schede. Backup precedente in {backup.name}.')
            except Exception as e:QMessageBox.warning(self,'Importazione',str(e))
    def about(self):
        QMessageBox.information(self,'Atlante Formule',f'Atlante Formule {self.store.catalog_version}\n{len(self.store.catalog)} schede di matematica, fisica, informatica e AI.\n\nSezioni disciplinari, concetti universitari e laboratorio booleano.\nCtrl+K: ricerca · Ctrl+L: laboratorio · Alt+Sinistra: indietro.\n\nPotenza: ^ nel laboratorio aritmetico; XOR: ^ nel laboratorio booleano.\nGli angoli dei calcoli sono in radianti.\n\nGUIDA.md, AUDIT_FORMULE.md e MATERIE.md nella cartella del programma.\nPyQt6, SymPy, NumPy, Matplotlib, MathJax e Pint.\nLicenze delle dipendenze incluse nel pacchetto.')
    def closeEvent(self,event):
        self.flush_note();self.jobs.cancel();self.plot.jobs.cancel();self.lab_plot.jobs.cancel();self.store.close();super().closeEvent(event)

def run():
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
    app=QApplication(sys.argv);app.setApplicationName('AtlanteFormule');app.setOrganizationName('AtlanteFormule');app.setStyle('Fusion');app.setFont(QFont('Segoe UI',10))
    window=MainWindow()
    screen=app.primaryScreen()
    if screen:
        available=screen.availableGeometry();window.setMinimumSize(min(1110,available.width()-32),min(720,available.height()-48));window.resize(min(1510,available.width()-32),min(950,available.height()-48))
    window.show()
    if '--qa-report' in sys.argv:
        from tools.package_smoke import begin
        begin(window,app,sys.argv[sys.argv.index('--qa-report')+1])
    if '--smoke' in sys.argv:
        def smoke():
            path=ROOT/'verifiche';path.mkdir(exist_ok=True);window.grab().save(str(path/'interfaccia.png'));window.close()
        QTimer.singleShot(8000,smoke)
    sys.exit(app.exec())

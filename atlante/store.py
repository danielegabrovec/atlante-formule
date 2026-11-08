"""Catalogo distribuito e dati personali separati, con ricerca locale."""
import json
import sqlite3
import unicodedata
import uuid
from datetime import datetime,timezone
from rapidfuzz.fuzz import WRatio
from atlante.paths import ROOT,user_dir

def normalize(text):
    return ''.join(c for c in unicodedata.normalize('NFKD',text.casefold()) if not unicodedata.combining(c))

def validate_personal(c):
    if not isinstance(c,dict):raise ValueError('Scheda non valida.')
    for key in ('title','latex','explanation','conditions','example'):
        if not isinstance(c.get(key),str) or not c[key].strip():raise ValueError(f'Campo obbligatorio: {key}.')
        if len(c[key])>20000:raise ValueError(f'Campo troppo lungo: {key}.')
    # Le schede importate sono contenuto editoriale, senza codice o calcolatori eseguibili.
    card={'id':c.get('id') if str(c.get('id','')).startswith('user-') else 'user-'+uuid.uuid4().hex,
            'title':c['title'].strip(),'latex':c['latex'],'explanation':c['explanation'],
            'conditions':c['conditions'],'example':c['example'],'symbols':str(c.get('symbols','')),
            'category':'personali','category_label':'Schede personali','level':str(c.get('level','Personale')),
            'tags':[str(x)[:100] for x in c.get('tags',[])[:30]],'sources':[], 'related':[], 'calculator':None,'plot':None}
    if c.get('kind') in ('formula','concetto'):card['kind']=c['kind']
    if c.get('code_example'):
        code=c['code_example']
        if not isinstance(code,dict) or not isinstance(code.get('source'),str) or len(code['source'])>20000:raise ValueError('Esempio di codice non valido.')
        card['code_example']={'language':str(code.get('language','Codice'))[:40],'source':code['source']}
    return card

class Store:
    def __init__(self,path=None):
        raw=json.loads((ROOT/'atlante/data/catalog.json').read_text(encoding='utf-8'))
        self.catalog=raw['cards']
        self.sections=raw['sections'];self.section_by_id={section['id']:section for section in self.sections};self.catalog_version=raw.get('catalog_version','1.2.0')
        self.db=sqlite3.connect(str(path or user_dir()/'atlante.sqlite3'))
        self.db.executescript('''
        PRAGMA journal_mode=WAL;
        CREATE TABLE IF NOT EXISTS personal(id TEXT PRIMARY KEY,data TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS notes(id TEXT PRIMARY KEY,body TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS favorites(id TEXT PRIMARY KEY);
        CREATE TABLE IF NOT EXISTS recent(id TEXT PRIMARY KEY,visited TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT NOT NULL);
        PRAGMA user_version=1;
        ''')
        self.reload()
    def reload(self):
        self.cards=self.catalog+[json.loads(row[0]) for row in self.db.execute('SELECT data FROM personal')]
        self.by_id={c['id']:c for c in self.cards}
        self.index={c['id']:normalize(' '.join([c['title'],c['category_label'],c.get('topic',''),c['explanation'],c['symbols'],*c['tags']])) for c in self.cards}
        self.favorites={r[0] for r in self.db.execute('SELECT id FROM favorites')}
        self.recents=[r[0] for r in self.db.execute('SELECT id FROM recent ORDER BY visited DESC LIMIT 40')]
    def search(self,query='',category=None,level=None,capability=None,mode='all',topic=None):
        candidates=self.cards
        if category:candidates=[c for c in candidates if c['category']==category]
        if topic:candidates=[c for c in candidates if c.get('topic')==topic]
        if level and level!='Tutti i livelli':
            if level=='Fondamenti':candidates=[c for c in candidates if 'Liceo' in c['level']]
            elif level=='Università':candidates=[c for c in candidates if c['level']!='Liceo' and c['level']!='Personale']
            else:candidates=[c for c in candidates if level in c['level']]
        if capability=='Con calcolatore':candidates=[c for c in candidates if c['calculator']]
        if capability=='Con visualizzazione':candidates=[c for c in candidates if c['plot']]
        if capability=='Con logica booleana':candidates=[c for c in candidates if c.get('logic')]
        if mode=='favorites':candidates=[c for c in candidates if c['id'] in self.favorites]
        if mode=='recent':candidates=sorted([c for c in candidates if c['id'] in self.recents],key=lambda c:self.recents.index(c['id']))
        q=normalize(query.strip())
        aliases={'algebra di bool':'boole','algebra di boole':'boole','boolean':'boole','pitagora':'pitagora','pythagoras':'pitagora','pendenza':'pendenza','newton':'newton','cerchio':'cerchio','area triangolo':'area triangolo','gauss':'gauss','ohm':'ohm','derivate':'derivata','integrali':'integrale','matrici':'matrice'}
        q=aliases.get(q,q)
        if not q:return candidates
        ranked=[]
        for c in candidates:
            title=normalize(c['title']);hay=self.index[c['id']]
            score=200 if q==title else 160 if q in title else 110 if all(w in hay for w in q.split()) else WRatio(q,title)
            if score>=65:ranked.append((score,c))
        return [c for score,c in sorted(ranked,key=lambda a:-a[0])]
    def favorite(self,cid):
        if cid in self.favorites:self.db.execute('DELETE FROM favorites WHERE id=?',(cid,))
        else:self.db.execute('INSERT OR IGNORE INTO favorites VALUES(?)',(cid,))
        self.db.commit();self.reload()
    def visit(self,cid):
        self.db.execute('INSERT OR REPLACE INTO recent VALUES(?,?)',(cid,datetime.now(timezone.utc).isoformat()))
        self.db.commit()
        self.recents=[cid]+[v for v in self.recents if v!=cid][:39]
    def note(self,cid):
        row=self.db.execute('SELECT body FROM notes WHERE id=?',(cid,)).fetchone()
        return row[0] if row else ''
    def save_note(self,cid,text):
        self.db.execute('INSERT OR REPLACE INTO notes VALUES(?,?)',(cid,text));self.db.commit()
    def save_card(self,card):
        card=validate_personal(card)
        self.db.execute('INSERT OR REPLACE INTO personal VALUES(?,?)',(card['id'],json.dumps(card,ensure_ascii=False)));self.db.commit();self.reload();return card
    def delete_card(self,cid):
        if not cid.startswith('user-'):raise ValueError('Il catalogo distribuito è di sola lettura.')
        for table in ('personal','favorites','notes','recent'):self.db.execute(f'DELETE FROM {table} WHERE id=?',(cid,))
        self.db.commit();self.reload()
    def export(self):
        return {'schema_version':1,'cards':[c for c in self.cards if c['category']=='personali'],
                'notes':dict(self.db.execute('SELECT id,body FROM notes')),'favorites':list(self.favorites),
                'settings':dict(self.db.execute('SELECT key,value FROM settings'))}
    def import_data(self,data):
        if not isinstance(data,dict) or data.get('schema_version')!=1:raise ValueError('Formato di archivio non supportato.')
        raw=data.get('cards',[])
        if not isinstance(raw,list) or len(raw)>2000:raise ValueError('Massimo 2000 schede per importazione.')
        cards=[validate_personal(c) for c in raw]
        notes=data.get('notes',{});favorites=data.get('favorites',[]);settings=data.get('settings',{})
        if not isinstance(notes,dict) or not isinstance(favorites,list) or not isinstance(settings,dict):raise ValueError('Metadati archivio non validi.')
        for k,v in notes.items():
            if not isinstance(k,str) or not isinstance(v,str) or len(v)>100000:raise ValueError('Annotazioni non valide.')
        if 'theme' in settings and settings['theme'] not in ('light','dark'):raise ValueError('Tema archivio non valido.')
        if 'font_size' in settings:
            value=settings['font_size']
            if not isinstance(value,str) or not value.isdigit() or not 13<=int(value)<=26:raise ValueError('Dimensione del testo archivio non valida.')
        known=set(self.by_id)|{c['id'] for c in cards}
        with self.db:
            for c in cards:self.db.execute('INSERT OR REPLACE INTO personal VALUES(?,?)',(c['id'],json.dumps(c,ensure_ascii=False)))
            for k,v in notes.items():
                if k in known:self.db.execute('INSERT OR REPLACE INTO notes VALUES(?,?)',(k,v))
            for cid in favorites:
                if isinstance(cid,str) and cid in known:self.db.execute('INSERT OR IGNORE INTO favorites VALUES(?)',(cid,))
            for k,v in settings.items():
                if k in ('theme','font_size') and isinstance(v,str):self.db.execute('INSERT OR REPLACE INTO settings VALUES(?,?)',(k,v))
        self.reload();return len(cards)
    def setting(self,key,default=''):
        row=self.db.execute('SELECT value FROM settings WHERE key=?',(key,)).fetchone()
        return row[0] if row else default
    def set_setting(self,key,value):
        self.db.execute('INSERT OR REPLACE INTO settings VALUES(?,?)',(key,str(value)));self.db.commit()
    def close(self):self.db.close()

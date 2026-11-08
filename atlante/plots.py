"""Grafici Qt e costruzioni geometriche con scale metriche coerenti."""
import math
import numpy as np
import sympy as s
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg,NavigationToolbar2QT
from matplotlib.patches import Circle,Polygon,Arc,Wedge
from PyQt6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QLabel,QDoubleSpinBox,QPushButton,QFileDialog,QComboBox
from PyQt6.QtGui import QValidator
from atlante.engine import parse,numeric

ACCENT='#168b92'; GOLD='#ce9b45'; BLUE='#507ed0'

from atlante.sampling import sample_curve
from atlante.jobs import Jobs

class ScientificSpinBox(QDoubleSpinBox):
    def __init__(self,parent=None):
        super().__init__(parent);self.setDecimals(30);self.setRange(-1e100,1e100)
    def textFromValue(self,value):return f'{value:.8g}'
    def valueFromText(self,text):
        try:return numeric(text)
        except Exception:return 0.
    def validate(self,text,pos):
        try:
            float(text.replace(',','.'));return QValidator.State.Acceptable,text,pos
        except ValueError:return QValidator.State.Intermediate,text,pos

class PlotWidget(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent);self.card=None;self.dark=False;self.inputs={};self.free=False
        layout=QVBoxLayout(self);layout.setContentsMargins(12,12,12,12)
        self.caption=QLabel('Scegli una scheda con visualizzazione.');self.caption.setWordWrap(True);layout.addWidget(self.caption)
        row=QHBoxLayout();self.varbox=QComboBox();self.varbox.setAccessibleName('Parametro da variare');row.addWidget(self.varbox)
        self.lo=ScientificSpinBox();self.hi=ScientificSpinBox()
        for w in (self.lo,self.hi):w.setSingleStep(0.5)
        self.lo.setValue(-5);self.hi.setValue(5)
        self.from_label=QLabel('Da');self.to_label=QLabel('a');row.addWidget(self.from_label);row.addWidget(self.lo);row.addWidget(self.to_label);row.addWidget(self.hi)
        self.parameter=ScientificSpinBox();self.parameter.setAccessibleName('Valore del parametro geometrico');self.parameter.hide();row.addWidget(self.parameter)
        self.draw_button=QPushButton('Aggiorna');self.draw_button.clicked.connect(self.redraw);row.addWidget(self.draw_button)
        self.reset_button=QPushButton('Ripristina');self.reset_button.clicked.connect(self.reset);row.addWidget(self.reset_button)
        layout.addLayout(row)
        self.varbox.currentIndexChanged.connect(self.parameter_selected)
        self.figure=Figure(figsize=(7,5),dpi=100);self.canvas=FigureCanvasQTAgg(self.figure)
        self.toolbar=NavigationToolbar2QT(self.canvas,self);layout.addWidget(self.toolbar);layout.addWidget(self.canvas,1)
        self.export_button=QPushButton('Esporta grafico PNG / SVG');self.export_button.clicked.connect(self.export);layout.addWidget(self.export_button)
        self.jobs=Jobs(self);self.jobs.done.connect(self.curve_ready);self.jobs.failed.connect(lambda msg:self.caption.setText('Controlla i dati: '+msg))
        cancel=QPushButton('Annulla grafico');cancel.clicked.connect(self.jobs.cancel);row.addWidget(cancel)
        for control in (self.lo,self.hi,self.parameter):control.valueChanged.connect(self.jobs.cancel)
    def set_card(self,card,inputs=None):
        self.jobs.cancel()
        self.card=card;self.free=False;self.inputs={}
        if card.get('calculator'):
            for p in card['calculator']['inputs']:self.inputs[p['name']]=numeric(str((inputs or {}).get(p['name'],p['default'])))
        self.varbox.blockSignals(True);self.varbox.clear()
        if card.get('calculator'):
            for p in card['calculator']['inputs']:
                if card['plot']['kind']=='geometry' or not p.get('integer'):self.varbox.addItem(p['name']+' · '+p['label'],p['name'])
        elif card.get('plot',{}).get('kind')=='geometry':
            for name,value in self.geometry_defaults(card).items():self.varbox.addItem(name,name);self.inputs[name]=value
        self.varbox.blockSignals(False)
        self.reset()
    def geometry_defaults(self,card):
        t=card['title'].lower();p=card['plot']['preset']
        if p=='triangle':return {'a':3.,'b':4.,'c':5.}
        if p=='circle':return {'r':3.,'theta':math.pi/3}
        if p=='polygon':return {'n':6.} if 'poligono'in t else {'b':5.,'h':3.}
        if p=='solid':return {'r':2.,'h':4.}
        if p=='angles':return {'theta':math.pi/3}
        if p=='line':return {'m':1.,'q':1.}
        if p in ('ellipse','hyperbola'):return {'a':5.,'b':3.}
        if p=='parabola':return {'a':0.5,'h':0.,'k':0.}
        return {'r':2.}
    def reset(self):
        self.lo.setValue(-5);self.hi.setValue(5)
        if self.card and self.card.get('plot'):
            geometric=self.card['plot']['kind']=='geometry';self.parameter.setVisible(geometric);self.lo.setVisible(not geometric);self.hi.setVisible(not geometric)
            self.from_label.setText('Valore' if geometric else 'Da');self.to_label.setVisible(not geometric)
            if self.card['plot']['kind']=='sensitivity':
                k=self.card['plot']['variable'];i=self.varbox.findData(k)
                if i>=0:self.varbox.setCurrentIndex(i)
                value=self.inputs.get(k,1);self.lo.setValue(value*.1 if value>0 else value*2 if value<0 else -5);self.hi.setValue(value*2 if value>0 else abs(value)*2 if value<0 else 5)
            elif self.card['plot']['kind']=='geometry':
                self.parameter_selected()
        self.redraw(use_defaults=True)
    def parameter_selected(self,*args):
        if self.card and self.card.get('plot',{}).get('kind')=='geometry':
            self.parameter.setValue(self.inputs.get(self.varbox.currentData(),1))
    def set_function(self,expression,variable='x',start=-5,end=5):
        self.card=None;self.free=True;self.expression=expression;self.variable=variable
        self.parameter.hide();self.lo.show();self.hi.show()
        self.varbox.clear();self.varbox.addItem(variable,variable);self.lo.setValue(start);self.hi.setValue(end);self.redraw()
    def redraw(self,checked=False,use_defaults=False):
        self.jobs.cancel()
        self.figure.clear()
        try:
            if self.free:
                self.curve_request(self.expression,self.variable,{});return
            elif self.card and self.card.get('plot'):
                if self.card['plot']['kind']=='geometry':
                    values=self.inputs.copy()
                    if not use_defaults:
                        key=self.varbox.currentData()
                        if key:values[key]=self.parameter.value()
                    self.draw_geometry(values)
                else:
                    key=self.varbox.currentData();values={k:v for k,v in self.inputs.items() if k!=key}
                    self.curve_request(self.card['calculator']['expression'],key,values);return
            else:
                ax=self.figure.add_subplot(111);ax.text(.5,.5,'Nessuna visualizzazione associata',ha='center',va='center',transform=ax.transAxes)
            self.style_axes();self.figure.tight_layout();self.canvas.draw_idle()
        except Exception as exc:
            self.figure.clear();self.figure.add_subplot(111).axis('off');self.caption.setText('Controlla i dati: '+str(exc));self.style_axes();self.canvas.draw_idle()
    def curve_request(self,expression,key,values):
        self.caption.setText('Campionamento in corso · annullabile · massimo 15 secondi')
        self.canvas.draw_idle()
        self.curve_key=key
        self.jobs.start({'kind':'plot2d','expression':expression,'variable':key,'start':self.lo.value(),'end':self.hi.value(),'names':values,'card':self.card if not self.free else None})
    def curve_ready(self,result):
        self.figure.clear();ax=self.figure.add_subplot(111);xx=np.asarray(result['x']);yy=np.asarray(result['y'],dtype=float);key=self.curve_key
        if not self.free and self.card:
            field=next(p for p in self.card['calculator']['inputs'] if p['name']==key)
            valid=np.ones_like(xx,dtype=bool)
            if 'strict_min'in field:valid&=xx>field['strict_min']
            if 'min'in field:valid&=xx>=field['min']
            if 'max'in field:valid&=xx<=field['max']
            yy[~valid]=np.nan
            ax.set_xlabel(key+(' ['+field['unit']+']' if field['unit'] else ''));ax.set_ylabel('Risultato '+self.card['calculator'].get('output_unit',''))
            self.caption.setText('Sensibilità rispetto a '+key+' · altri parametri fissati ai dati del calcolatore.')
        else:
            ax.set_xlabel(key);ax.set_ylabel('f('+key+')');self.caption.setText('Grafico reale · '+self.expression)
        ax.plot(xx,yy,color=ACCENT,lw=2.3);self.style_axes();self.figure.tight_layout();self.canvas.draw_idle()
    def surface(self,result,expression):
        self.jobs.cancel();self.figure.clear();ax=self.figure.add_subplot(111,projection='3d');ax.plot_surface(np.asarray(result['x']),np.asarray(result['y']),np.asarray(result['z'],dtype=float),cmap='viridis',alpha=.85);ax.set_xlabel('x');ax.set_ylabel('y');ax.set_zlabel('f(x,y)');self.style_axes();self.canvas.draw_idle();self.caption.setText('Superficie · '+expression)
    def closeEvent(self,event):self.jobs.cancel();super().closeEvent(event)
    def draw_geometry(self,v):
        t=self.card['title'].lower();preset=self.card['plot']['preset']
        def get(k,d):return float(v.get(k,d))
        def point(ax,name,x,y):ax.plot(x,y,'o',color=GOLD,ms=5);ax.annotate(name,(x,y),xytext=(7,8),textcoords='offset points',fontsize=11)
        self.caption.setText('Costruzione di riferimento · '+self.card['title']+' · assi con uguale scala. Scegli un parametro, modifica il suo valore e premi Aggiorna.')
        if preset in ('solid','space'):
            ax=self.figure.add_subplot(111,projection='3d')
            u=np.linspace(0,2*np.pi,60);w=np.linspace(0,np.pi,40);r=get('r',2)
            if r<=0:raise ValueError('Raggio strettamente positivo richiesto.')
            if 'piano' in t:
                xx,yy=np.meshgrid(np.linspace(-3,3,12),np.linspace(-3,3,12));zz=(6-xx-yy)/2;ax.plot_surface(xx,yy,zz,color=ACCENT,alpha=.55);ax.text(0,0,3,'x + y + 2z = 6')
            elif any(k in t for k in ('sfera','ellissoide','quadric')):
                a,b,c=(3,2,1) if 'ellissoide'in t or 'quadric'in t else (r,r,r)
                ax.plot_surface(a*np.outer(np.cos(u),np.sin(w)),b*np.outer(np.sin(u),np.sin(w)),c*np.outer(np.ones_like(u),np.cos(w)),color=ACCENT,alpha=.65,linewidth=.2)
                ax.plot([0,a],[0,0],[0,0],color=GOLD);ax.text(a,0,0,f'a={a:g}')
            elif 'cilindro'in t or 'cono'in t:
                h=get('h',4)
                if h<=0:raise ValueError('Altezza positiva richiesta.')
                uu,zz=np.meshgrid(u,np.linspace(0,h,25));rr=r*(1-zz/h) if 'cono'in t else r
                ax.plot_surface(rr*np.cos(uu),rr*np.sin(uu),zz,color=ACCENT,alpha=.6);ax.plot([0,0],[0,0],[0,h],color=GOLD);ax.text(0,0,h,f'h={h:g}')
            elif any(k in t for k in ('prisma','piramide')):
                from mpl_toolkits.mplot3d.art3d import Poly3DCollection
                h=get('h',4);area=get('A',9)
                if h<=0 or area<=0:raise ValueError('Area di base e altezza positive richieste.')
                b=math.sqrt(area);p=np.array([[0,0,0],[b,0,0],[b,b,0],[0,b,0]])
                if 'piramide'in t:
                    apex=np.array([b/2,b/2,h]);faces=[p]+[[p[i],p[(i+1)%4],apex] for i in range(4)]
                else:
                    top=p+[0,0,h];faces=[p,top]+[[p[i],p[(i+1)%4],top[(i+1)%4],top[i]] for i in range(4)]
                ax.add_collection3d(Poly3DCollection(faces,facecolor=ACCENT,edgecolor=BLUE,alpha=.4));ax.set_xlim(0,b);ax.set_ylim(0,b);ax.set_zlim(0,h);ax.text(b,0,h,f'h={h:g}')
            else:
                ax.plot([0,2],[0,3],[0,6],color=ACCENT,lw=2);ax.scatter([0,2],[0,3],[0,6],color=GOLD);ax.text(0,0,0,'A');ax.text(2,3,6,'B (2,3,6)')
            ax.set_xlabel('x');ax.set_ylabel('y');ax.set_zlabel('z');ax.set_aspect('equal');return
        ax=self.figure.add_subplot(111);ax.set_aspect('equal',adjustable='datalim');ax.set_xlabel('x');ax.set_ylabel('y')
        if self.card['category']=='analitica' and self.analytic_detail(ax,v,point):return
        if preset=='triangle':
            a,b,c=get('a',3),get('b',4),get('c',5)
            if 'pitagora'in t:c=math.hypot(a,b)
            if 'euclide'in t:
                if 'primo'in t:
                    c=get('c',25);p=get('p',9)
                    if not 0<p<c:raise ValueError('La proiezione deve essere compresa fra 0 e l’ipotenusa.')
                    cx=p;cy=math.sqrt(p*(c-p))
                else:p=get('p',9);q=get('q',16);c=p+q;cx=p;cy=math.sqrt(p*q)
            elif 'bisettrice'in t:
                c=get('a',6);b=get('b',4)
                if min(b,c)<=0:raise ValueError('Lati adiacenti positivi richiesti.')
                cx=b/2;cy=b*math.sqrt(3)/2
            elif 'area del triangolo'in t:c=get('b',6);cx=c*.3;cy=get('h',4)
            elif 'somma degli angoli'in t:
                al,be=get('alpha',math.pi/3),get('beta',math.pi/4)
                if al<=0 or be<=0 or al+be>=math.pi:raise ValueError('Occorrono angoli positivi con somma minore di π.')
                c=5;cx=c*math.sin(be)*math.cos(al)/math.sin(al+be);cy=c*math.sin(be)*math.sin(al)/math.sin(al+be)
            else:
                if min(a,b,c)<=0 or a+b<=c or a+c<=b or b+c<=a:raise ValueError('Lati incompatibili: triangolo degenere o impossibile.')
                cx=(b*b+c*c-a*a)/(2*c);cy=math.sqrt(max(b*b-cx*cx,0))
            if 'baricentro'in t:
                median=math.hypot((c+cx)/2,cy/2);length=get('l',median)
                if length<=0:raise ValueError('La mediana deve avere lunghezza positiva.')
                factor=length/median;c*=factor;cx*=factor;cy*=factor
            ax.add_patch(Polygon([[0,0],[c,0],[cx,cy]],closed=True,facecolor=ACCENT+'22',edgecolor=ACCENT,lw=2))
            point(ax,'A',0,0);point(ax,'B',c,0);point(ax,'C',cx,cy)
            ax.annotate(f'AB={c:.3g}',(c/2,0),xytext=(0,-22),textcoords='offset points',ha='center')
            ax.text(cx*.5-.25,cy*.5,f'AC={math.hypot(cx,cy):.3g}');ax.text((cx+c)/2,cy/2,f'BC={math.hypot(c-cx,cy):.3g}')
            if 'mediana'in t or 'baricentro'in t:
                mx,my=(c+cx)/2,cy/2;ax.plot([0,mx],[0,my],'--',color=GOLD,label='mediana AM');point(ax,'M',mx,my)
                if 'baricentro'in t:point(ax,'G',(c+cx)/3,cy/3)
            elif 'bisettrice'in t:
                ac=math.hypot(cx,cy);dx=(ac*c+c*cx)/(ac+c);dy=c*cy/(ac+c);ax.plot([0,dx],[0,dy],'--',color=GOLD,label='bisettrice AD');point(ax,'D',dx,dy)
            elif 'inscritta'in t:
                aa=math.hypot(c-cx,cy);bb=math.hypot(cx,cy);per=aa+bb+c;ix=(bb*c+c*cx)/per;iy=c*cy/per;rr=c*cy/per;ax.add_patch(Circle((ix,iy),rr,fill=False,color=GOLD,lw=2));point(ax,'I',ix,iy)
            elif 'circoscritta'in t:
                ux=c/2;uy=(cx*cx+cy*cy-c*cx)/(2*cy);rr=math.hypot(ux,uy);ax.add_patch(Circle((ux,uy),rr,fill=False,color=GOLD));point(ax,'O',ux,uy)
            else:
                ax.plot([cx,cx],[0,cy],'--',color=GOLD);point(ax,'H',cx,0);ax.text(cx+.12,cy/2,f'h={cy:.3g}')
            if 'similitudine'in t or 'congruenza'in t:
                k=get('k',1)
                if k<=0:raise ValueError('Rapporto positivo richiesto.')
                shift=c*1.5;ax.add_patch(Polygon([[shift,0],[shift+k*c,0],[shift+k*cx,k*cy]],closed=True,fill=False,edgecolor=BLUE,lw=2));ax.text(shift,k*cy+.15,f'k={k:g} · lato corrispondente={k*math.hypot(c-cx,cy):.3g}')
            ax.autoscale_view();ax.margins(.25)
        elif preset=='angles':
            angle=get('alpha',get('theta',math.pi/3))
            if not 0<=angle<=math.pi:raise ValueError('Angolo compreso fra 0 e π richiesto.')
            if 'parallele'in t or 'talete'in t:
                for yy in (-1,0,1):ax.plot([-3,3],[yy,yy],color=ACCENT)
                ax.plot([-2,2],[-2,2],color=GOLD);ax.plot([-1.2,1.2],[-2,2],color=BLUE);ax.text(-2,1.2,'r ∥ s ∥ t');point(ax,'A',-1,-1);point(ax,'B',0,0);point(ax,'C',1,1)
            else:
                end=math.pi/2 if 'complementari'in t else math.pi
                if angle>end:raise ValueError('Angolo oltre il riferimento complementare o supplementare.')
                ax.plot([0,3],[0,0],color=ACCENT);ax.plot([0,3*np.cos(end)],[0,3*np.sin(end)],color=ACCENT);ax.plot([0,3*np.cos(angle)],[0,3*np.sin(angle)],color=GOLD)
                ax.add_patch(Arc((0,0),1.5,1.5,theta1=0,theta2=np.degrees(angle),color=BLUE));ax.add_patch(Arc((0,0),2,2,theta1=np.degrees(angle),theta2=np.degrees(end),color=ACCENT));ax.text(1,.3,f'α={np.degrees(angle):.1f}°');ax.text(-.4,1.3,f'β={np.degrees(end-angle):.1f}°');point(ax,'O',0,0)
            ax.set_xlim(-3.5,3.5);ax.set_ylim(-2,3.5)
        elif preset=='polygon':
            b,h=get('b',5),get('h',3)
            if min(b,h)<=0:raise ValueError('Misure positive richieste.')
            if 'rombo'in t:a=get('a',6);b=get('b',8);pts=[[-a/2,0],[0,b/2],[a/2,0],[0,-b/2]]
            elif 'regolare'in t or 'angoli interni'in t:
                n=int(get('n',6));radius=3.
                if 'P'in v and 'a'in v:
                    ratio=v['P']/(2*v['a']);n=min(range(3,61),key=lambda k:abs(k*math.tan(math.pi/k)-ratio));radius=v['a']/math.cos(math.pi/n)
                if n<3 or n>60:raise ValueError('Numero di lati fra 3 e 60 richiesto.')
                th=np.linspace(0,2*np.pi,n,endpoint=False);pts=np.column_stack([radius*np.cos(th),radius*np.sin(th)])
            elif 'trapezio'in t:B=get('B',8);pts=[[0,0],[B,0],[(B+b)/2,h],[(B-b)/2,h]]
            elif 'parallelogramma'in t:pts=[[0,0],[b,0],[b+1,h],[1,h]]
            elif 'quadrato'in t:l=get('l',4);pts=[[0,0],[l,0],[l,l],[0,l]];ax.plot([0,l],[0,l],'--',color=GOLD)
            else:pts=[[0,0],[b,0],[b,h],[0,h]]
            ax.add_patch(Polygon(pts,closed=True,facecolor=ACCENT+'22',edgecolor=ACCENT,lw=2))
            for i,(x,y) in enumerate(pts):point(ax,chr(65+i),x,y)
            ax.autoscale_view();ax.margins(.3)
        elif preset in ('circle','ellipse','hyperbola','parabola'):
            if preset=='circle':
                r=get('r',3);theta=2*get('beta',math.pi/6) if 'angolo al centro'in t else get('theta',math.pi/3)
                if r<=0:raise ValueError('Il raggio deve essere positivo.')
                if not 0<=theta<=2*math.pi:raise ValueError('Angolo fra 0 e 2π richiesto.')
                ax.add_patch(Circle((0,0),r,facecolor=ACCENT+'15',edgecolor=ACCENT,lw=2));point(ax,'O',0,0);point(ax,'A',r,0)
                ax.plot([0,r],[0,0],color=GOLD);ax.text(r/2,.12,f'r={r:g}')
                if any(k in t for k in ('arco','settore','corda','angolo')):
                    x,y=r*np.cos(theta),r*np.sin(theta);point(ax,'B',x,y);ax.plot([0,x],[0,y],color=GOLD)
                    ax.add_patch(Wedge((0,0),r,0,np.degrees(theta),facecolor=GOLD+'33'))
                    if 'corda'in t:ax.plot([r,x],[0,y],color=BLUE,lw=2)
                    if 'angolo al centro'in t:
                        phi=(theta+2*math.pi)/2;px,py=r*np.cos(phi),r*np.sin(phi);point(ax,'P',px,py);ax.plot([r,px,x],[0,py,y],color=BLUE);ax.text(px,py-.4,f'β={np.degrees(theta/2):.1f}°')
                    ax.text(.3,.3,f'θ={np.degrees(theta):.1f}°')
                ax.set_xlim(-r*1.35,r*1.35);ax.set_ylim(-r*1.35,r*1.35)
            elif preset=='ellipse':
                a,b=get('a',5),get('b',3)
                if not a>=b>0:raise ValueError('Occorre a≥b>0.')
                th=np.linspace(0,2*np.pi,500);ax.plot(a*np.cos(th),b*np.sin(th),color=ACCENT,lw=2);focus=math.sqrt(a*a-b*b);point(ax,'F₁',-focus,0);point(ax,'F₂',focus,0);ax.set_xlim(-a*1.3,a*1.3);ax.set_ylim(-a*.85,a*.85)
            elif preset=='hyperbola':
                a,b=get('a',3),get('b',2)
                if min(a,b)<=0:raise ValueError('Semiassi positivi richiesti.')
                u=np.linspace(-1.5,1.5,400)
                for sign in (-1,1):ax.plot(sign*a*np.cosh(u),b*np.sinh(u),color=ACCENT,lw=2)
                xx=np.linspace(-a*3,a*3,50);ax.plot(xx,b/a*xx,'--',color=GOLD);ax.plot(xx,-b/a*xx,'--',color=GOLD);point(ax,'F₁',-math.hypot(a,b),0);point(ax,'F₂',math.hypot(a,b),0)
            else:
                a,h,k=get('a',.5),get('h',0),get('k',0)
                if a==0:raise ValueError('a non può essere zero per una parabola.')
                xx=np.linspace(h-3,h+3,400);ax.plot(xx,a*(xx-h)**2+k,color=ACCENT,lw=2);point(ax,'V',h,k);point(ax,'F',h,k+1/(4*a));ax.axhline(k-1/(4*a),color=GOLD,ls='--',label='Direttrice');ax.legend()
        else:
            if self.card.get('calculator') and all(k in v for k in ('x1','x2','y1','y2')):
                point(ax,'A',v['x1'],v['y1']);point(ax,'B',v['x2'],v['y2']);ax.plot([v['x1'],v['x2']],[v['y1'],v['y2']],color=ACCENT,lw=2)
            elif 'implicita'in t or 'punto-retta'in t:
                a,b,c=get('a',1),get('b',-1),get('c',1)
                if a*a+b*b==0:raise ValueError('Normale nulla: non è una retta.')
                xx=np.linspace(-5,5,100)
                if b:ax.plot(xx,(-a*xx-c)/b,color=ACCENT,lw=2)
                else:ax.axvline(-c/a,color=ACCENT,lw=2)
                px,py=get('x0',0),get('y0',0);d=(a*px+b*py+c)/(a*a+b*b);hx,hy=px-d*a,py-d*b;point(ax,'P',px,py);point(ax,'H',hx,hy);ax.plot([px,hx],[py,hy],'--',color=GOLD)
            else:
                m,q=get('m',1),get('q',1);xx=np.linspace(-4,4,100);ax.plot(xx,m*xx+q,color=ACCENT,lw=2,label=f'y={m:g}x+{q:g}');point(ax,'A',0,q);point(ax,'B',1,m+q);ax.legend()
            ax.margins(.3)
    def analytic_detail(self,ax,v,point):
        """Esempi didattici specifici per le relazioni fra punti, rette e tangenti."""
        cid=int(self.card['id'].split('-')[-1]);t=self.card['title'].lower()
        if cid in (2,3,4,15):
            if cid==2:
                A=np.array([2.,4.]);B=np.array([6.,10.]);M=(A+B)/2
                ax.plot([*A[:1],*B[:1]],[A[1],B[1]],color=ACCENT);point(ax,'A (2,4)',*A);point(ax,'B (6,10)',*B);point(ax,'M (4,7)',*M)
            elif cid==3:
                ax.plot([0,6],[0,3],color=ACCENT);point(ax,'A',0,0);point(ax,'B',6,3);point(ax,'P · rapporto 2:1',4,2)
            else:
                A=np.array([0.,0.]);B=np.array([6.,0.]);C=np.array([0.,3.]);ax.add_patch(Polygon([A,B,C],closed=True,facecolor=ACCENT+'22',edgecolor=ACCENT,lw=2))
                for name,p in zip('ABC',(A,B,C)):point(ax,name,*p)
                if cid==4:
                    for P,Q,R in ((A,B,C),(B,A,C),(C,A,B)):
                        mid=(Q+R)/2;ax.plot([P[0],mid[0]],[P[1],mid[1]],'--',color=GOLD)
                    point(ax,'G (2,1)',2,1)
                else:ax.text(1,1,'Area = 9')
            ax.autoscale_view();ax.margins(.3);return True
        if cid in (7,9,10,11,13,14,29,30):
            xx=np.linspace(-3,5,100)
            if cid==7:ax.axvline(2,color=ACCENT,label='x = 2');point(ax,'A',2,1);point(ax,'B',2,5)
            elif cid==9:
                ax.plot(xx,(1-xx)/2,color=ACCENT,label='x+2y−1=0');ax.plot(xx,(-3-2*xx)/4,color=GOLD,label='2x+4y+3=0')
            elif cid==10:ax.axvline(2,color=ACCENT,label='x=2');ax.axhline(3,color=GOLD,label='y=3')
            elif cid==11:
                ax.plot(xx,xx,color=ACCENT,label='y=x');ax.plot(xx,2-xx,color=GOLD,label='y=2−x');point(ax,'P (1,1)',1,1)
            elif cid==13:
                ax.plot(xx,2-xx,color=ACCENT,label='x+y−2=0');point(ax,'P (0,0)',0,0);point(ax,'H (1,1)',1,1);ax.plot([0,1],[0,1],'--',color=GOLD)
            elif cid==14:
                ax.axhline(0,color=ACCENT,label='y=0');ax.plot(xx,xx,color=GOLD,label='y=x');ax.add_patch(Arc((0,0),2,2,theta1=0,theta2=45,color=BLUE));ax.text(1,.3,'45°')
            elif cid==29:
                ax.add_patch(Circle((2,-1),3,fill=False,color=ACCENT,lw=2));point(ax,'O′ (2,−1)',2,-1);ax.axvline(2,color=GOLD,ls='--');ax.axhline(-1,color=GOLD,ls='--');point(ax,'O',0,0)
            else:
                theta=float(v.get('m',math.pi/4));ax.plot([-3,3],[0,0],color=ACCENT,label='asse x');ax.plot([0,3*np.cos(theta)],[0,3*np.sin(theta)],color=GOLD,label='asse X ruotato');ax.plot([0,-3*np.sin(theta)],[0,3*np.cos(theta)],color=GOLD)
            if ax.get_legend_handles_labels()[0]:ax.legend()
            ax.autoscale_view();ax.margins(.25);return True
        if cid in (16,18,19,22,25,28):
            if cid in (16,18,19):
                r=5 if cid==18 else 1 if cid==19 else float(v.get('r',3));xc,yc=(1,-2) if cid==16 else (0,0)
                ax.add_patch(Circle((xc,yc),r,fill=False,color=ACCENT,lw=2));point(ax,'C',xc,yc)
                if cid==18:
                    xx=np.linspace(-6,6,100);ax.plot(xx,(25-3*xx)/4,color=GOLD,label='3x+4y=25');point(ax,'P (3,4)',3,4);ax.plot([0,3],[0,4],'--',color=BLUE)
                elif cid==19:ax.axhline(1,color=GOLD,label='y=1');point(ax,'T (0,1)',0,1)
                else:ax.plot([xc,xc+r],[yc,yc],color=GOLD);ax.text(xc+r/2,yc+.15,f'r={r:g}')
                ax.set_xlim(xc-r*1.5,xc+r*1.5);ax.set_ylim(yc-r*1.5,yc+r*1.5)
            elif cid==22:
                xx=np.linspace(-2,3,200);ax.plot(xx,xx*xx,color=ACCENT,label='y=x²');ax.plot(xx,2*xx-1,color=GOLD,label='y=2x−1');point(ax,'P (1,1)',1,1)
            elif cid==25:
                th=np.linspace(0,2*np.pi,300);ax.plot(2*np.cos(th),np.sin(th),color=ACCENT,label='x²/4+y²=1');ax.axvline(2,color=GOLD,label='x=2');point(ax,'P (2,0)',2,0)
            else:
                th=np.linspace(0,2*np.pi,300);ax.plot(3*np.cos(th),2*np.sin(th),color=ACCENT,label='Tipo ellittico');ax.text(-2,-3,'B²−4AC < 0; controllare anche la degenerazione')
            ax.autoscale_view();ax.margins(.25)
            if ax.get_legend_handles_labels()[0]:ax.legend()
            return True
        return False
    def style_axes(self):
        bg='#111d2b' if self.dark else '#ffffff';fg='#d9e7ef' if self.dark else '#334e60';grid='#8196a833'
        self.figure.set_facecolor(bg)
        for ax in self.figure.axes:
            ax.set_facecolor(bg);ax.tick_params(colors=fg,labelsize=9);ax.xaxis.label.set_color(fg);ax.yaxis.label.set_color(fg)
            if hasattr(ax,'zaxis'):ax.zaxis.label.set_color(fg)
            ax.grid(True,color=grid,linewidth=.7)
            for sp in ax.spines.values():sp.set_color('#8196a866')
            for txt in ax.texts:txt.set_color(fg)
            legend=ax.get_legend()
            if legend:
                legend.get_frame().set_facecolor(bg)
                for txt in legend.get_texts():txt.set_color(fg)
    def export(self):
        path,_=QFileDialog.getSaveFileName(self,'Esporta visualizzazione','grafico.png','PNG (*.png);;SVG (*.svg)')
        if path:self.figure.savefig(path,dpi=180,bbox_inches='tight',facecolor=self.figure.get_facecolor())

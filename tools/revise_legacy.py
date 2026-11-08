"""Correzioni editoriali motivate della prima edizione; ID sempre conservati."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
# indici: 0 titolo, 1 LaTeX, 2 espressione, 3 dati, 4 spiegazione, 5 ipotesi, 6 esempio.
CHANGES={
 'base-050':{5:'x non nullo; n intero anche negativo e coefficiente normalizzato con 1≤∣a∣<10.'},
 'classica-030':{5:'Stesso arco sotteso non degenere, vertice alla circonferenza sul suo arco complementare; 0<β<π e angolo al centro riferito all’arco sotteso, anche riflesso.'},
 'base-024':{0:'Equazione quadratica: ramo con segno +',5:'a diverso da zero e Δ=b²−4ac≥0. Il ramo + è la radice maggiore se a>0 e quella minore se a<0.'},
 'base-008':{5:'Pesi u,w non negativi con u+w>0; a,b valori della stessa grandezza. Pesi reali, non necessariamente interi.'},
 'analitica-015':{0:'Area di un triangolo in coordinate',4:'Il determinante delle coordinate misura il doppio dell’area orientata. Il valore assoluto nella formula restituisce l’area geometrica, indipendente dall’ordine dei vertici.'},
 'analisi-027':{5:'Forma 0/0 o ∞/∞, f e g derivabili in un intorno bucato unilatero, g′ non nulla; il limite di f′/g′ deve esistere finito o infinito. Per un limite bilatero verificare entrambi i lati.'},
 'analisi-030':{5:'Ipotesi sufficiente: f di classe Cⁿ in un intorno di a. Resto di Peano per x→a; non è una stima uniforme dell’errore su intervalli grandi.'},
 'analisi-043':{1:r'\int_a^b f(x)dx=\lim_{\max_i\Delta x_i\to0}\sum_i f(\xi_i)\Delta x_i',5:'a<b, partizioni di [a,b] con ampiezza massima che tende a zero, ξ_i nel rispettivo sottointervallo; f limitata e Riemann integrabile.'},
 'analisi-065':{1:r'\int_a^b f\approx\frac h3\left[f_0+4\sum_{\substack{1\le i\le n-1\\i\ \mathrm{dispari}}}f_i+2\sum_{\substack{2\le i\le n-2\\i\ \mathrm{pari}}}f_i+f_n\right]'},
 'multivariabile-032':{1:r'y\prime+p(x)y=q(x),\quad\mu=e^{\int p(x)dx},\quad y=\frac{\int\mu q\,dx+C}{\mu}'},
 'analisi-036':{5:'a reale diverso da −1 e x>0 come dominio sufficiente; per potenze intere si estende agli intervalli in cui integranda e primitiva sono definite.'},
 'analisi-061':{5:'Entrambi i limiti finiti, m diverso da zero per un asintoto obliquo. Se m=0 e q è finito si ha un asintoto orizzontale. Studiare separatamente +∞ e −∞.'},
 'multivariabile-034':{5:'K>0 e r>0 per il modello di crescita; y₀>0 e C=(K−y₀)/y₀; il denominatore deve restare positivo nell’intervallo scelto. La soluzione di equilibrio y=0 va aggiunta separatamente.'},
 'lineare-037':{5:'Fattorizzazione QR ridotta per colonne indipendenti; esiste anche per matrici di rango carente, ma la decomposizione ridotta va trattata con pivoting o basi non uniche.'},
 'probabilita-023':{5:'n≥2 intero; somme coerenti con dati reali: Σxᵢ²≥(Σxᵢ)²/n. Non distorsione sotto campionamento iid con varianza finita.'},
 'meccanica-010':{5:'Stessa quota iniziale e finale, assenza d’aria, 0≤θ≤π/2; gli estremi sono casi limite di gittata nulla. Uscita m.'},
 'meccanica-023':{5:'Punto materiale in un sistema inerziale, massa costante. Per corpi estesi il lavoro reale totale cambia la cinetica totale inclusa la rotazione; il lavoro della risultante lungo il CM riguarda la sola parte traslazionale.'},
 'meccanica-028':{5:'F e v del calcolatore sono moduli non negativi e θ∈[0,π] è l’angolo fra i vettori nello stesso istante; P può essere negativa. Uscita W.'},
 'meccanica-034':{5:'r e F sono moduli non negativi; θ è l’angolo fra vettore posizione e forza, 0≤θ≤π. La formula dà il modulo del momento; il verso segue r×F. Uscita N·m.'},
 'termo-012':{5:'Re≪1, fluido newtoniano, sfera lontana dalle pareti; v è la rapidità relativa non negativa. Il calcolatore dà il modulo della resistenza, diretto contro il moto. Uscita N.'},
 'termo-020':{5:'Corpo grigio e ambiente ampio uniforme, fattore di vista unitario; 0≤ε≤1 e temperature assolute positive. Potenza netta positiva uscente se T₁>T₂. Uscita W.'},
 'termo-031':{5:'Q_h>0 e 0≤Q_c≤Q_h sono moduli dei calori del ciclo motore; 0≤η≤1. La formula non descrive direttamente il COP di un frigorifero.'},
 'termo-033':{1:r'\Delta S=S_f-S_i=\int_i^f\frac{\delta Q_{rev}}T'},
 'onde-008':{5:'Oscillatore lineare con ω₀>0, β>0 e forzante sinusoidale in regime stazionario. Un picco a frequenza positiva esiste solo se ω₀²>2β²; allora ω_r=√(ω₀²−2β²).'},
 'onde-021':{5:'a=n₁>0 e b=n₂>0; 0≤θ₁≤π/2. Se n₁ sinθ₁>n₂ non esiste un angolo rifratto reale: riflessione totale interna. Uscita θ₂ in rad.'},
 'elettro-002':{1:r'E_r=\frac{q}{4\pi\epsilon_0r^2}',4:'Il calcolatore restituisce la componente radiale orientata E_r: positiva verso l’esterno per q>0 e negativa verso il centro per q<0. Il modulo è il valore assoluto.'},
 'elettro-010':{5:'q è il modulo positivo di ciascuna carica e d≥0 è la distanza; il vettore d va dalla carica negativa a quella positiva. Uscita del modulo p in C·m.'},
 'elettro-011':{5:'p ed E sono moduli non negativi, θ∈[0,π]. La formula dà il modulo; il vettore è p×E. Dipolo rigido, campo uniforme; uscita N·m.'},
 'elettro-012':{5:'Condensatore lineare passivo: Q e V sono grandezze con segni coerenti e Q/V≥0, V≠0. Uscita F.'},
 'elettro-028':{5:'v è rapidità non negativa, B modulo non negativo e θ∈[0,π]. Il verso della forza è quello di q(v×B); la formula restituisce il modulo in N.'},
 'elettro-030':{5:'Regime non relativistico; v è rapidità perpendicolare positiva, B>0 e q≠0. Per velocità obliqua usare v_perp, con moto elicoidale. Uscita m.'},
 'elettro-031':{1:r'F=\lvert I\rvert LB\sin\theta',2:'Abs(current)*L*B*sin(theta)',5:'Filo rettilineo e campo uniforme; L>0, B≥0 e θ∈[0,π]. Il modulo usa |I|; il verso segue I L×B con la convenzione di corrente. Uscita N.'},
 'elettro-032':{1:r'B_\varphi=\frac{\mu_0I}{2\pi r}',5:'Componente azimutale orientata per filo idealmente infinito nel vuoto, r>0. Il segno di I fissa il verso; per il modulo usare |B_phi|. Uscita T.'},
 'elettro-033':{1:r'B_z=\frac{\mu_0I}{2R}',5:'Spira circolare sottile nel vuoto; componente assiale orientata secondo la mano destra per la corrente positiva. Uscita T.'},
 'elettro-034':{1:r'B_z=\mu_0\frac NL I',5:'Solenoide lungo rispetto al diametro, aria o vuoto, lontano dagli estremi; N intero positivo e L>0. Componente assiale orientata, uscita T.'},
 'moderna-009':{5:'energy=φ≥0. Se hf<φ non si ha emissione nel modello a un fotone: il calcolatore segnala la soglia e non presenta un’energia cinetica negativa. Uscita J.'},
 'moderna-010':{5:'p è il modulo strettamente positivo della quantità di moto. Uscita m. Per p=0 non è definita una lunghezza d’onda finita.'},
 'moderna-017':{5:'N₀≥0 come popolazione media iniziale, t≥0 e λ=rate>0. È un valore atteso, non il conteggio deterministico di un singolo campione.'},
 'moderna-019':{5:'λ=rate>0 e N≥0 riferiti allo stesso istante; uscita Bq, cioè s⁻¹ di decadimenti. Non è una dose assorbita.'},
}

def revise():
    for key in sorted({cid.rsplit('-',1)[0] for cid in CHANGES}):
        path=ROOT/'contenuti'/f'{key}.txt';lines=path.read_text(encoding='utf-8').splitlines()
        for cid,changes in CHANGES.items():
            if not cid.startswith(key+'-'):continue
            index=int(cid.rsplit('-',1)[1])-1;parts=lines[index].split('|')
            for field,value in changes.items():parts[field]=value.replace('|',r'\lvert' if field==1 else '∣')
            lines[index]='|'.join(parts)
        path.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(f'{len(CHANGES)} schede con chiarimenti o correzioni editoriali applicati.')

if __name__=='__main__':revise()

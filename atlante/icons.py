"""Icone SVG autonome per materie e azioni: nessun font o servizio esterno."""
from functools import lru_cache
from PyQt6.QtCore import QByteArray,Qt
from PyQt6.QtGui import QIcon,QPixmap,QPainter
from PyQt6.QtSvg import QSvgRenderer

PATHS={
 'book':'<path d="M3 4h6a3 3 0 0 1 3 3v14a4 4 0 0 0-4-2H3zM12 7a3 3 0 0 1 3-3h6v15h-5a4 4 0 0 0-4 2"/>',
 'home':'<rect x="3" y="3" width="7" height="7" rx="2"/><rect x="14" y="3" width="7" height="7" rx="2"/><rect x="3" y="14" width="7" height="7" rx="2"/><rect x="14" y="14" width="7" height="7" rx="2"/>',
 'star':'<path d="m12 3 2.8 5.7 6.2.9-4.5 4.4 1.1 6.2-5.6-3-5.6 3 1.1-6.2L3 9.6l6.2-.9z"/>',
 'search':'<circle cx="10" cy="10" r="6"/><path d="m15 15 6 6"/>',
 'lab':'<path d="M9 3h6M10 3v7L4 20h16l-6-10V3M7 15h10"/>',
 'sun':'<circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1 1m12 12 1 1M5 19l1-1M18 6l1-1"/>',
 'moon':'<path d="M20 15.5A9 9 0 0 1 8.5 4a8.8 8.8 0 1 0 11.5 11.5Z"/>',
 'plus':'<path d="M12 4v16M4 12h16"/>',
 'clock':'<circle cx="12" cy="12" r="9"/><path d="M12 6v6l4 2"/>',
 'copy':'<rect x="8" y="8" width="12" height="13" rx="2"/><path d="M16 8V3H3v13h5"/>',
 'arrow':'<path d="M19 12H5m6-6-6 6 6 6"/>',
 'folder':'<path d="M3 6h7l2 3h9v12H3z"/>',
 'sigma':'<path d="M19 4H5l7 8-7 8h14"/>',
 'export':'<path d="M12 3v12m-4-4 4 4 4-4M4 15v6h16v-6"/>',
 'import':'<path d="M12 15V3m-4 4 4-4 4 4M4 15v6h16v-6"/>',
 'save':'<path d="m4 3 14 0 3 3v15H3V3Zm3 0v6h10V3M7 21v-8h10v8"/>',
 'edit':'<path d="m15 4 5 5M4 15 16 3l5 5L9 20l-6 1z"/>',
 'trash':'<path d="M4 6h16M9 6V3h6v3M6 6l1 15h10l1-15M10 10v7m4-7v7"/>',
 'more':'<circle cx="5" cy="12" r="1.5"/><circle cx="12" cy="12" r="1.5"/><circle cx="19" cy="12" r="1.5"/>',
 'calculator':'<rect x="5" y="2" width="14" height="20" rx="2"/><path d="M8 6h8M8 10h1m6 0h1M8 14h1m6 0h1M8 18h1m6 0h1"/>',
 'plot':'<path d="M3 3v18h18M6 17l4-6 4 3 6-9"/>',
 'notes':'<path d="M5 2h10l5 5v15H5zM15 2v6h5M8 12h9M8 16h7"/>',
 'check':'<path d="m4 12 5 5L20 5"/>',
 'reset':'<path d="M4 10a8 8 0 1 1 1 8M4 4v6h6"/>',
 'stop':'<rect x="5" y="5" width="14" height="14" rx="2"/>',
 'help':'<circle cx="12" cy="12" r="9"/><path d="M9 8a3 3 0 1 1 5 2c-2 1-2 2-2 3m0 4v.1"/>',
 'legend':'<path d="M3 5h3v3H3zM3 11h3v3H3zM3 17h3v3H3zM10 6h11M10 12h11M10 18h11"/>',
 'math':'<path d="M4 6h16M8 6v13M16 6v10q0 4 4 2"/>',
 'triangle':'<path d="M3 20 10 3l11 17zM5 16l4 1-1 3"/>',
 'coordinates':'<path d="M3 12h18M12 3v18M5 19Q9 3 19 5"/>',
 'sine':'<path d="M2 12h20M3 12c3-13 6-13 9 0s6 13 9 0"/>',
 'integral':'<path d="M17 3c-4-2-5 1-5 5v8c0 4-1 7-5 5M4 12h3m10 0h3"/>',
 'surface':'<path d="M3 17q9-18 18 0M3 17q9-8 18 0M7 13q5 7 10 0M7 9q5 6 10 0M12 3v18"/>',
 'matrix':'<path d="M6 3H3v18h3M18 3h3v18h-3M8 7h1m6 0h1M8 12h1m6 0h1M8 17h1m6 0h1"/>',
 'dice':'<rect x="3" y="3" width="18" height="18" rx="3"/><circle cx="7" cy="7" r="1"/><circle cx="17" cy="7" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="7" cy="17" r="1"/><circle cx="17" cy="17" r="1"/>',
 'pendulum':'<path d="M4 3h16M12 3 7 17M12 3l5 14"/><circle cx="7" cy="18" r="3"/><path d="M12 19q3 0 5-3"/>',
 'thermometer':'<path d="M9 14V5a3 3 0 0 1 6 0v9a5 5 0 1 1-6 0ZM12 8v10m5-12h3m-3 4h2"/>',
 'optics':'<path d="M12 3q8 9 0 18-8-9 0-18ZM2 6h7m6 3 7 3M2 18h7m6-3 7-3M2 12h20"/>',
 'magnet':'<path d="M4 3h5v10a3 3 0 0 0 6 0V3h5v10a8 8 0 0 1-16 0ZM4 7h5m6 0h5"/>',
 'atom':'<ellipse cx="12" cy="12" rx="10" ry="4"/><ellipse cx="12" cy="12" rx="10" ry="4" transform="rotate(60 12 12)"/><ellipse cx="12" cy="12" rx="10" ry="4" transform="rotate(120 12 12)"/><circle cx="12" cy="12" r="1.5"/>',
 'gate':'<path d="M7 4h5a8 8 0 0 1 0 16H7ZM2 8h5M2 16h5m13-4h3"/>',
 'binary':'<rect x="5" y="5" width="14" height="14" rx="2"/><path d="M8 2v3m8-3v3M8 19v3m8-3v3M2 8h3m-3 8h3m14-8h3m-3 8h3M9 9v6m4-6h3v6h-3z"/>',
 'graph':'<path d="m5 5 14 2-8 12-6-14 6 14"/><circle cx="5" cy="5" r="2"/><circle cx="19" cy="7" r="2"/><circle cx="11" cy="19" r="2"/>',
 'numeric':'<path d="M3 20h18M5 17l4-5 5-3 5-4"/><circle cx="5" cy="17" r="1.5"/><circle cx="9" cy="12" r="1.5"/><circle cx="14" cy="9" r="1.5"/><circle cx="19" cy="5" r="1.5"/>',
 'circuit':'<path d="M2 12h4l2-4 3 8 3-8 2 4h6M6 3h12M6 21h12"/>',
 'signal':'<path d="M2 13h4l2-9 4 17 3-13 2 5h5"/>',
 'robot':'<path d="M5 21h14M8 21v-4l5-4-5-6M13 13l5-6m-2-3 4 5"/><circle cx="8" cy="7" r="3"/><circle cx="13" cy="13" r="2"/>',
 'network':'<rect x="9" y="2" width="6" height="5" rx="1"/><rect x="2" y="17" width="6" height="5" rx="1"/><rect x="16" y="17" width="6" height="5" rx="1"/><path d="M12 7v6M5 17v-4h14v4"/>',
 'algorithm':'<rect x="8" y="2" width="8" height="5" rx="1"/><path d="M12 7v4m-6 5-4-4 4-4 4 4-4 4Zm12 0-4-4 4-4 4 4-4 4ZM6 16v5h12v-5"/>',
 'cpu':'<rect x="5" y="5" width="14" height="14" rx="2"/><rect x="9" y="9" width="6" height="6"/><path d="M8 2v3m4-3v3m4-3v3M8 19v3m4-3v3m4-3v3M2 8h3m-3 4h3m-3 4h3m14-8h3m-3 4h3m-3 4h3"/>',
 'database':'<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14c0 4 18 4 18 0V5M3 12c0 4 18 4 18 0"/>',
 'shield':'<path d="m12 2 9 4v6c0 6-9 10-9 10S3 18 3 12V6z"/><path d="M9 11V9a3 3 0 0 1 6 0v2M8 11h8v6H8z"/>',
 'statistics':'<path d="M3 20h18M5 16v-4h3v4m3 0V8h3v8m3 0V4h3v12M4 6l4 3 6-6"/>',
 'target':'<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/><path d="m12 12 8-8"/>',
 'learning':'<path d="M12 4v6M5 18v-5h14v5M12 13v5"/><circle cx="12" cy="4" r="2"/><circle cx="5" cy="20" r="2"/><circle cx="12" cy="20" r="2"/><circle cx="19" cy="20" r="2"/>',
 'neural':'<path d="m5 5 14 3M5 5l14 13M5 12l14-4M5 12l14 6M5 19 19 8M5 19l14-1"/><circle cx="5" cy="5" r="2"/><circle cx="5" cy="12" r="2"/><circle cx="5" cy="19" r="2"/><circle cx="19" cy="8" r="2"/><circle cx="19" cy="18" r="2"/>',
 'qubit':'<circle cx="12" cy="12" r="9"/><ellipse cx="12" cy="12" rx="9" ry="3"/><path d="M12 3v18m0-9 6-6M2 12h20"/>',
 'dna':'<path d="M6 2c0 8 12 12 12 20M18 2C18 10 6 14 6 22M7 5h10M8 9h8m-8 6h8M7 19h10"/>',
 'vision':'<path d="M2 12s4-8 10-8 10 8 10 8-4 8-10 8S2 12 2 12Z"/><circle cx="12" cy="12" r="4"/>',
 'code':'<path d="m8 6-6 6 6 6m8-12 6 6-6 6M14 3l-4 18"/>',
 'os':'<rect x="2" y="3" width="20" height="15" rx="2"/><path d="M2 7h20M8 22h8m-4-4v4M5 5h.1m3 0h.1M6 11l3 2-3 2m6 0h5"/>',
 'web':'<circle cx="12" cy="12" r="10"/><ellipse cx="12" cy="12" rx="4" ry="10"/><path d="M2 12h20M4 6h16M4 18h16"/>',
 'servers':'<rect x="2" y="3" width="8" height="6" rx="1"/><rect x="14" y="3" width="8" height="6" rx="1"/><rect x="8" y="16" width="8" height="6" rx="1"/><path d="M6 9v3h12V9m-6 3v4M5 6h2m10 0h2m-8 13h2"/>',
}

def svg_source(name,color='#237b85'):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">{PATHS[name]}</svg>'

@lru_cache(maxsize=256)
def icon(name,color='#237b85'):
    renderer=QSvgRenderer(QByteArray(svg_source(name,color).encode()))
    if not renderer.isValid():raise ValueError('Icona SVG non valida: '+name)
    pix=QPixmap(40,40);pix.fill(Qt.GlobalColor.transparent);painter=QPainter(pix);renderer.render(painter);painter.end();return QIcon(pix)

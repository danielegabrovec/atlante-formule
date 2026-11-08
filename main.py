"""Avvio desktop e protocollo dei processi di calcolo isolati."""
import sys

if __name__ == '__main__':
    # Gli EXE windowed non hanno console: conserva diagnosi e traceback locali.
    if getattr(sys,'frozen',False) and sys.stderr is None:
        from atlante.paths import user_dir
        log=open(user_dir()/'avvio.log','a',encoding='utf-8',buffering=1)
        sys.stderr=log
        if sys.stdout is None:sys.stdout=log
    if '--worker' in sys.argv:
        from atlante.engine import worker_main
        worker_main()
    else:
        from atlante.ui import run
        run()

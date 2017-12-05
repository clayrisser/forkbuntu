from cement.core.foundation import CementApp
from cement.utils.misc import init_defaults
from config import NAME, BANNER
from pydash import _
from controllers import (
    BuildController,
    BaseController
)
import traceback

defaults = init_defaults(NAME, 'log.logging')
defaults['log.logging']['level'] = 'WARNING'

class App(CementApp):
    class Meta:
        label = NAME
        base_controller = BaseController
        extensions = ['colorlog']
        log_handler = 'colorlog'
        config_defaults=defaults
        handlers = [
            BuildController
        ]

def create_app():
    with App() as app:
        return app


def main():
    app = create_app()
    print(BANNER)
    try:
        app.run()
    except BaseException as err:
        if not hasattr(err, 'known') or not err.known:
            return handle_error(app, err)
        if not hasattr(err, 'level'):
            return app.log.error(err.message)
        if err.level == 'warning':
            return app.log.warning(err.message)
        return handle_error(app, err)

def handle_error(app, err):
    debug = False
    if app.config.get('log.logging', 'level') == 'DEBUG':
        debug = True
    if _.includes(app.config.keys('forkbuntu'), 'debug') and app.config.get(NAME, 'debug'):
        debug = True
    if debug:
        traceback.print_exc()
    return app.log.error(err.message)

if __name__ == '__main__':
    main()

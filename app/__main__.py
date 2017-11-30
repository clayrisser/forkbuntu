from cement.core.foundation import CementApp
from config import NAME, BANNER
from controllers import (
    BuildController,
    BaseController
)

class App(CementApp):
    class Meta:
        label = NAME
        base_controller = BaseController
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
    except BaseException as e:
        if not hasattr(e, 'known') or not e.known:
            raise e
        if not hasattr(e, 'level'):
            return app.log.error(e.message + '\n')
        if e.level == 'warning':
            return app.log.warning(e.message + '\n')
        return app.log.error(e.message + '\n')

if __name__ == '__main__':
    main()

import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from forkbuntu import App
from forkbuntu import get_steps

def main():
    with App() as app:
        app.steps = get_steps(app)
        app.run()

if __name__ == '__main__':
    main()

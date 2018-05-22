from cfoundation import Service
import os

class GPG(Service):
    def setup(self):
        os.system('gpgconf --kill gpg-agent')
        os.system('gpg-agent --daemon --keep-tty --pinentry-program=$(which pinentry-curses)')

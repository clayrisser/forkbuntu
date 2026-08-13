from __future__ import annotations

from typing import TYPE_CHECKING

from munch import Munch

from .cache import Cache
from .clean import Clean
from .configure import Configure
from .extras import Extras
from .filesystem import Filesystem
from .gpg import GPG
from .initrd import Initrd
from .iso import Iso
from .setup import Setup
from .util import Util

if TYPE_CHECKING:
    from ..app import App


def create_services(app: App) -> Munch:
    return Munch(
        cache=Cache(app),
        clean=Clean(app),
        configure=Configure(app),
        extras=Extras(app),
        filesystem=Filesystem(app),
        gpg=GPG(app),
        initrd=Initrd(app),
        iso=Iso(app),
        setup=Setup(app),
        util=Util(app),
    )

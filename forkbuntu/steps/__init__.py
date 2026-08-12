from __future__ import annotations

from typing import TYPE_CHECKING

from munch import Munch

from .build_keyring import BuildKeyring
from .clean import Clean
from .configure_filesystem import ConfigureFilesystem
from .create_extras import CreateExtras
from .initialize import Initialize
from .load_config import LoadConfig
from .merge_filesystem import MergeFilesystem
from .merge_initrd import MergeInitrd
from .merge_iso import MergeIso
from .pack_filesystem import PackFilesystem
from .pack_initrd import PackInitrd
from .pack_iso import PackIso
from .sign_iso import SignIso
from .unpack_filesystem import UnpackFilesystem
from .unpack_initrd import UnpackInitrd
from .unpack_iso import UnpackIso

if TYPE_CHECKING:
    from ..app import App

step_classes = {
    "build_keyring": BuildKeyring,
    "clean": Clean,
    "configure_filesystem": ConfigureFilesystem,
    "create_extras": CreateExtras,
    "initialize": Initialize,
    "load_config": LoadConfig,
    "merge_filesystem": MergeFilesystem,
    "merge_initrd": MergeInitrd,
    "merge_iso": MergeIso,
    "pack_filesystem": PackFilesystem,
    "pack_initrd": PackInitrd,
    "pack_iso": PackIso,
    "sign_iso": SignIso,
    "unpack_filesystem": UnpackFilesystem,
    "unpack_initrd": UnpackInitrd,
    "unpack_iso": UnpackIso,
}


def create_steps(app: App) -> Munch:
    return Munch(
        {name: step_class(name, app) for name, step_class in step_classes.items()}
    )

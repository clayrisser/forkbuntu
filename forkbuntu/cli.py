from __future__ import annotations

import sys
from argparse import ArgumentParser, Namespace

from halo import Halo

from .app import App
from .config import ConfigError


def parse_args(argv: list[str] | None = None) -> Namespace:
    argv = list(sys.argv[1:] if argv is None else argv)
    command = "build"
    if argv and argv[0] == "clean":
        command = "clean"
        argv = argv[1:]
    parser = ArgumentParser(
        prog="forkbuntu",
        description="Easily create your own Ubuntu distribution and install CD",
    )
    parser.add_argument(
        "--source",
        "--src",
        "-s",
        action="store",
        dest="src",
        help="source path",
        required=False,
    )
    parser.add_argument(
        "--reset",
        "-r",
        action="store_true",
        dest="reset",
        help="reset cache",
        required=False,
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        dest="debug",
        help="enable debug output",
        required=False,
    )
    parser.add_argument(
        "output",
        action="store",
        help="built iso output path",
        nargs="*",
    )
    pargs = parser.parse_args(argv)
    pargs.command = command
    return pargs


def main(argv: list[str] | None = None) -> int:
    pargs = parse_args(argv)
    try:
        app = App(pargs)
    except ConfigError as err:
        Halo(text=str(err)).fail()
        return 1
    if pargs.command == "clean":
        return app.clean()
    return app.build()


if __name__ == "__main__":
    sys.exit(main())

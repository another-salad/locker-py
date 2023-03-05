"""Encrypt and Decrypt"""

from argparse import ArgumentParser
from pathlib import Path
from getpass import getpass
from src.locker.common.crpyto import encryptor


class MainArgs(ArgumentParser):
    """Arg parser"""

    _desc = "Args for Encrypting/Decrypting"

    def __init__(self, description=_desc):
        super().__init__(description=description)
        self.add_argument("--decrypt", dest="decrypt", action="store_true")
        self.add_argument("--source", dest="source", type=str)
        self.add_argument("--dest", dest="dest", type=str)


class PathSadness(Exception):
    """Raised when a path doesn't exist"""


def _path_checker(path_to_check: Path):
    """Validates the input path"""
    if not path_to_check.exists():
        raise PathSadness(f"{path_to_check} isn't a valid path.")


def do_action(decrypt: bool, source: str, dest: str) -> str | None:
    source_path = Path(source)
    _path_checker(source_path)
    key = getpass("Please enter your key: ")
    if not decrypt:
        return encryptor(key, source_path, Path(dest))


if __name__ == "__main__":
    """lets parse some args"""
    args, _ = MainArgs().parse_known_args()
    do_action(args.decrypt, args.source, args.dest)

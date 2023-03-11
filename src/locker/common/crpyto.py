"""A thin wrapper around cryptography"""

from typing import Union  # py3.9 support
from pathlib import Path
from datetime import datetime
from typing import Callable
import re

from cryptography import fernet


def gen_key() -> bytes:
    """Spits out a key generated by fernet.Fernet.generate_key()"""
    return fernet.Fernet.generate_key()


def _mkdir_enc(key: bytes, parent: Path, nested_dir: Path) -> Path:
    """Makes a directory in the source, encrypts it's name"""
    dir = Path(parent, fernet.Fernet(key).encrypt(str(nested_dir).encode()).decode())
    dir.mkdir(parents=True, exist_ok=True)
    return dir


def _mkdir_dec(key: bytes, parent: Path, nested_dir: Path) -> Path:
    """Makes a directory in the source, decrypts it's name"""
    dir = Path(parent, fernet.Fernet(key).decrypt(str(nested_dir)).decode())
    dir.mkdir(parents=True, exist_ok=True)
    return dir


def _write_file_enc(key: bytes, source_file: Path, dest_dir: Path):
    """Reads data from source file, encrypts it via key and writes it to target."""
    enc_data = fernet.Fernet(key).encrypt(source_file.read_bytes())
    enc_file = Path(dest_dir, fernet.Fernet(key).encrypt(source_file.name.encode()).decode())
    enc_file.write_bytes(enc_data)


def _write_file_dec(key: bytes, source_file: Path, dest_dir: Path):
    """Reads data from source file, decrypts it via key and writes it to target."""
    enc_data = fernet.Fernet(key).decrypt(source_file.read_bytes())
    enc_file = Path(dest_dir, fernet.Fernet(key).decrypt(source_file.name.encode()).decode())
    enc_file.write_bytes(enc_data)


def crypto_operation(key: str, source: Path, dest: Union[Path, str, None], crypto_file_fnc: Callable, crypto_dir_fnc: Callable) -> int:
    """Encrypts/Decrypts a file/folder with the provided key"""
    # Check if the source directory is valid (ie a file, folder)
    if not any([source.is_dir(), source.is_file()]):
        print(f"Source: '{source}' is neither a file or folder, exiting.")
        return 1

    if dest is None:
        dest = Path.cwd()

    # To avoid any potentially horrible consequences, lets make an output folder in the parent
    # output directory. More Path fun....
    actual_output_root_dir = Path(Path(dest).absolute(), datetime.strftime(datetime.now(), "%Y-%m-%d_%H.%M.%S___r"))
    print(f"Creating parent output directory: {actual_output_root_dir}")
    actual_output_root_dir.absolute().mkdir()

    try:
        key = key.encode()  # Key must be Bytes for fernet
        if source.is_dir():
            for file_path in source.glob("**/*"):
                if file_path.is_file():
                    # Ignore our own 'root' (relative root, if thats a term...) directory that is created during encryption
                    relative_dir = re.sub(r"\d{4}-\d{2}-\d{2}_\d{2}.\d{2}.\d{2}___r", "", str(file_path.relative_to(source).parent))
                    dir = crypto_dir_fnc(key, actual_output_root_dir, relative_dir)
                    crypto_file_fnc(key, file_path, dir)
        elif source.is_file():
            crypto_file_fnc(key, source, actual_output_root_dir)
    except Exception as exc:
        print(f"Error returned: {repr(exc)}")
        if actual_output_root_dir.exists() and not any(actual_output_root_dir.iterdir()):
            print(f"Attempting to remove unused output DIR: {actual_output_root_dir}")
            try:
                actual_output_root_dir.rmdir()  # attempt some form of cleanup
            except:  # Oh Python
                print(f"Failed to remove {actual_output_root_dir}")

        print("Failure.")
        return 1

    print(f"files in output dir ({actual_output_root_dir}):")
    for out_file in actual_output_root_dir.iterdir():
        if out_file.is_file():
            print(out_file)
    return 0


def encryptor(key: str, source: Path, dest: Union[Path, str, None]) -> int:
    """Encrypts files in source directory"""
    return crypto_operation(key, source, dest, _write_file_enc, _mkdir_enc)


def decryptor(key: str, source: Path, dest: Union[Path, str, None]) -> int:
    """Decrypts files in source directory"""
    print(key)
    return crypto_operation(key, source, dest, _write_file_dec, _mkdir_dec)

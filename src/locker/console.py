"""Console scripts"""

from .common.crpyto import gen_key


def generate() -> str:
    """Outputs a generated key, keep this secret"""
    return gen_key().decode()

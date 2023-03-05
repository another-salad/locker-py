"""Tests the basic crypto operations"""

from contextlib import contextmanager
from unittest import TestCase, main
from pathlib import Path
from datetime import datetime
import logging

# Path hacks because Python
import os
import sys

sys.path.append(os.path.join(str(Path(__file__).parent.parent), "src"))

from locker.common.crpyto import encryptor, decryptor


class CryptoTestCase(TestCase):

    test_key = "t6foLpDJNBLlZDlwDD9aRmglEPtj3kjqHixmRuwo6gU="
    in_dir = Path(Path(__file__).parent.resolve(), "test_data")
    out_dir = Path(Path(__file__).parent.resolve(), "output")

    @contextmanager
    def _wrapper(self, fname):
        test_sub_dir = Path(self.out_dir.resolve(), f'test-{fname}')
        logging.info("Making DIR '%s' for test case.", test_sub_dir.absolute())
        test_sub_dir.mkdir()
        yield test_sub_dir

    def test_encrypt_content(self):
        with self._wrapper(f'test_encrypt_content.{datetime.strftime(datetime.now(), "%H.%M.%S")}') as test_out_dir:
            res = encryptor(self.test_key, self.in_dir, test_out_dir)

        self.assertEqual(res, 0, "Return code should be 0")
        out_files = list(test_out_dir.glob("**/*"))
        self.assertEqual(len(out_files), 2, "Test DIR should contain a datetime folder and an encrypted file")
        self.assertNotEqual(out_files[1].name, "test.txt")
        self.assertNotEqual(out_files[1].read_text("UTF-8"), "super secret data!", "Test file data should be encrypted")

    def test_decrypt_content(self):
        # Create the DIR and encrypted content
        with self._wrapper(f'test_decrypt_content_ENC.{datetime.strftime(datetime.now(), "%H.%M.%S")}') as test_enc_dir:
            encryptor(self.test_key, self.in_dir, test_enc_dir)

        # Create the DIR for the decrypted content
        with self._wrapper(f'test_encrypt_content_DEC.{datetime.strftime(datetime.now(), "%H.%M.%S")}') as test_dec_dir:
            res = decryptor(self.test_key, test_enc_dir, test_dec_dir)

        self.assertEqual(res, 0, "Return code should be 0")
        out_files = list(test_dec_dir.glob("**/*"))
        self.assertEqual(len(out_files), 2, "Test DIR should contain a datetime folder and an decrypted file")
        self.assertEqual(out_files[1].name, "test.txt")
        self.assertEqual(out_files[1].read_text("UTF-8"), "super secret data!", "Test file data should be decrypted")


if __name__ == "__main__":
    main()
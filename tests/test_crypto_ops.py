"""Tests the basic crypto operations"""

from contextlib import contextmanager
from unittest import TestCase, main
from pathlib import Path
from datetime import datetime
import logging
import re

# Path hacks because Python
import os
import sys

sys.path.append(os.path.join(str(Path(__file__).parent.parent), "src"))

from locker.common.crpyto import encryptor, decryptor


class CryptoTestCase(TestCase):

    test_key = "t6foLpDJNBLlZDlwDD9aRmglEPtj3kjqHixmRuwo6gU="
    root_in_dir = Path(Path(__file__).parent.resolve(), "test_data")
    single_file_dir = Path(root_in_dir, "single_file")
    multi_dir = Path(root_in_dir, "multi_dir")
    out_dir = Path(Path(__file__).parent.resolve(), "output")
    parent_dt_dir = r"\d{4}-\d{2}-\d{2}_\d{2}.\d{2}.\d{2}___r"

    @contextmanager
    def _wrapper(self, fname):
        test_sub_dir = Path(self.out_dir.resolve(), f'test-{fname}')
        logging.info("Making DIR '%s' for test case.", test_sub_dir.absolute())
        test_sub_dir.mkdir()
        yield test_sub_dir

    def test_encrypt_content_single_file(self):
        with self._wrapper(f'test_encrypt_content_single_file.{datetime.strftime(datetime.now(), "%H.%M.%S")}') as test_out_dir:
            res = encryptor(self.test_key, self.single_file_dir, test_out_dir)

        self.assertEqual(res, 0, "Return code should be 0")
        out_files = list(test_out_dir.glob("**/*"))
        self.assertEqual(len(out_files), 3)
        self.assertRegex(
            out_files[0].parts[-1], self.parent_dt_dir, "Expected a timestamped 'root' DIR to be created"
        )
        self.assertNotEqual(out_files[2].name, "test.txt")
        self.assertNotEqual(out_files[2].read_text("UTF-8"), "super secret data!", "Test file data should be encrypted")

    def test_decrypt_content_single_file(self):
        # Create the DIR and encrypted content
        with self._wrapper(f'test_decrypt_content_ENC.{datetime.strftime(datetime.now(), "%H.%M.%S")}') as test_enc_dir:
            encryptor(self.test_key, self.single_file_dir, test_enc_dir)

        # Create the DIR for the decrypted content
        with self._wrapper(f'test_decrypt_content_DEC.{datetime.strftime(datetime.now(), "%H.%M.%S")}') as test_dec_dir:
            res = decryptor(self.test_key, test_enc_dir, test_dec_dir)

        self.assertEqual(res, 0, "Return code should be 0")
        out_files = list(test_dec_dir.glob("**/*"))
        self.assertEqual(len(out_files), 2)
        self.assertEqual(out_files[1].name, "test.txt")
        self.assertEqual(out_files[1].read_text("UTF-8"), "super secret data!", "Test file data should be decrypted")

    def test_encrypt_content_multi_dir(self):
        with self._wrapper(f'test_encrypt_content_multi_dir.{datetime.strftime(datetime.now(), "%H.%M.%S")}') as test_out_dir:
            res = encryptor(self.test_key, self.multi_dir, test_out_dir)

        self.assertEqual(res, 0, "Return code should be 0")
        out_files = list(test_out_dir.glob("**/*"))
        self.assertEqual(len(out_files), 7)
        self.assertRegex(
            out_files[0].parts[-1], self.parent_dt_dir, "Expected a timestamped 'root' DIR to be created"
        )
        for f_name in ["even_more_inner", "inner_file", "outer_file"]:
            for enc_f_path in out_files:
                self.assertNotIn(f_name, str(enc_f_path), "file names should be encrypted")
                if enc_f_path.is_file():
                    self.assertNotIn("secret", enc_f_path.read_text("UTF-8").lower(), "file contents should be encrypted")


if __name__ == "__main__":
    main()
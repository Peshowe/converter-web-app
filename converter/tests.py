from django.test import TestCase
from converter.converter import Converter
import os
from pathlib import Path

FILE_DIR = os.path.dirname(os.path.realpath(__file__))
STATIC_DIR = os.path.join(FILE_DIR, "static/converter/test_files")
STATIC_DIR = Path(STATIC_DIR)

# Create your tests here.
class ConverterTestCase(TestCase):
    def setUp(self):
        self.converter = Converter()

    def _test(self, input_file, expected_output_file):
        with open(Path(f"{STATIC_DIR}/{input_file}"), encoding="utf-8") as f:
            input_text = f.read()

        with open(Path(f"{STATIC_DIR}/{expected_output_file}"), encoding="utf-8") as f:
            expected_text = f.read()

        converted_text = self.converter.convertText(input_text)

        self.assertEqual(converted_text, expected_text)

    # def test_text1(self):
    #     self._test("text1.txt", "conv1.txt")

    def test_text2(self):
        self._test("text2.txt", "conv2.txt")

    def test_words1(self):
        self._test("owords1.txt", "cwords1.txt")

    def test_words2(self):
        self._test("owords2.txt", "cwords2.txt")

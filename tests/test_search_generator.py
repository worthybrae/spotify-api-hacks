# tests/test_search_generator.py
import pytest
from services.search_generator import SearchStringGenerator

def test_char_increment():
    generator = SearchStringGenerator()
    assert generator.char_increment('a') == 'b'
    assert generator.char_increment('z') == '0'
    assert generator.char_increment('9') == 'aa'
    assert generator.char_increment('az') == 'a0'
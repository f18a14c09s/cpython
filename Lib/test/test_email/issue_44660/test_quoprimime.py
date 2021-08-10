import quopri
from email import quoprimime

import pytest


@pytest.mark.parametrize(
    'input_text,expected_output_text',
    [
        ('aaa', 'aaa'),
        (
                'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
                'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa=\r\naaaaa',
        ),
        (
                '                                                                                ',
                '                                                                           =\r\n     =\r\n',
        ),
        (
                'ⒶⒶⒶⒶⒶⒶⒶⒶⒶ',
                '=E2=92=B6=E2=92=B6=E2=92=B6=E2=92=B6=E2=92=B6=E2=92=B6=E2=92=B6=E2=92=B6=E2=\r\n=92=B6',
        ),
        (
                'a\r\nb',
                'a\r\nb',
        ),
        (
                'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\r\nbbbbb',
                'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\r\nbbbbb',
        ),
    ]
)
def test_quoprimime_encode(input_text: str, expected_output_text: str):
    input_bytes = input_text.encode('utf-8')
    assert quopri.decodestring(expected_output_text) == input_bytes
    actual_output_bytes = quoprimime.encode(
        input_bytes,
        maxlinelen=76,
        eol=b'\r\n'
    )
    assert isinstance(actual_output_bytes, bytes)
    actual_output_str = actual_output_bytes.decode('ascii')
    assert actual_output_str == expected_output_text

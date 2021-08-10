import email
import email.policy
from email.message import EmailMessage, Message
from email.parser import BytesFeedParser, BytesParser, BytesHeaderParser, \
    FeedParser, HeaderParser, Parser
from functools import partial
from io import StringIO
from test.test_email import TestEmailBase

import pytest


class TestParsers(TestEmailBase):
    def test_rfc6532_s3_5_quoted_printable_subpart(self):
        # Issue 44660: email.feedparser Module Lacks Support for Section 3.5 of
        #  RFC 6532: message/global Emails with non-identity
        #  Content-Transfer-Encodings.

        m = (
            # Top-level part header:
            'Content-Type: message/global\r\n'
            'Content-Transfer-Encoding: quoted-printable\r\n'
            '\r\n'
            # Top-level part body:
            # Quoted-printable-encoded subpart header:
            'Content-Type: text/plain; charset=3Dutf-8\r\n'
            'X-Really-Long-Header-Field-Name: This header field value is intentionally l=\r\n'
            'ong because soft-wrapped, quoted-printable header fields are an edge case.\r\n'
            'X-Header-Field-with-Unicode-Value: =E2=93=89=E2=93=97=E2=93=98=E2=93=A2 =\r\n'
            '=E2=93=98=E2=93=A2 =E2=93=8A=E2=93=9D=E2=93=98=E2=93=92=E2=93=9E=E2=93=\r\n'
            '=93=E2=93=94 =E2=93=A3=E2=93=94=E2=93=A7=E2=93=A3.\r\n'
            '\r\n'
            # Quoted-printable-encoded subpart body:
            'This is ASCII text.\r\n'
            '=E2=93=89=E2=93=97=E2=93=98=E2=93=A2 =E2=93=98=E2=93=A2 =E2=93=8A=E2=93=\r\n'
            '=9D=E2=93=98=E2=93=92=E2=93=9E=E2=93=93=E2=93=94 =E2=93=A3=E2=93=94=\r\n'
            '=E2=93=A7=E2=93=A3.\r\n'
        )
        actual_email_object = email.message_from_string(
            m,
            policy=email.policy.default
        )
        self.assertIsInstance(
            actual_email_object,
            email.message.EmailMessage,
            'Parsed value should be a message part object.'
        )

        self.assertEqual(
            dict(actual_email_object),
            {'Content-Transfer-Encoding': 'quoted-printable',
             'Content-Type': 'message/global'},
            'Top-level message headers incorrect.'
        )

        actual_payload = actual_email_object.get_payload()
        self.assertIsInstance(
            actual_payload,
            list,
            'Top-level message body should be a list.'
        )
        self.assertFalse(
            [subpart for subpart in actual_payload if
             not isinstance(subpart, Message)],
            'Top-level message body (a list) should contain only subpart object(s).'
        )
        self.assertEqual(
            len(actual_payload),
            1,
            'Top-level message should have a single subpart.'
        )
        actual_subpart: Message = actual_payload[0]

        self.assertEqual(
            actual_subpart.get_content_type(),
            'text/plain'
        )
        self.assertEqual(
            actual_subpart.get_content_charset(),
            'utf-8'
        )
        self.assertEqual(
            {key: list(actual_subpart.get_all(key))
             for key in actual_subpart.keys()
             if key not in ['Content-Type']},
            {'X-Header-Field-with-Unicode-Value': ['Ⓣⓗⓘⓢ ⓘⓢ Ⓤⓝⓘⓒⓞⓓⓔ ⓣⓔⓧⓣ.'],
             'X-Really-Long-Header-Field-Name': [
                 ('This header field value is intentionally '
                  'long because soft-wrapped, '
                  'quoted-printable header fields are an '
                  'edge case.')]},
            'Subpart headers incorrect.'
        )
        actual_subpart_payload = actual_subpart.get_payload()
        self.assertIsInstance(
            actual_subpart_payload,
            str,
            'Subpart body is of type "text/plain" so should be a string.'
        )
        self.assertEqual(
            actual_subpart_payload.encode('utf-8'),
            ('This is ASCII text.\r\n'
             'Ⓣⓗⓘⓢ ⓘⓢ Ⓤⓝⓘⓒⓞⓓⓔ ⓣⓔⓧⓣ.\r\n').encode('utf-8'),
            'Parsed subpart body text might be corrupt.'
        )

    def test_rfc6532_s3_5_base64_subpart(self):
        # Issue 44660: email.feedparser Module Lacks Support for Section 3.5 of
        #  RFC 6532: message/global Emails with non-identity
        #  Content-Transfer-Encodings.

        m = (
            # Top-level part header:
            'Content-Type: message/global\r\n'
            'Content-Transfer-Encoding: base64\r\n'
            '\r\n'
            # Top-level part body:
            # Base-64-encoded subpart (header and body):
            'Q29udGVudC1UeXBlOiB0ZXh0L3BsYWluDQpYLUhlYWRlci1GaWVsZC13aXRoLVVuaWNvZGUtVmFs\r\n'
            'dWU6IOKTieKTl+KTmOKToiDik5jik6Ig4pOK4pOd4pOY4pOS4pOe4pOT4pOUIOKTo+KTlOKTp+KT\r\n'
            'oy4NCg0KVGhpcyBpcyBBU0NJSSB0ZXh0Lg==\r\n'
        )
        actual_email_object = email.message_from_string(
            m,
            policy=email.policy.default
        )
        self.assertIsInstance(
            actual_email_object,
            email.message.EmailMessage,
            'Parsed value should be a message part object.'
        )

        self.assertEqual(
            dict(actual_email_object),
            {'Content-Transfer-Encoding': 'base64',
             'Content-Type': 'message/global'},
            'Top-level message headers incorrect.'
        )

        actual_payload = actual_email_object.get_payload()
        self.assertIsInstance(
            actual_payload,
            list,
            'Top-level message body should be a list.'
        )
        self.assertFalse(
            [subpart for subpart in actual_payload if
             not isinstance(subpart, Message)],
            'Top-level message body (a list) should contain only subpart object(s).'
        )
        self.assertEqual(
            len(actual_payload),
            1,
            'Top-level message should have a single subpart.'
        )
        actual_subpart: Message = actual_payload[0]

        self.assertEqual(
            actual_subpart.get_content_type(),
            'text/plain'
        )
        self.assertEqual(
            {key: list(actual_subpart.get_all(key))
             for key in actual_subpart.keys()
             if key not in ['Content-Type']},
            {'X-Header-Field-with-Unicode-Value': [
                'Ⓣⓗⓘⓢ ⓘⓢ Ⓤⓝⓘⓒⓞⓓⓔ ⓣⓔⓧⓣ.'
            ]},
            'Subpart headers incorrect.'
        )
        actual_subpart_payload = actual_subpart.get_payload()
        self.assertIsInstance(
            actual_subpart_payload,
            str,
            'Subpart body is of type "text/plain" so should be a string.'
        )
        self.assertEqual(
            actual_subpart_payload,
            'This is ASCII text.',
            'Parsed subpart body text might be corrupt.'
        )

    def test_parsing_of_quoted_printable_plaintext(self):
        m = (
            'Content-Type: text/plain; charset="utf-8"\r\n'
            'Content-Transfer-Encoding: quoted-printable\r\n'
            '\r\n'
            'abcd\r\n'
            '\r\n'
            '\r\n'
            '=\r\n'
            '\r\n'
            '\r\n'
            'efgh\r\n'
        )
        actual_email_object = email.message_from_string(
            m,
            policy=email.policy.default
        )
        assert isinstance(
            actual_email_object, email.message.EmailMessage
        ), 'Parsed value should be a message part object.'
        actual_content = actual_email_object.get_content()
        assert actual_content == ('abcd\r\n'
                                  '\r\n'
                                  '\r\n'
                                  '\r\n'
                                  '\r\n'
                                  'efgh\r\n')


# The following tests need to be added to TestParsers class or another class,
# once they are ready.


def test_utf8_unix_from():
    """
    Parsing of Unix-From address that contains UTF-8 characters;
     from UTF-8-encoded, top-level e-mail header.
    """

    expected_unixfrom = 'From ⒶⒷⒸ.①②③@mydomain.com'
    message_str = f'{expected_unixfrom}'

    actual_message: EmailMessage = email.message_from_string(
        message_str,
        policy=email.policy.default
    )

    assert isinstance(actual_message, EmailMessage)
    assert actual_message.get_unixfrom() == expected_unixfrom
    assert actual_message.get_unixfrom() != (
        expected_unixfrom.encode(
            'utf-8'
        ).decode(
            'ascii',
            'surrogateescape'
        )
    )


def utf8_header_field_value_parsers():
    def feed_parse(message_str: str):
        parser_obj = FeedParser(policy=email.policy.default)
        parser_obj.feed(message_str)
        return parser_obj.close()

    def bytes_feed_parse(message_str: str):
        parser_obj = BytesFeedParser(policy=email.policy.default)
        parser_obj.feed(message_str.encode('utf-8'))
        return parser_obj.close()

    parsers = [
        pytest.param(
            lambda message_str: email.message_from_bytes(
                message_str.encode('utf-8'),
                policy=email.policy.default
            ),
            id='email.message_from_bytes'
        ),
        pytest.param(
            partial(email.message_from_string, policy=email.policy.default),
            id='email.message_from_string'
        ),
        pytest.param(
            lambda message_str: email.message_from_file(
                StringIO(message_str),
                policy=email.policy.default
            ),
            id='email.message_from_file'
        ),
        pytest.param(
            feed_parse,
            id='FeedParser'
        ),
        pytest.param(
            bytes_feed_parse,
            id='BytesFeedParser'
        ),
        pytest.param(
            Parser(policy=email.policy.default).parsestr,
            id='Parser'
        ),
        pytest.param(
            lambda message_str: BytesParser(
                policy=email.policy.default
            ).parsebytes(message_str.encode('utf-8')),
            id='BytesParser'
        ),
        pytest.param(
            HeaderParser(policy=email.policy.default).parsestr,
            id='HeaderParser'
        ),
        pytest.param(
            lambda message_str: BytesHeaderParser(
                policy=email.policy.default
            ).parsebytes(message_str.encode('utf-8')),
            id='BytesHeaderParser'
        )
    ]

    return parsers


def utf8_header_field_params():
    return [
        ('Message-ID', '{}-UTF-8-Message-ID-{}'),
        ('Received', ('from x.y.test by example.net via TCP with ESMTP'
                      ' id ABC12345 for <{}.{}@mydomain.com>'
                      '; 21 Nov 1997 10:05:43 -0600')),
        ('From', '{}.{}@mydomain.com'),
        ('Sender', '{}.{}@mydomain.com'),
        ('Reply-To', '{}.{}@mydomain.com'),
        ('To', '{}.{}@mydomain.com'),
        ('Cc', '{}.{}@mydomain.com'),
        ('Bcc', '{}.{}@mydomain.com'),
        ('Subject', 'Hello, {} {}!'),
        ('Content-Description', 'Welcome message to person named {} {}.')
    ]


@pytest.mark.parametrize(
    'field_name,field_value_format_str',
    utf8_header_field_params()
)
@pytest.mark.parametrize(
    'message_from_string',
    utf8_header_field_value_parsers()
)
def test_utf8_header_field_values(
        field_name: str,
        field_value_format_str: str,
        message_from_string
):
    """
    Parsing of header fields whose values contain UTF-8 characters;
     from UTF-8-encoded, top-level e-mail headers.
    """

    utf8_str_1 = 'ⒶⒷⒸ'
    utf8_str_2 = '①②③'
    expected_value = field_value_format_str.format(utf8_str_1, utf8_str_2)
    message_str = (
        f'{field_name}: {expected_value}\r\n'
        '\r\n'
        'Hello, World!'
    )
    assert message_str.startswith(field_name)
    assert utf8_str_1 in message_str
    assert utf8_str_2 in message_str

    actual_message: EmailMessage = message_from_string(message_str)

    assert isinstance(actual_message, EmailMessage)
    actual_header_values = actual_message.get_all(field_name)
    assert actual_header_values == [expected_value]
    assert expected_value.encode('utf-8').decode(
        'ascii', 'surrogateescape'
    ) not in actual_header_values
    assert actual_message.get_content() == 'Hello, World!'

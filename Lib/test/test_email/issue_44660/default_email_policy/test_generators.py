import email
import email.policy
from email.message import EmailMessage

from unittest import TestCase


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


class TestGenerators(TestCase):
    def test_rfc6532_set_global_message_content(self):
        """
        Generation of RFC 822 string that has ASCII characters only, from message
         object whose content:
         - Is another message object with UTF-8 in header field value; and
         - Has explicit configuration of "global" message subtype and
          "quoted-printable" Content-Transfer-Encoding.
        """

        for field_name, field_value_format_str in utf8_header_field_params():
            with self.subTest(field_name):
                message = EmailMessage()
                self.assertIsInstance(
                    message.get_content_type(), str
                )
                orig_content_type = str(message.get_content_type())
                self.assertTrue(orig_content_type)
                global_message = EmailMessage()
                utf8_str_1 = 'ⒶⒷⒸ'
                utf8_str_2 = '①②③'
                field_value = field_value_format_str.format(utf8_str_1,
                                                            utf8_str_2)
                expected_encoded_field_value = (
                    field_value_format_str.format(
                        '=E2=92=B6=E2=92=B7=E2=92=B8',
                        '=E2=91=A0=E2=91=A1=E2=91=A2'
                    )
                )
                global_message[field_name] = field_value
                expected_cte = 'quoted-printable'
                message.set_content(
                    global_message,
                    subtype='global',
                    cte=expected_cte
                )

                actual_message_str = message.as_string(
                    policy=email.policy.default.clone(
                        utf8=False, cte_type='7bit', max_line_length=200,
                        linesep='\r\n'
                    )
                )
                self.assertEqual(
                    actual_message_str, (
                        'Content-Type: message/global\r\n'
                        'Content-Transfer-Encoding: quoted-printable\r\n'
                        'MIME-Version: 1.0\r\n'
                        '\r\n'
                        f'{field_name}: {expected_encoded_field_value}\r\n'
                        '\r\n'
                    )
                )

    def test_rfc6532_global_message_generation(self):
        """
        Generation of RFC 822 string that has UTF-8 characters, from message object
         that has header field value with UTF-8 characters.
        """

        for field_name, field_value_format_str in utf8_header_field_params():
            with self.subTest(field_name):
                global_message = EmailMessage()
                utf8_str_1 = 'ⒶⒷⒸ'
                utf8_str_2 = '①②③'
                expected_value = field_value_format_str.format(utf8_str_1,
                                                               utf8_str_2)
                global_message[field_name] = expected_value
                self.assertEqual(
                    global_message.as_string(
                        policy=email.policy.default.clone(
                            utf8=True, cte_type='8bit', max_line_length=200,
                            linesep='\r\n'
                        )
                    ),
                    f'{field_name}: {expected_value}\r\n\r\n',
                )
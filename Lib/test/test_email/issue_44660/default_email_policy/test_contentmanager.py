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


class TestContentManager(TestCase):
    def test_rfc6532_set_global_message_content(self):
        """
        Explicit configuration of "global" message subtype and "quoted-printable"
         Content-Transfer-Encoding when message with UTF-8 in header field value
         is set as the content of (i.e. nested in) a top-level message.
        """

        for field_name, field_value_format_str in utf8_header_field_params():
            with self.subTest(field_name):
                message = EmailMessage()
                self.assertIsInstance(message.get_content_type(), str)
                orig_content_type = str(message.get_content_type())
                self.assertTrue(orig_content_type)
                global_message = EmailMessage()
                utf8_str_1 = 'ⒶⒷⒸ'
                utf8_str_2 = '①②③'
                expected_value = field_value_format_str.format(utf8_str_1,
                                                               utf8_str_2)
                global_message[field_name] = expected_value
                expected_cte = 'quoted-printable'

                message.set_content(
                    global_message,
                    subtype='global',
                    cte=expected_cte
                )

                self.assertIsInstance(message.get_content_type(), str)
                self.assertTrue(message.get_content_type())
                self.assertNotEqual(message.get_content_type(),
                                    orig_content_type)
                # Make sure Content-Type is not set to "message/rfc822," as none of the RFCs
                # prior to 6532 support UTF-8:
                self.assertEqual(message.get_content_type(), 'message/global', (
                    'Wrong Content-Type set as described at top of RFC 6532, s. 3.7.'
                ))
                self.assertEqual(
                    message.get_all('Content-Transfer-Encoding'),
                    [expected_cte],
                    'Content-Transfer-Encoding not set to specified value.',
                )

from django.test import TestCase

from .patterns import Message, NotificationService, AuditSubscriber, build_channel_stack


class NotificationPatternTests(TestCase):
    def test_chain_falls_back_from_sms_to_email(self):
        message = Message(
            event_type="System Warning",
            body="The server needs attention.",
            recipient_email="student@example.com",
            recipient_phone="",
        )
        service = NotificationService()
        service.subscribe(AuditSubscriber())

        result = service.notify(
            message,
            [build_channel_stack("sms"), build_channel_stack("email")],
        )

        self.assertTrue(result.success)
        self.assertEqual(result.channel, "email")
        self.assertTrue(any("Observer" in item for item in message.trace))
        self.assertTrue(any("Decorator" in item for item in message.trace))
        self.assertTrue(any("Chain of Responsibility" in item for item in message.trace))

"""Design pattern implementation for the Group F notification demo.

The goal is not to fake a pattern for the presentation. The goal is to make the
code prove the design proposal: no giant switch statement, low coupling, and new
channels added through new classes instead of edits across the system.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Iterable, List, Optional

from django.conf import settings
from django.core.mail import send_mail


@dataclass()
class Message:
    """The thing being sent. This is separate from how it gets delivered."""

    event_type: str
    body: str
    recipient_email: str = ""
    recipient_phone: str = ""
    trace: List[str] = field(default_factory=list)


@dataclass()
class SendResult:
    """A clean result object keeps the frontend and database code simple."""

    channel: str
    success: bool
    detail: str


class NotificationChannel(ABC):
    """Shared channel interface.

    Adapter pattern target interface: every real or simulated vendor sender must
    expose send(message). The service never needs to know vendor-specific code.
    """

    name = "base"

    @abstractmethod
    def send(self, message: Message) -> SendResult:
        """Send a message through the concrete channel."""


class EmailAdapter(NotificationChannel):
    """Adapter around Django email.

    In class-demo mode, Django prints email to the backend terminal. For real
    email, change EMAIL_BACKEND and SMTP environment variables in .env.
    """

    name = "email"

    def send(self, message: Message) -> SendResult:
        if not message.recipient_email:
            return SendResult(self.name, False, "Email skipped because no email address was provided.")

        send_mail(
            subject=f"Group F Demo: {message.event_type}",
            message=message.body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[message.recipient_email],
            fail_silently=False,
        )
        return SendResult(self.name, True, f"Email delivered to {message.recipient_email}.")


class SMSAdapter(NotificationChannel):
    """Adapter placeholder for Twilio.

    The proposal names Twilio. The demo keeps this safe and key-free by simulating
    the vendor call while keeping the exact place where Twilio would be added.
    """

    name = "sms"

    def send(self, message: Message) -> SendResult:
        if not message.recipient_phone:
            return SendResult(self.name, False, "SMS skipped because no phone number was provided.")
        return SendResult(self.name, True, f"Twilio-style SMS simulated to {message.recipient_phone}.")


class PushAdapter(NotificationChannel):
    """Adapter placeholder for Firebase Cloud Messaging."""

    name = "push"

    def send(self, message: Message) -> SendResult:
        # In a real deployment, this class would call Firebase Cloud Messaging.
        # The adapter boundary means that change would not touch the service.
        return SendResult(self.name, True, "Firebase push notification simulated successfully.")


class InAppAdapter(NotificationChannel):
    """Simple in-app channel used by the demo dashboard."""

    name = "in-app"

    def send(self, message: Message) -> SendResult:
        return SendResult(self.name, True, "In-app notification saved for dashboard display.")


class ChannelDecorator(NotificationChannel):
    """Base decorator so cross-cutting logic does not get copy-pasted."""

    def __init__(self, wrapped: NotificationChannel) -> None:
        self.wrapped = wrapped
        self.name = wrapped.name


class LoggingDecorator(ChannelDecorator):
    """Decorator pattern: add logging/tracing without editing channel classes."""

    def send(self, message: Message) -> SendResult:
        message.trace.append(f"Decorator: logging started for {self.name}")
        result = self.wrapped.send(message)
        message.trace.append(f"Decorator: logging finished for {self.name} -> {result.success}")
        return result


class RetryDecorator(ChannelDecorator):
    """Decorator pattern: add retry without editing channel classes."""

    def __init__(self, wrapped: NotificationChannel, tries: int = 2) -> None:
        super().__init__(wrapped)
        self.tries = max(1, tries)

    def send(self, message: Message) -> SendResult:
        last_result: Optional[SendResult] = None
        for attempt in range(1, self.tries + 1):
            message.trace.append(f"Decorator: retry attempt {attempt} for {self.name}")
            last_result = self.wrapped.send(message)
            if last_result.success:
                return last_result
        return last_result or SendResult(self.name, False, "No send attempt was made.")


class ChannelChain:
    """Chain of Responsibility: try each channel until one succeeds."""

    def __init__(self, channels: Iterable[NotificationChannel]) -> None:
        self.channels = list(channels)

    def handle(self, message: Message) -> SendResult:
        for channel in self.channels:
            result = channel.send(message)
            message.trace.append(f"Chain of Responsibility: {channel.name} returned {result.success}")
            if result.success:
                return result
        return SendResult("none", False, "Every selected channel failed.")


class Subscriber(ABC):
    """Observer pattern subscriber interface."""

    @abstractmethod
    def update(self, message: Message) -> None:
        """React to the event before delivery starts."""


class AuditSubscriber(Subscriber):
    """Observer that proves subscribers can react without being hard-coded into channels."""

    def update(self, message: Message) -> None:
        message.trace.append(f"Observer: audit subscriber received {message.event_type}")


class NotificationService:
    """Coordinates notification sending while depending on abstractions only."""

    def __init__(self) -> None:
        self._subscribers: List[Subscriber] = []

    def subscribe(self, subscriber: Subscriber) -> None:
        self._subscribers.append(subscriber)

    def notify(self, message: Message, channels: Iterable[NotificationChannel]) -> SendResult:
        for subscriber in self._subscribers:
            subscriber.update(message)
        return ChannelChain(channels).handle(message)


CHANNEL_FACTORIES = {
    "push": PushAdapter,
    "sms": SMSAdapter,
    "email": EmailAdapter,
    "in-app": InAppAdapter,
}


def build_channel_stack(channel_name: str) -> NotificationChannel:
    """Build the adapter + decorator stack for one selected channel."""

    try:
        adapter = CHANNEL_FACTORIES[channel_name]()
    except KeyError as exc:
        raise ValueError(f"Unsupported channel: {channel_name}") from exc

    return LoggingDecorator(RetryDecorator(adapter, tries=2))

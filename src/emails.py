from dataclasses import dataclass
from enum import Enum

from kubernetes import client

from crd import CRD, CustomResourceStatus
from email_sender_configs import EmailSenderConfig


class EmailDeliveryStatus(Enum):
    """
    TODO: doc.
    """
    UNSENT = "UNSENT"
    FAILED = "FAILED"
    SENT = "SENT"


@dataclass
class EmailStatus(CustomResourceStatus):
    """
    TODO: doc.
    """
    delivery_status: EmailDeliveryStatus
    message_id: str

    @property
    def _serialized(self):
        """
        TODO: doc.
        """
        return {
            "deliveryStatus": self.delivery_status.value,
            "messageId": self.message_id
        }


class Email(CRD):
    """
    TODO: doc.
    # """
    sender_config_ref: EmailSenderConfig
    group: str = "stable.email-sender-operator.dev"
    version: str = "v1"
    plural: str = "emails"
    body: str
    recipient_email: str
    subject: str

    def __init__(self, namespace, name, sender, body, recipient_email, subject):
        """
        TODO: doc.
        """
        super().__init__(namespace, name)

        self.sender_config_ref = sender
        self.body = body
        self.recipient_email = recipient_email
        self.subject = subject
        self.status = self._status

        if not self.status:
            # NOTE: First time object is read from cluster.
            # NOTE: Assumes it has never been SENT.
            self.set_status(EmailStatus(
                delivery_status=EmailDeliveryStatus.UNSENT,
                message_id=self.uid
            ))

    def set_delivery_status(self, delivery_status: EmailDeliveryStatus):
        """
        TODO: doc.
        """
        self.set_status(EmailStatus(
            delivery_status=delivery_status,
            message_id=self.uid
        ))

    def send(self):
        """
        TODO: doc.
        """
        pass

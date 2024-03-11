from dataclasses import dataclass
from enum import Enum

from crd import CRD, CustomResourceStatus
from email_sender_configs import EmailSenderConfig


class EmailDeliveryStatus(Enum):
    """
    Enumerator representing all possible delivery statuses for
    an Email (below).
    """

    UNSENT = "UNSENT"
    FAILED = "FAILED"
    SENT = "SENT"


@dataclass
class EmailStatus(CustomResourceStatus):
    """
    Representation of an Email's object status.
    """

    delivery_status: EmailDeliveryStatus
    message_id: str

    @property
    def _serialized(self):
        """
        Builds/returns a serialized version of EmailStatus.

        Returns:
            dict: serialized EmailStatus.
        """
        return {
            "deliveryStatus": self.delivery_status.value,
            "messageId": self.message_id,
        }


class Email(CRD):
    """
    Representation of the namespaced Email Custom Resource.
    """

    sender_config_ref: EmailSenderConfig
    group: str = "stable.email-sender-operator.dev"
    version: str = "v1"
    plural: str = "emails"
    body: str
    recipient_email: str
    subject: str

    def __init__(self, namespace, name, sender, body, recipient_email, subject):
        """
        Constructor.

        Args:
            namespace (str): kubernetes namespace where EmailSenderConfig resides.
            name (str): EmailSenderConfig name.
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
            self.set_status(
                EmailStatus(
                    delivery_status=EmailDeliveryStatus.UNSENT, message_id=self.uid
                )
            )

    def set_delivery_status(self, delivery_status: EmailDeliveryStatus):
        """
        Sets Email's delivery status.

        Args:
            delivery_status: EmailDeliveryStatus to set Email status to.

        Note:
            Sets both instance and Email custom resource delivery status (via cluster
            API - i.e. CRD.set_status).
        """
        self.set_status(
            EmailStatus(delivery_status=delivery_status, message_id=self.uid)
        )

    def send(self):
        """
        Sends email via EmailSenderConfig reference at the sender_config_ref attribute.
        """
        self.sender_config_ref.send(
            self.body, self.recipient_email, self.subject, self.uid
        )

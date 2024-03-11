from base64 import b64decode
from dataclasses import dataclass

from kopf import PermanentError
from kubernetes import client
from mailersend import emails
import requests

from crd import CRD


class UnknownEmailSender(PermanentError):
    """
    Exception denoting that the EmailSenderConfig for which an event was handled is not
    known by this controller - i.e. will be ignored by it.

    Note:
        Extends kopf's PermanentError. Therefore is treated as a non-retriable exception
        by the handlers.
    """

    pass


class MailSendingFailure(PermanentError):
    """
    Exception denoting that a failure happened while trying to send an email via an
    EmailSenderConfig.

    Note:
        Extends kopf's PermanentError. Therefore is treated as a non-retriable exception
        by the handlers. We're assumind that the error is always on the client, not the
        server.
    """

    pass


class EmailSenderConfig(CRD):
    """
    Base class to be extended by specific implementations of mail sending services.
    Provides attributes and methods common in those entities.
    """

    api_token: str
    sender_email: str
    group: str = "stable.email-sender-operator.dev"
    version: str = "v1"
    plural: str = "emailsenderconfigs"

    def __init__(self, namespace, name):
        """
        Constructor.

        Args:
            namespace (str): kubernetes namespace where EmailSenderConfig resides.
            name (str): EmailSenderConfig name.
        """
        super().__init__(namespace, name)

        self.api_token = self._api_token
        self.sender_email = self._sender_email

    @property
    def _api_token(self):
        """
        Gets API token/key for the EmailSenderConfig from the cluster API (See note below).

        Returns:
            str: API token/key for the mail sending service represented by the instance.

        Note:
            Meant to be private (i.e. used within this class and its children only).

            API token/key is expected to exist at the apiToken attribute of a Secret
            with the same name and namespace of the EmailSenderConfig.
        """
        return b64decode(
            client.CoreV1Api(self.api)
            .read_namespaced_secret(self.name, self.namespace)
            .data.get("apiToken")
        ).decode("UTF-8")

    @property
    def _sender_email(self):
        """
        Gets sender email for the EmailSenderConfig from the cluster API.

        Returns:
            str: Sender email for the mail sending service represented by the instance.

        Note:
            Meant to be private (i.e. used within this class and its children only).
        """
        return self._resource.get("spec").get("senderEmail")

    def send(self, body, recipient, subject, uid):
        """
        Sends email.

        Args:
            body (str): Email contents/message.
            recipient (str): Email to.
            subject (str): Email subject.
            uid (str): EmailSenderConfig object uid - used for logging purposes only.
        """
        pass


class MailGun(EmailSenderConfig):
    """
    EmailSenderConfig implementation for MailGun service.

    See: https://www.mailgun.com.
    """

    @property
    def _domain(self):
        """
        Gets sender domain from sender email - needed to build MailGun's API URL (below).

        Returns:
            str: Sender's domain.

        Note:
            Meant to be private (i.e. used within this class only).
        """
        return self.sender_email.split("@", 1)[1]

    @property
    def _url(self):
        """
        Builds/returns MailGun's API URL.

        Returns:
            str: MailGun's API URL.

        Note:
            Meant to be private (i.e. used within this class only).
        """
        return f"https://api.mailgun.net/v3/{self._domain}/messages"

    def send(self, body, recipient, subject, uid):
        """
        Sends email via MailGun service.

        Args:
            body (str): Email contents/message.
            recipient (str): Email to.
            subject (str): Email subject.
            uid (str): EmailSenderConfig object uid - used for logging purposes only.

        Raises:
            MailSendingFailure: Email could not be sent. Treated as client error (see
                exception's def. above.
        """
        try:
            requests.post(
                self._url,
                auth=("api", self.api_token),
                data={
                    "from": self.sender_email,
                    "to": [recipient],
                    "subject": subject,
                    "text": body,
                },
            ).raise_for_status()
        except requests.exceptions.HTTPError as exc:
            raise MailSendingFailure(
                f"Failed to send email with id {uid} (reason: {exc})."
            )


class MailerSend(EmailSenderConfig):
    """
    EmailSenderConfig implementation for MailerSend service.

    See: https://www.mailersend.com.
    """

    @staticmethod
    def _success(result):
        """
        Determines if call to MailerSend's API was successul.

        Args:
            result (str): Response from MailerSend's SDK/API send method.

        Returns:
            bool: Indicator of success of email sending based on result.

        Note:
            Meant to be private (i.e. used within this class only).
        """
        try:
            int(result)
        except ValueError:
            return False
        else:
            return True

    def send(self, body, recipient, subject, uid):
        """
        Sends email via MailerSend service.

        Args:
            body (str): Email contents/message.
            recipient (str): Email to.
            subject (str): Email subject.
            uid (str): EmailSenderConfig object uid - used for logging purposes only.

        Raises:
            MailSendingFailure: Email could not be sent. Treated as client error (see
                exception's def. above.
        """
        mailer = emails.NewEmail(self.api_token)

        mail = {}

        mailer.set_mail_from({"email": self.sender_email}, mail)
        mailer.set_mail_to([{"email": recipient}], mail)
        mailer.set_subject(subject, mail)
        mailer.set_plaintext_content(body, mail)

        try:
            result = mailer.send(mail)
        except Exception as exc:
            raise MailSendingFailure(
                f"Failed to send email with id {uid} (reason: {exc})."
            )

        if not self._success(result):
            raise MailSendingFailure(
                f"Failed to send email with id {uid} (result: {result})."
            )


def create_email_sender_config(namespace, name):
    """
    Builds/returns appropriate instance of EmailSenderConfig.

    Args:
        namespace (str): kubernetes namespace where EmailSenderConfig resides.
        name (str): EmailSenderConfig name.

    Returns:
        EmailSenderConfig: child of EmailSenderConfig.

    Raises:
        UnknownEmailSender: name is from unknown mail sending service.
    """

    def _to_camel_case(name):
        """
        CamelCasesi (hyphenated) name.

        Args:
            name (str): string to be CamelCased.

        Returns:
            str: CamelCased string.
        """
        return "".join([token.capitalize() for token in name.split("-")])

    try:
        return globals()[_to_camel_case(name)](namespace, name)
    except KeyError:
        raise UnknownEmailSender(f"{name} is not a known email sender.")

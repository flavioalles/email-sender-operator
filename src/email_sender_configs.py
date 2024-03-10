from base64 import b64decode
from dataclasses import dataclass

from kubernetes import client
from mailersend import emails
import requests

from crd import CRD


class UnknownEmailSender(Exception):
    """
    TODO: doc.
    """
    pass


class MailSendingFailure(Exception):
    """
    TODO: doc.
    """
    pass


class EmailSenderConfig(CRD):
    """
    TODO: doc.
    """
    api_token: str
    sender_email: str
    group: str = "stable.email-sender-operator.dev"
    version: str = "v1"
    plural: str = "emailsenderconfigs"

    def __init__(self, namespace, name):
        """
        TODO: doc.
        """
        super().__init__(namespace, name)

        # NOTE: this could be better - does not have to live here.
        self.api_token = b64decode(client.CoreV1Api(self.api).read_namespaced_secret(
            f"{name}",
            namespace
        ).data.get("apiToken")).decode("UTF-8")
        self.sender_email = self._sender_email

    @property
    def _sender_email(self):
        """
        TODO: doc.
        """
        return self._resource.get("spec").get("senderEmail")

    def send(self, body, recipient, subject, uid):
        """
        TODO: doc.
        """
        pass

class MailGun(EmailSenderConfig):
    """
    TODO: doc.
    """
    @property
    def _domain(self):
        """
        TODO: doc.
        """
        # NOTE: this could be more elegant.
        return self.sender_email.split("@", 1)[1]

    @property
    def _url(self):
        """
        TODO: doc.
        """
        return f"https://api.mailgun.net/v3/{self._domain}/messages"

    def send(self, body, recipient, subject, uid):
        """
        TODO: doc.
        """
        try:
            requests.post(
                self._url,
                auth=("api", self.api_token),
                data={
                    "from": self.sender_email,
                    "to": [recipient],
                    "subject": subject,
                    "text": body
                }
            ).raise_for_status()
        except requests.exceptions.HTTPError as exc:
            raise MailSendingFailure(
                f"Failed to send email with id {uid} (reason: {exc})."
            )

class MailerSend(EmailSenderConfig):
    """
    TODO: doc.
    """
    @staticmethod
    def _success(result):
        """
        TODO: doc.
        """
        try:
            int(result)
        except ValueError:
            return False
        else:
            return True

    def send(self, body, recipient, subject, uid):
        """
        TODO: doc.
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
    TODO: doc.
    """
    def _to_camel_case(name):
        """
        TODO: doc.
        """
        return "".join(
            [token.capitalize() for token in name.split("-")]
        )

    try:
        return globals()[_to_camel_case(name)](namespace, name)
    except KeyError:
        raise UnknownEmailSender(f"{name} is not a known email sender.")

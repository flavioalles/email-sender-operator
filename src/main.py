import logging

import kopf

import emails as eml
import email_sender_configs as esc


@kopf.on.create("EmailSenderConfig")
@kopf.on.update("EmailSenderConfig")
def email_sender_config_handler(name, namespace, reason, **_):
    """
    TODO: doc.
    """
    base_log = f"(handler/EmailSenderConfig) ({namespace}/{name})"

    try:
        esc.create_email_sender_config(
            namespace, name
        )
    except esc.UnknownEmailSender as exc:
        logging.error(f"{base_log} {str(exc)}")
    else:
        logging.info(f"{base_log} Known sender {reason.upper()}D.")

@kopf.on.create("Email")
def email_handler(name, namespace, reason, spec, uid, **_):
    """
    TODO: doc.
    """
    def _email():
        """
        TODO: doc.
        """
        try:
            sender = esc.create_email_sender_config(
                namespace, spec.get("senderConfigRef")
            )
        except esc.UnknownEmailSender as exc:
            logging.error(f"{base_log} {str(exc)}")
            logging.warning(
                f"{base_log} will not manage Email with unknown sender config."
            )
            mail, sender = None, None
        else:
            logging.info(f"{base_log} EmailSenderConfig acquired.")

            mail = eml.Email(
                namespace,
                name,
                sender,
                spec.get("body"),
                spec.get("recipientEmail"),
                spec.get("subject")
            )

            logging.info(
                f"""{base_log} Email deliveryStatus set to
                {mail.status.delivery_status}."""
            )

        return mail, sender

    def _send(mail, sender):
        """
        TODO: doc.
        """
        try:
            sender.send(
                spec.get("body"),
                spec.get("recipientEmail"),
                spec.get("subject"),
                uid
            )
        except AttributeError:
            logging.warning(
                f"""{base_log} Sender unset. Nothing to do."""
            )
        except esc.MailSendingFailure as exc:
            logging.error(f"{base_log} {str(exc)}")
            mail.set_delivery_status(eml.EmailDeliveryStatus.FAILED)
            logging.warning(
                f"""{base_log} Email deliveryStatus set to
                {mail.status.delivery_status}."""
            )
        else:
            logging.info(f"{base_log} Sent successfully.")
            mail.set_delivery_status(eml.EmailDeliveryStatus.SENT)
            logging.info(
                f"""{base_log} Email deliveryStatus set to
                {mail.status.delivery_status}."""
            )

    base_log = f"(handler/Email) ({namespace}/{name}/{uid})"
    logging.info(f"{base_log} {reason.upper()}D.")

    _send(*_email())

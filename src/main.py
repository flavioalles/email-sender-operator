import kopf
import logging  # NOTE: fix ordering (black?)

@kopf.on.create("EmailSenderConfig")
def email_sender_config_handler(body, **kwargs):
    """
    TODO: doc.
    """
    logging.info("EmailSenderConfig created.")

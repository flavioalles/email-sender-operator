from dataclasses import dataclass
import logging

from kubernetes import client, config


@dataclass
class CustomResourceStatus:
    """
    TODO: doc.
    """

    @property
    def _serialized(self):
        """
        TODO: doc.
        """
        pass


class CRD:
    """
    TODO: doc.
    """

    api: client.ApiClient
    group: str
    version: str
    plural: str
    namespace: str
    name: str
    status: CustomResourceStatus
    uid: str

    def __init__(self, namespace, name):
        """
        TODO: doc.
        """
        self.api = self._api()
        self.namespace = namespace
        self.name = name
        self.uid = self._uid

    @staticmethod
    def _api():
        """
        TODO: doc.
        """
        try:
            config.load_kube_config()
        except config.config_exception.ConfigException:
            logging.debug(
                "ConfigException raised. Will silence it - assuming login via ServiceAccount."
            )
            config.load_incluster_config()

        return client.ApiClient()

    @property
    def _resource(self):
        """
        TODO: doc.
        """
        return client.CustomObjectsApi(self.api).get_namespaced_custom_object(
            self.group, self.version, self.namespace, self.plural, self.name
        )

    @property
    def _status(self):
        """
        TODO: doc.
        """
        return (
            client.CustomObjectsApi(self.api)
            .get_namespaced_custom_object(
                self.group, self.version, self.namespace, self.plural, self.name
            )
            .get("status")
        )

    def set_status(self, status: CustomResourceStatus):
        """
        TODO: doc.
        """
        self.status = status
        self._patch_resource_status(self.status)

    def _patch_resource_status(self, status: CustomResourceStatus):
        """
        TODO: doc.
        """
        client.CustomObjectsApi(self.api).patch_namespaced_custom_object(
            self.group,
            self.version,
            self.namespace,
            self.plural,
            self.name,
            {"status": self.status._serialized},
        )

    @property
    def _uid(self):
        """
        TODO: doc.
        """
        return self._resource.get("metadata").get("uid")

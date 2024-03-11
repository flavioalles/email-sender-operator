from dataclasses import dataclass
import logging

from kubernetes import client, config


@dataclass
class CustomResourceStatus:
    """
    Base class for extension by children to represent a custom object's status.

    Note:
        Type used in CRD's (below) status attribute.
    """

    @property
    def _serialized(self):
        """
        Should return a serialized version of status.

        Returns:
            dict: Namespaced Custom Resource status.
        """
        pass


class CRD:
    """
    Base class for extension by children representing some form of CRD.

    Note:
        Supports namespaced CustomResourceDefinitions only - i.e. no support for
        cluster-wide CRD's.
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
        (Base) Constructor.

        Args:
            namespace (str): kubernetes namespace where Custom Resource resides.
            name (str): Custom Resource name.
        """
        self.api = self._api()
        self.namespace = namespace
        self.name = name
        self.uid = self._uid

    @staticmethod
    def _api():
        """
        Sets up authentication configuration with cluster and build kubernetes API client.

        Returns:
            client.ApiClient: kubernetes API client.

        Note:
            Meant to be private (i.e. used within this class and its children only).
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
        Gets namespaced Custom Resource represented by CRD instance from cluster API.

        Returns:
            object: Namespaced Custom Object represented by class instance.

        Note:
            Meant to be private (i.e. used within this class and its children only).
        """
        return client.CustomObjectsApi(self.api).get_namespaced_custom_object(
            self.group, self.version, self.namespace, self.plural, self.name
        )

    @property
    def _status(self):
        """
        Gets status of namespaced Custom Resource represented by CRD instance from
        cluster API.

        Returns:
            dict: Namespaced Custom Object represented by class instance.

        Note:
            Meant to be private (i.e. used within this class and its children only).
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
        Sets status attribute on class instance and patches namespaced Custom Resource
        object's status via cluster API.

        Args:
            status (CustomResourceStatus): object containing new Custom Resource status.
        """
        self.status = status
        self._patch_resource_status(self.status)

    def _patch_resource_status(self, status: CustomResourceStatus):
        """
        Patches namespaced Custom Resource object's status via cluster API.

        Args:
            status (CustomResourceStatus): object containing new Custom Resource status.

        Note:
            Meant to be private (i.e. used within this class and its children only).
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
        Gets namespaced Custom Resource's object UID from cluster API.

        Returns:
            str: Namespaced Custom Resource's object UID.

        Note:
            Meant to be private (i.e. used within this class and its children only).
        """
        return self._resource.get("metadata").get("uid")

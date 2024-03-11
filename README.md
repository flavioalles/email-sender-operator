### `email-sender-operator`

A [`kubernetes` operator](https://kubernetes.io/docs/concepts/extend-kubernetes/operator/)
controlling/managing CRD's aimed at sending emails. The operator can use either [MailGun](https://www.mailgun.com/) or
[MailerSend](https://www.mailersend.com/) as it's email sending backend.

#### Installation

##### Requirements

- `make` required.
    - OBS: `make` is central to interacting with this project. It is the interface for most (if not
      all technologies used here - i.e. `docker`, `helm`, Python tools and [`kopf`](https://kopf.readthedocs.io/en/stable/))
- `kubernetes` cluster at version ~`1.28`.
    - Might work with different versions. Untested as of yet.
- [`envsubst`](https://linux.die.net/man/1/envsubst).

##### Operator

FYI: `make help` is your friend.

```shell
user at host in location
↪ make help
email-sender-operator
---------------------
Available targets are:

Operation:
         install-operator                Installs operator into cluster.
         uninstall-operator              Uninstalls operator from cluster.

Development & testing:

(...)

```

`make install-operator` will install the `email-sender-operator` into the `kubernetes` cluster's
`default` namespace. Conversely, `make uninstall-operator` will uninstall the operator.

```shell
user at host in location
↪ make install-operator
NAME: email-sender-operator
LAST DEPLOYED: Mon Mar 11 00:08:22 2024
NAMESPACE: default
STATUS: deployed
REVISION: 1
TEST SUITE: None
flavio at plainfield in ~/w/p/s/t/m/email-sender-operator
user at host in location
↪ make uninstall-operator
release "email-sender-operator" uninstalled
```

#### Developing

##### Requirements

- `python` requirement: ~`3.12`.
    - \+ `kopf`s [requirements](https://kopf.readthedocs.io/en/stable/walkthrough/prerequisites/).
- `kubernetes` cluster at version ~`1.28`.
    - Might work with different versions. Untested as of yet.

##### Image Building, Controller Development & Testing

Once again, `make help` is there for you.

```shell
user at host in location
↪ make help
email-sender-operator
---------------------
Available targets are:

Operation:

(...)

Development & testing:
         build-image                             Builds controller's Docker image.
         install-controller-with-dev             Installs all controller's Python project dependencies.
         install-controller                      Installs controller's Python project dependencies (excl. dev).
         run-controller                          Starts controller.
         create-examples                         Creates example objects (at examples/custom-resources).
         delete-examples                         Deletes example objects (at examples/custom-resources).
         check                                   Dry-run of black (on src/) reporting diff.
         format                                  Runs black (on src/).
```

Most importantly:
- `make create-examples` will create a few Custom Resources that can be used for
testing/validation.
    - Check their definitions at `examples/`.
    - Environment variables needed to execute target:
        - `MAIL_GUN_SENDER_EMAIL`
        - `MAIL_GUN_RECIPIENT_EMAIL`
        - `MAIL_GUN_API_TOKEN` (`base64`-encoded)
        - `MAILER_SEND_SENDER_EMAIL`
        - `MAILER_SEND_RECIPIENT_EMAIL`
        - `MAILER_SEND_API_TOKEN` (`base64`-encoded)
- `make delete-examples` will delete those Custom Resources from the cluster.

#### Caveats

- The Deployment` of the controller has been named `email-sender-operator` - instead of
    the required `email-operator`. Since this is the chosen name for the repository this
    seemed to make sense.
- There are no configurable elements in the Helm chart (located at `email-sender-operator/`.
    Installation occurs in the `default` namespace and the image used for the `Deployment`
    is set to [`flavioalles/email-sender-operator:latest`](https://hub.docker.com/repository/docker/flavioalles/email-sender-operator/general).
- Diverging from the requirements, for security's sake, the EmailSenderConfig CRD has no
    `apiToken` property. A `Secret` with the same name is expected to Mention use of Secret - and no apiToken on CRD.
- The `Email` Custom Resource object's UID was used as the status' `messageId`.

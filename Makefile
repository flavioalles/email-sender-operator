.PHONY: help
help:
	@echo "email-sender-operator"
	@echo "---------------------"
	@echo "Available targets are:"
	@echo
	@echo "Operation:"
	@echo "\t install-operator \t\t Installs operator."
	@echo "\t run-controller   \t\t Starts controller."
	@echo
	@echo "Development & testing:"
	@echo "\t install-controller-with-dev  \t\t Installs all controller's Python project dependencies."
	@echo "\t install-controller           \t\t Installs controller's Python project dependencies (excl. dev)."
	@echo "\t create-examples              \t\t Creates example objects (at examples/custom-resources)."
	@echo "\t delete-examples              \t\t Deletes example objects (at examples/custom-resources)."

.PHONY: poetry
poetry:
	# NOTE: Could be problematic if not run inside virtualenv.
	# NOTE: Consider creating one before using it.
	@pip install poetry==1.8.2

.PHONY: install-controller-with-dev
install-controller-with-dev: poetry
	@poetry install --with=dev

.PHONY: install-controller
install-controller: poetry
	@poetry install

.PHONY: create-crds
install-operator:
	# NOTE: assumes existence of namespace dev.
	@kubectl apply -f email-sender-operator/crd.email-sender-config.yaml
	@kubectl apply -f email-sender-operator/crd.email.yaml

.PHONY: run-controller
run-controller:
	@kopf run --all-namespaces src/main.py

.PHONY: create-examples
create-examples:
	# NOTE: assumes existence of namespace dev.
	# NOTE: assumes existence of CRD's (i.e. esc and eml).
	# TODO: check if api-token ENV's have been created.
	@envsubst \
	  < examples/secrets/mail-gun-api-token.envsubst.yaml \
	  | kubectl apply -f -
	@envsubst \
	  < examples/secrets/mailer-send-api-token.envsubst.yaml \
	  | kubectl apply -f -
	@examples/custom-resources/create.sh

.PHONY: delete-examples
delete-examples:
	@kubectl delete secret mail-gun-api-token
	@kubectl delete secret mailer-send-api-token
	@examples/custom-resources/delete.sh

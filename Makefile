.PHONY: help
help:
	@echo "email-sender-operator"
	@echo "---------------------"
	@echo "Available targets are:"
	@echo
	@echo "Operation:"
	@echo "\t install-operator   \t\t Installs operator into cluster."
	@echo "\t uninstall-operator \t\t Uninstalls operator from cluster."
	@echo
	@echo "Development & testing:"
	@echo "\t build-image                  \t\t Builds controller's Docker image."
	@echo "\t install-controller-with-dev  \t\t Installs all controller's Python project dependencies."
	@echo "\t install-controller           \t\t Installs controller's Python project dependencies (excl. dev)."
	@echo "\t run-controller               \t\t Starts controller."
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

.PHONY: install-operator
install-operator:
	@helm install --atomic --namespace default --timeout 60s \
		email-sender-operator \
		email-sender-operator/ \

.PHONY: uninstall-operator
uninstall-operator:
	@helm uninstall --namespace default email-sender-operator

.PHONY: build-image
build-image:
ifdef TAG
	@docker build --tag $(TAG) .
else
	@echo "Nothing to do: TAG unset."
endif

.PHONY: run-controller
run-controller:
	@poetry run kopf run --all-namespaces src/main.py

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

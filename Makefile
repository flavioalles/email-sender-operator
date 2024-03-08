.PHONY: help
help:
	@echo "email-sender-operator"
	@echo "---------------------"
	@echo "Available targets are:"
	@echo
	@echo "Operation:"
	@echo "\t run             \t\t Starts operator."
	@echo
	@echo "Development & testing:"
	@echo "\t install         \t\t Installs python project dependencies."
	@echo "\t create-examples \t\t Creates example objects (at examples/custom-resources)."
	@echo "\t delete-examples \t\t Deletes example objects (at examples/custom-resources)."

.PHONY: install
install:
	@poetry install --with=dev

.PHONY: run
run:
	@kopf run src/main.py

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

.PHONY: destroy-examples
destroy-examples:
	@kubectl delete secret mail-gun-api-token
	@kubectl delete secret mailer-send-api-token
	@examples/custom-resources/delete.sh

#!/usr/bin/env bash

BASE_PATH="examples/custom-resources"

kubectl delete -f $BASE_PATH/email-sender-configs/mail-gun.yaml
kubectl delete -f $BASE_PATH/email-sender-configs/mailer-send.yaml
kubectl delete -f $BASE_PATH/emails/mail-gun.yaml
kubectl delete -f $BASE_PATH/emails/mailer-send.yaml

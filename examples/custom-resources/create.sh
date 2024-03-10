#!/usr/bin/env bash

BASE_PATH="examples/custom-resources"

kubectl apply -f $BASE_PATH/email-sender-configs/mail-gun.yaml
kubectl apply -f $BASE_PATH/email-sender-configs/mailer-send.yaml
kubectl apply -f $BASE_PATH/email-sender-configs/unknown.yaml
kubectl apply -f $BASE_PATH/emails/a-proper-email-via-mail-gun.yaml
kubectl apply -f $BASE_PATH/emails/a-failed-email-via-mail-gun.yaml
kubectl apply -f $BASE_PATH/emails/a-proper-email-via-mailer-send.yaml
kubectl apply -f $BASE_PATH/emails/a-failed-email-via-mailer-send.yaml
kubectl apply -f $BASE_PATH/emails/an-email-via-unknown.yaml

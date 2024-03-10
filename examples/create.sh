#!/usr/bin/env bash

BASE_PATH="examples"

envsubst \
  < $BASE_PATH/secrets/mail-gun.envsubst.yaml \
  | kubectl apply -f -
envsubst \
  < $BASE_PATH/secrets/mailer-send.envsubst.yaml \
  | kubectl apply -f -
envsubst \
  < $BASE_PATH/custom-resources/email-sender-configs/mail-gun.envsubst.yaml \
  | kubectl apply -f -
envsubst \
  < $BASE_PATH/custom-resources/email-sender-configs/mailer-send.envsubst.yaml \
  | kubectl apply -f -
kubectl apply -f $BASE_PATH/custom-resources/email-sender-configs/unknown.yaml
kubectl apply -f $BASE_PATH/custom-resources/emails/a-failed-email-via-mail-gun.yaml
envsubst \
  < $BASE_PATH/custom-resources/emails/a-proper-email-via-mail-gun.envsubst.yaml \
  | kubectl apply -f -
kubectl apply -f $BASE_PATH/custom-resources/emails/a-failed-email-via-mailer-send.yaml
envsubst \
  < $BASE_PATH/custom-resources/emails/a-proper-email-via-mailer-send.envsubst.yaml \
  | kubectl apply -f -
kubectl apply -f $BASE_PATH/custom-resources/emails/an-email-via-unknown.yaml

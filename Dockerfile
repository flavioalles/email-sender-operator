FROM python:3.12

ADD . /email-sender-operator/
WORKDIR /email-sender-operator
RUN make install-controller

ENTRYPOINT ["make", "run-controller"]

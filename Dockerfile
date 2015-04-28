FROM quay.io/cygnus/cygnus-python:cpython-2.7.10

RUN mkdir /opt/cyg
ADD . /opt/cyg
WORKDIR /opt/cyg


# Because we have not yet published a version of cygnet-common publicly
# we just have to install it before running setup.py manually for now.
# We also had to make this a public repo for this to work.
RUN ["pip", "install", "https://github.com/Cygnus-Inc/cygnet-common/zipball/master"]

RUN ["python", "setup.py", "install"]

# In order for this container to connect to the WAMP router automatically,
# it is necessary to assume/require a few things so things work correctly.

# For automatic configuration, we rely on the router being at
# "ws://<$ip_address>/ws"
# ENV WAMP_WEBSOCKET_URL="ws://127.0.0.1/ws"

ENV WAMP_REALM="realm1"
EXPOSE 80

CMD ["cygnus-adapter"]


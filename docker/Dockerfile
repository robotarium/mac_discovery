FROM arm32v6/alpine

COPY qemu-arm-static /usr/bin

RUN apk update && apk upgrade

# Get python + deps.  Most of these are actually for netifaces install
RUN apk add --no-cache git python3 python3-dev gcc musl-dev linux-headers

ADD https://api.github.com/repos/robotarium/vizier/git/refs/heads/master version.json
RUN git clone https://github.com/robotarium/vizier
RUN cd vizier && python3 -m pip install .

ADD https://api.github.com/repos/robotarium/mac_discovery/git/refs/heads/master version.json
RUN git clone https://github.com/robotarium/mac_discovery
RUN cd mac_discovery && python3 -m pip install .

ARG PORT
ENV PORT ${PORT}

ENTRYPOINT python3 -m macdiscovery.server ${PORT}

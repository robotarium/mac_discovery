#!/bin/bash

docker run -d \
	--label=com.centurylinklabs.watchtower.enable=false \
	--restart always \
	--name watchtower_mac_discovery \
	-v /var/run/docker.sock:/var/run/docker.sock \
	v2tec/watchtower:armhf-latest -i 60 --debug mac_discovery

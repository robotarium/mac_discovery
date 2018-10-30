#!/bin/bash

docker run -d \
	--restart always \
	--name watchtower_mac \
	-v /var/run/docker.sock:/var/run/docker.sock \
	v2tec/watchtower:armhf-latest -i 60 --debug mac_discovery

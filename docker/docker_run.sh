#!/bin/bash

docker run -d \
	--name mac_discovery \
	--restart always \
	--net host \
	robotarium/mac_discovery

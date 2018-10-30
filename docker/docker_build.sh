#!/bin/bash 

docker build --tag robotarium:mac_discovery \
	--build-arg PORT=$1 .

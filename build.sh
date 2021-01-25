#!/bin/bash

readonly PROJECT=pyvmsnap
readonly CONTAINER_OLD=$(docker ps -q --all --filter name="$PROJECT")

docker stop "$CONTAINER_OLD"
docker rm "$CONTAINER_OLD"
docker build --tag "$PROJECT" --build-arg project="$PROJECT" .
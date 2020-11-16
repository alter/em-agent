#!/bin/bash
cd /opt/em-agent
while true
do
  if [ "$(git fetch --dry-run 2>&1 | wc -l)" -gt 0 ]
  then
    git pull
    docker restart em-agent
  fi
  sleep 60
done

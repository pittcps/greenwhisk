#!/bin/bash

# List of machines to run the script on
#machines=(
#    "ric-data-02" "invoker0" "ric-data-03" "invoker1" "ric-data-04" "invoker2" "ric-data-05"
#     "invoker3" "ric-data-06" "invoker4" "ric-data-08" "invoker6"
#     "ric-data-09" "invoker7" "ric-data-10" "invoker8"
#)
machines=(
     "ric-data-02" "invoker0" "ric-data-03" "invoker1" "ric-data-04" "invoker2" "ric-data-05"
     "invoker3" "ric-data-06" "invoker4" "ric-data-07" "invoker5" "ric-data-08" "invoker6"
     "ric-data-09" "invoker7" "ric-data-10" "invoker8"
)
username="jas644"

image="ssreekmr/invoker:latest"

redis_image="redis:4.0"

for ((i=0; i<${#machines[@]}; i+=2)); do

  ip="${machines[$i]}"
  machine="${machines[$i+1]}"
  ssh "${username}@${ip}" << EOF
    rm -f /var/tmp/wsklogs/${machine}/${machine}_logs.log
    container_ids=\$(docker ps -q -f "ancestor=${image}")
    if [ -z "\$container_ids" ]; then
      echo "No containers found for image ${image}"
    else
      docker stop \$container_ids
      docker rm \$container_ids
      echo "Stopped and removed containers for image ${image}"
    fi
    docker pull $image
    echo "docker pull ${image}"
EOF

rm -f /var/tmp/wsklogs/controller0/controller0_logs.log
container_ids=$(docker ps -q -f "ancestor=${redis_image}")
if [ -z "$container_ids" ]; then
  echo "No containers found for image ${redis_image}"
else
  docker stop "$container_ids"
  docker rm "$container_ids"
  echo "Stopped and removed containers for image ${redis_image}"
fi
done

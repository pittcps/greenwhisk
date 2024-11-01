#!/bin/bash

# List of machines to run the script on
# machines=(
#    "ric-data-02" "invoker0" "ric-data-03" "invoker1" "ric-data-04" "invoker2" "ric-data-05"
#     "invoker3" "ric-data-06" "invoker4" "ric-data-08" "invoker6"
#     "ric-data-09" "invoker7" "ric-data-10" "invoker8"
# )
machines=(
   "ric-data-02" "invoker0" "ric-data-03" "invoker1" "ric-data-04" "invoker2" "ric-data-05"
    "invoker3" "ric-data-06" "invoker4" "ric-data-07" "invoker5" "ric-data-08" "invoker6"
    "ric-data-09" "invoker7" "ric-data-10" "invoker8"
)

# machines=(
#    "192.168.0.11" "invoker0" "192.168.0.12" "invoker1" "192.168.0.13" "invoker2" "192.168.0.14"
#    "invoker3" "192.168.0.15" "invoker4" "192.168.0.16" "invoker5" "192.168.0.17" "invoker6"
# )

# machines=("192.168.0.11" "invoker0" "192.168.0.12" "invoker1" "192.168.0.13" "invoker2"
#   "192.168.0.14" "invoker3" "192.168.0.15" "invoker4" "192.168.0.16" "invoker5" "192.168.0.17" "invoker6")
username="jas644"


mkdir /data/02/stephen/energy-aware-openwhisk/ow_exps/baseline_logs/
# Loop through the machines and start the script on each one
for ((i=0; i<${#machines[@]}; i+=2)); do
  ip="${machines[$i]}"
  machine="${machines[$i+1]}"
  echo "${machine}"
  echo "${ip}"
  source_path="${username}@${ip}:/var/tmp/wsklogs/${machine}/${machine}_logs.log"
  echo "$source_path"
  dest_path="/data/02/stephen/energy-aware-openwhisk/ow_exps/baseline_logs/"
  scp "$source_path" "$dest_path"
  echo "Copied $machine"
  done

cp /var/tmp/wsklogs/controller0/controller0_logs.log /data/02/stephen/energy-aware-openwhisk/ow_exps/baseline_logs/

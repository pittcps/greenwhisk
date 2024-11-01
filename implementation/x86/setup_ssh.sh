#!/bin/bash

# List of remote machines
# machines=(
#     "ric-data-02" "ric-data-03" "ric-data-04"
#     "ric-data-05" "ric-data-06"
#      "ric-data-08" "ric-data-09" "ric-data-10"
# )
machines=(
    "ric-data-02" "ric-data-03" "ric-data-04"
    "ric-data-05" "ric-data-06" "ric-data-07"
     "ric-data-08" "ric-data-09" "ric-data-10"
)
username=$1
echo $username
echo $2
# Generate SSH key pair (if not already generated)
if [ ! -f ~/.ssh/cluster_id_rsa ]; then
    ssh-keygen -t rsa -N "" -f ~/.ssh/cluster_id_rsa
fi

# Install sshpass utility (if not already installed)
#if ! command -v sshpass >/dev/null 2>&1; then
#    echo "sshpass utility not found. Installing..."
#    sudo apt-get update
#    sudo apt-get install -y sshpass
#fi

# Iterate over each machine and copy SSH public key
for machine in "${machines[@]}"; do
    # Copy SSH public key to remote machine using sshpass
    ../sshpass -p $2 ssh-copy-id -o StrictHostKeyChecking=no -i ~/.ssh/cluster_id_rsa.pub "$username@$machine"
done

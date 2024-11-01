#  How to setup the Pi cluster
1. A local machine acts as the controller and 9 of the pi's act as invokers (One of the pi is the head node which acts as the DHCP and NFS server)
2. Make sure the static ip addresses of all pie's in their ethernet port is 192.168.0.11-19
   1. This is setup by the head node which acts as the DHCP server as well as the NFS server which has the ip-address: 192.168.0.2
   2. If not follow the instructions here to setup the DHCP server and NFS server: https://www.raspberrypi.com/tutorials/cluster-raspberry-pi-tutorial/
3. Make sure your local machine (which acts as the controller) has a static ip address of 192.168.0.1 for its ethernet port
4. Run ```bash setup_ssh.sh``` to set up ssh connections between your device and all the pi's
5. The deployment process involves pushing multi-arch docker images to a docker hub and then pulling it in to each pi since multi-architecture docker builds can only be pushed to a repository and can't be saved locally (This was the state when the project was in progress. If it has changed, modify the docker build commands at ./gradle/docker.gradle)
    1. The pi's should have already been logged into a docker account (ssreekmr), if not login to a docker hub account.
6. Modify ansible/environments/host-dist/hosts to reflect your local machine $USER in ansible_user

# Deploying Apache OpenWhisk
1. Install wsk-cli into your local machine. Instructions found here: https://github.com/apache/openwhisk-cli#downloading-released-binaries
   2. Deploy openwhisk by running the below commands in succession\
      1. `./gradlew distDocker // Builds docker images`
      2. Setup ansible using
         ```
         # Ubuntu
         apt-get install python-pip
         pip install 
         pip install ansible==2.5.2
         pip install jinja2==2.9.6
         
         ```
      3. ```ENVIRONMENT=host-dist```
      4. ```cd ansible```
      5. ```ansible-playbook -i environments/$ENVIRONMENT prereq.yml // Install prereqs```
      6. ```ansible-playbook -i environments/$ENVIRONMENT couchdb.yml
	 pip install -U 'requests<2.29.0'
         ansible-playbook -i environments/$ENVIRONMENT initdb.yml
         ansible-playbook -i environments/$ENVIRONMENT wipe.yml
         ansible-playbook -i environments/$ENVIRONMENT openwhisk.yml
      
         # installs a catalog of public packages and actions
         ansible-playbook -i environments/$ENVIRONMENT postdeploy.yml
      
         # to use the API gateway
         ansible-playbook -i environments/$ENVIRONMENT apigateway.yml```

# Changing setup in running experiments
1. Modify the file energy-aware-openwhisk/core/controller/src/main/resources/reference.conf file
   1. Change whisk.loadbalancer.scheduler to "baseline", "consistent-hashing, "greedy", "weighted-dist" to reflect different algorithms.
   2. Modify ansible/host-dist/host to change number of invokers to execute experiements
      1. Comment out invokers by prepending the line with ;

# Running experiments
1. Once deployment is finished. Run these scripts to start the experiments. Modify the files inside the script to get modify experiments
   1. ```
      cd ow_exps
      python test_bed.py && sleep 10 && bash collect_system_logs.sh && bash cleanup.sh
      ```
2. Modify collect_system_logs.sh file to reflect directories for new experiments and add them to git
3. All results are stored inside the ow_exps dir
4. Run `python collect_cold_warm_start.py` to collect information regarding cold and warm start of containers per experiment.
5. Run `python collect_exec_latency.py` to collect execution latency per experiment (Time taken for invoker to finish execution).
6. Run `python collect_total_latency.py` to collect total latency per experiment (Time taken for invoker to finish and controller to get back the results).
7. Results are stored in ow_exps/latency_and_dropped and ow_exps/cold_warm_starts



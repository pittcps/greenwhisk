import os
import matplotlib.pyplot as plt
import re
from datetime import datetime

dir_names = ['baseline_logs_three_nodes', 'baseline_logs_five_nodes',
             'baseline_logs_seven_nodes', 'baseline_logs']
translate = {
    'baseline_logs_three_nodes': 3,
    'baseline_logs_five_nodes': 5,
    'baseline_logs_seven_nodes': 7,
    'baseline_logs': 9
}

pattern1 = r"posting topic '(\w+)' with activation id '(\w+)'"
pattern2 = r"received completion ack for '(\w+)'"
escape_pattern = r"tid_sid_invokerHealth"


def extract_details_from_string(string, comp=False):
    # Extract timestamp
    timestamp_match = re.search(r"\[(.*?)\]", string)
    if timestamp_match:
        timestamp_str = timestamp_match.group(1)
    else:
        timestamp_str = ""

    # Convert timestamp to datetime object
    timestamp_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    timestamp = datetime.strptime(timestamp_str, timestamp_format) if timestamp_str else None

    # Extract activation ID
    if comp:
        activation_id_match = re.search(r"for '(.*?)'", string)
    else:
        activation_id_match = re.search(r"activation id '(.*?)'", string)
    if activation_id_match:
        activation_id = activation_id_match.group(1)
    else:
        activation_id = ""

    return timestamp, activation_id

if __name__ == "__main__":
    node_latency = {}
    node_dropped = {}

    for dirname in dir_names:
        send_times = {}
        comp_times = {}
        with open(f'./{dirname}/controller0_logs.log') as file:
            for line in file:
                if re.search(pattern1, line) and not re.search(escape_pattern, line):
                    time, actId = extract_details_from_string(line)
                    send_times[actId] = time

                if re.search(pattern2, line) and not re.search(escape_pattern, line):
                    time, actId = extract_details_from_string(line, comp=True)
                    comp_times[actId] = time

        common_keys = set(send_times.keys()) & set(comp_times.keys())
        dropped_keys = set(send_times.keys()) - set(comp_times.keys())

        latency = 0
        for key in common_keys:
            time_diff = (comp_times[key] - send_times[key]).total_seconds()
            latency += time_diff/60

        avg_latency = latency / len(common_keys)

        dropped = len(dropped_keys)
        node_latency[translate[dirname]] = avg_latency
        node_dropped[translate[dirname]] = dropped

    if not os.path.isdir('./latency_and_dropped'):
        os.mkdir('./latency_and_dropped')

    # Plot latency graph
    plt.bar(node_latency.keys(), node_latency.values())
    plt.xlabel('No of nodes')
    plt.ylabel('Avg latency in mins for baseline')
    plt.savefig('./latency_and_dropped/total_latency_num_nodes_baseline.png')
    plt.close()

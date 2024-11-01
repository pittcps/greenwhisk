import numpy as np
import os
import matplotlib.pyplot as plt
import re
from datetime import datetime
import pickle
import matplotlib
import csv

# Set global font size to 16
matplotlib.rcParams.update({'font.size': 16})

# dir_names = ['consistent_hashing_logs', 'baseline_logs', 'greedy_logs', 'weighted_dist_logs']
# translate = {
#     'consistent_hashing_logs': 'CH',
#     'baseline_logs': 'OW',
#     'greedy_logs': 'GR',
#     'weighted_dist_logs': 'WD'
# }

dir_names = ['consistent_hashing_logs', 'baseline_logs', 'greedy_logs', 'weighted_dist_logs']
translate = {
    'consistent_hashing_logs': 'Consistent',
    'baseline_logs': 'OpenWhisk',
    'greedy_logs': 'Greedy',
    'weighted_dist_logs': 'GreenWhisk'
}

pattern1 = r"posting topic '(\w+)' with activation id '(\w+)'"
pattern2 = r"received completion ack for '(\w+)'"
escape_pattern = r"tid_sid_invokerHealth"


def save_set_to_pickle_file(data_set, file_path):
    with open(file_path, 'wb') as file1:
        pickle.dump(data_set, file1)


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
    alg_latency = {}
    alg_dropped = {}

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

        save_set_to_pickle_file(common_keys, './total_pick.pkl')

        latency = 0
        all_latencies = []
        for key in common_keys:
            time_diff = (comp_times[key] - send_times[key]).total_seconds()
            latency += time_diff/60
            all_latencies.append(time_diff/60.0)
        # avg_latency = latency / len(common_keys)
        avg_latency = np.quantile(all_latencies, 0.5)

        dropped = len(dropped_keys)
        alg_latency[translate[dirname]] = avg_latency
        alg_dropped[translate[dirname]] = dropped


    csv_file_path = './latency_and_dropped/total_latency__data.csv'
    fieldnames = ['Algorithm', 'Average Latency (minutes)', 'Dropped Invocations']

    # Check if the directory exists before writing the file
    if not os.path.isdir('./latency_and_dropped'):
        os.mkdir('./latency_and_dropped')

    with open(csv_file_path, mode='w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for alg, latency in alg_latency.items():
            writer.writerow({'Algorithm': alg, 'Average Latency (minutes)': latency, 'Dropped Invocations': alg_dropped[alg]})

    print(f"Data has been written to {csv_file_path}")

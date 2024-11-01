import numpy as np
import os
import matplotlib.pyplot as plt
import re
from datetime import datetime
import pickle
import matplotlib

# Set global font size to 16
matplotlib.rcParams.update({'font.size': 16})

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
    alg_std_dev = {}
    alg_dropped = {}
    alg_all_latencies = {}

    for dirname in dir_names:
        send_times = {}
        comp_times = {}
        all_latencies = []  # List to store all latencies for this algorithm

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

        # Calculate latencies and store each latency value
        for key in common_keys:
            latency = (comp_times[key] - send_times[key]).total_seconds() / 60
            all_latencies.append(latency)

        # Calculate average latency and standard deviation
        # avg_latency = np.mean(all_latencies)
        avg_latency = np.quantile(all_latencies, 0.5)
        std_dev = np.std(all_latencies)

        dropped = len(dropped_keys)
        alg_latency[translate[dirname]] = avg_latency
        alg_std_dev[translate[dirname]] = std_dev
        alg_all_latencies[translate[dirname]] = all_latencies
        alg_dropped[translate[dirname]] = dropped

    # Plot latency graph with standard deviation
    fig, ax = plt.subplots()
    positions = np.arange(len(alg_latency))
    bars = ax.bar(positions, alg_latency.values(), yerr=alg_std_dev.values(), align='center', alpha=0.7, ecolor='black', capsize=10)

    # Annotate bars with the average latency and standard deviation
    for bar, (label, std_dev) in zip(bars, alg_std_dev.items()):
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2.0, yval, f'{alg_latency[label]:.2f}±{std_dev:.2f}', va='bottom', ha='center', color='black', fontweight='bold')

    # Set the labels and titles
    ax.set_ylabel('Total Avg Latency (min)')
    ax.set_xticks(positions)
    ax.set_xticklabels(alg_latency.keys())
    ax.set_title('Total Average Latency with Standard Deviation')

    # Removing the top and right spines for a cleaner look
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(True)
    ax.spines['bottom'].set_visible(True)

    # Add a grid behind the bars
    ax.yaxis.grid(True)

    # Save the figure
    plt.tight_layout()
    plt.savefig('total_latency_with_std_dev_annotated.png')
    # plt.show()

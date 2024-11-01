import numpy as np
import os
import matplotlib.pyplot as plt
import re
from datetime import datetime
import pickle
import matplotlib

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
            all_latencies.append(time_diff/1.0)
        # avg_latency = latency / len(common_keys)
        avg_latency = np.quantile(all_latencies, 0.5)

        dropped = len(dropped_keys)
        alg_latency[translate[dirname]] = avg_latency
        alg_dropped[translate[dirname]] = dropped

    if not os.path.isdir('./latency_and_dropped'):
        os.mkdir('./latency_and_dropped')

    # Plot latency graph
    fig, ax = plt.subplots()
    bars = ax.bar(alg_latency.keys(), alg_latency.values())

    # Add numbers on top of each bar with font size 16
    for bar in bars:
        height = bar.get_height()
        # Adjust the position of the annotation to prevent overlapping with the bound
        annotation_y_position = height + 0.5 if height < fig.get_size_inches()[1] * fig.dpi * 0.9 else height - 0.5
        ax.annotate('%.3f' % height,
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')

    ax.set_ylabel('Total Avg Latency (s)')

    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Adjust layout to ensure that the numbers on top of the bars are visible
    plt.tight_layout()

    plt.savefig('./latency_and_dropped/total_latency.png')
    plt.close()
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
#     'consistent_hashing_logs': 'consistent_hashing',
#     'baseline_logs': 'baseline',
#     'greedy_logs': 'greedy',
#     'weighted_dist_logs': 'weighted_dist'
# }
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

pattern1 = r'\[(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z)\] \[INFO\] \[#tid_[a-fA-F0-9]+\] \[ContainerPool\] ' \
           r'containerStart containerState: (\w+) container: (.*?) activations: (\d+) of max (\d+) action: (\w+) ' \
           r'namespace: (\w+) activationId: ([a-fA-F0-9]+) '

pattern2 = r'posted completion of activation (\w+)'
escape_pattern = r"tid_sid_invokerHealth"


def save_set_to_pickle_file(data_set, file_path):
    with open(file_path, 'wb') as file1:
        pickle.dump(data_set, file1)


def extract_details_from_string(string, comp=False):
    timestamp_match = re.search(r"\[(.*?)\]", string)
    if timestamp_match:
        timestamp_str = timestamp_match.group(1)
    else:
        timestamp_str = ""

    # Convert timestamp to datetime object
    timestamp_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    timestamp = datetime.strptime(timestamp_str, timestamp_format) if timestamp_str else None

    if comp:
        activation_id_match = re.search(r"of activation (\w+)", string)
    else:
        activation_id_match = re.search(r"activationId: (\w+)", string)
    if activation_id_match:
        activation_id = activation_id_match.group(1)
    else:
        activation_id = ""

    return timestamp, activation_id


if __name__ == '__main__':
    alg_latency = {}
    alg_dropped = {}

    for dirname in dir_names:
        send_times = {}
        comp_times = {}

        list_files = [f'./{dirname}/invoker{i}_logs.log' for i in range(0, 9)]
        for file in list_files:
            with open(file, 'r') as delta:
                for line in delta:
                    if re.search(pattern1, line) and not re.search(escape_pattern, line):
                        time, actId = extract_details_from_string(line)
                        send_times[actId] = time

                    if re.search(pattern2, line) and not re.search(escape_pattern, line):
                        time, actId = extract_details_from_string(line, comp=True)
                        comp_times[actId] = time

        common_keys = set(send_times.keys()) & set(comp_times.keys())
        dropped_keys = set(send_times.keys()) - set(comp_times.keys())

        save_set_to_pickle_file(common_keys, './exec_pick.pkl')
        latency = 0
        for key in common_keys:
            time_diff = (comp_times[key] - send_times[key]).total_seconds()
            latency += time_diff/60

        avg_latency = latency / len(common_keys)

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
        ax.annotate('%.2f' % height,
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')

    ax.set_ylabel('Avg execution latency/min')

    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Adjust layout to ensure that the numbers on top of the bars are visible
    plt.tight_layout()

    plt.savefig('./latency_and_dropped/avg_exec_latency.png')
    plt.close()

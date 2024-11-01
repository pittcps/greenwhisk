import re
import os
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
import matplotlib

# Set global font size to 16
matplotlib.rcParams.update({'font.size': 16})


dir_names = ['weighted_dist_logs_three_nodes', 'weighted_dist_logs_five_nodes',
             'weighted_dist_logs_seven_nodes', 'weighted_dist_logs']
translate = {
    'weighted_dist_logs_three_nodes': 3,
    'weighted_dist_logs_five_nodes': 5,
    'weighted_dist_logs_seven_nodes': 7,
    'weighted_dist_logs': 9
}

pattern1 = r"posting topic '(\w+)' with activation id '(\w+)'"
escape_pattern = r"tid_sid_invokerHealth"

pattern2 = r'\[(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z)\] \[INFO\] \[#tid_[a-fA-F0-9]+\] \[ContainerPool\] ' \
           r'containerStart containerState: (\w+) container: (.*?) activations: (\d+) of max (\d+) action: (\w+) ' \
           r'namespace: (\w+) activationId: ([a-fA-F0-9]+) '

def get_start_type(string):
    if 'cold' in string.lower():
        return 'cold'
    elif string.lower() == 'prewarmed':
        return 'prewarm'
    else:
        return 'warm'


if __name__ == "__main__":
    node_counts = {}
    dropped_acts = {}

    for dirname in dir_names:
        invoker_activations = {}
        node_num = translate[dirname]
        print(f'{node_num}\n')
        with open(f'./{dirname}/controller0_logs.log', 'r') as file1:
            for line in file1:
                result1 = re.search(pattern1, line)
                if result1 and not re.search(escape_pattern, line):
                    invoker = int(result1.group(1)[-1])
                    actId = result1.group(2)

                    if invoker in invoker_activations.keys():
                        invoker_activations[invoker].append(actId)
                    else:
                        invoker_activations[invoker] = [actId]

            for key in invoker_activations.keys():
                actIds = {}
                file_name = f'./{dirname}/invoker{key}_logs.log'
                with open(file_name, 'r') as file2:
                    for line in file2:
                        result2 = re.search(pattern2, line)
                        if result2 and not re.search(escape_pattern, line):
                            activation = result2.group(8)
                            if activation in invoker_activations[key]:
                                start_type = get_start_type(result2.group(2))
                                actIds[activation] = start_type

                if node_num in node_counts.keys():
                    node_counts[node_num].extend(list(actIds.values()))
                else:
                    node_counts[node_num] = list(actIds.values())

        node_counts[node_num] = Counter(node_counts[node_num])

    cold_starts = [node_counts[key]['cold'] for key in node_counts.keys()]
    prewarm_starts = [node_counts[key]['prewarm'] for key in node_counts.keys()]
    warm_starts = [node_counts[key]['warm'] for key in node_counts.keys()]

    # Combine 'warm' and 'prewarm' starts
    combined_warm_prewarm = [w + p for w, p in zip(warm_starts, prewarm_starts)]

    plt.figure(figsize=(10, 6))

    # Plotting bars
    bar_positions = np.arange(len(cold_starts))
    plt.bar(bar_positions - 0.2, cold_starts, color='green', width=0.4)
    plt.bar(bar_positions + 0.2, combined_warm_prewarm, color='red', width=0.4)

    # Adding numbers on top of each bar
    for position, value in zip(bar_positions - 0.2, cold_starts):
        plt.text(position, value, str(value), ha='center', va='bottom')
    for position, value in zip(bar_positions + 0.2, combined_warm_prewarm):
        plt.text(position, value, str(value), ha='center', va='bottom')

    # Adjusting plot aesthetics
    plt.xlabel('Number of Nodes')
    plt.xticks(bar_positions, labels=[str(key) for key in node_counts.keys()])
    plt.ylabel('Invocations')

    # Adjusting legend
    plt.legend(['Cold Starts', 'Warm Starts'], loc='upper center', 
               bbox_to_anchor=(0.5, 1.15), ncol=2, frameon=False)

    # Removing top and right spines
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)

    plt.savefig('./cold_warm_starts/cold_warm_starts_num_nodes_modified.png')
    plt.close()

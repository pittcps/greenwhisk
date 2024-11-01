import re
import os
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter

dir_names = ['consistent_hashing_logs', 'baseline_logs', 'greedy_logs', 'weighted_dist_logs']
translate = {
    'consistent_hashing_logs': 'consistent_hashing',
    'baseline_logs': 'baseline',
    'greedy_logs': 'greedy',
    'weighted_dist_logs': 'weighted_dist'
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
    algo_counts = {}
    dropped_acts = {}

    for dirname in dir_names:
        invoker_activations = {}
        algo_name = translate[dirname]
        print(f'{algo_name}/n')
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

                if algo_name in algo_counts.keys():
                    algo_counts[algo_name].extend(list(actIds.values()))
                else:
                    algo_counts[algo_name] = list(actIds.values())

        algo_counts[algo_name] = Counter(algo_counts[algo_name])

    tot_algos = len(algo_counts.keys())

    cold_starts = [algo_counts[key]['cold'] for key in algo_counts.keys()]
    prewarm_starts = [algo_counts[key]['prewarm'] for key in algo_counts.keys()]
    warm_starts = [algo_counts[key]['warm'] for key in algo_counts.keys()]

    print(warm_starts)

    plt.figure(figsize=(10, 6))

    for key in algo_counts.keys():
        plt.bar(np.arange(0, tot_algos) - 0.2, cold_starts, color='red', width=0.2)
        plt.bar(np.arange(0, tot_algos), prewarm_starts, color='green', width=0.2)
        plt.bar(np.arange(0, tot_algos) + 0.2, warm_starts, color='blue', width=0.2)

    plt.xlabel('Algorithms')
    plt.xticks(np.arange(0, tot_algos), ['consistent_hashing', 'baseline', 'greedy', 'weighted_dist'])
    plt.ylabel('Cold/Warm start counts')
    plt.legend(['Cold Starts', 'Pre warm Starts', 'Warm Starts'], loc='center right')
    plt.savefig('./cold_warm_starts/consol_cold_warm_starts.png')
    plt.close()

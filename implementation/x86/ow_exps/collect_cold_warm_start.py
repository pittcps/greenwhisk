import os
import re
import matplotlib.pyplot as plt
import numpy as np

dir_names = ['consistent_hashing_logs', 'baseline_logs', 'greedy_logs', 'weighted_dist_logs']
translate = {
    'consistent_hashing_logs': 'consistent_hashing',
    'baseline_logs': 'baseline',
    'greedy_logs': 'greedy',
    'weighted_dist_logs': 'weighted_dist'
}
pattern1 = r"Total number of warm starts in this minute: "
pattern2 = r"Total number of cold starts in this minute: "
pattern3 = r"Total number of prewarmed starts in this minute: "

# invoker_start_pattern = r'\[(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z)\] \[INFO\] \[#tid_sid_invokerHealth] \[' \
#                         r'ContainerPool\] ' \
#                         r'containerStart containerState: (\w+) container: (.*?) activations: (\d+) of max (\d+) ' \
#                         r'action: (.*?) ' \
#                         r'namespace: (\w+) activationId: ([a-fA-F0-9]+) '

invoker_start_pattern = r'\[(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z)\] \[INFO\] \[#tid_sid_invokerHealth\] \[' \
                        r'ContainerPool\] containerStart ' \
                        r'containerState: (\w+) container: (.*?) activations: (\d+) of max (\d+) action: ' \
                        r'invokerHealthTestAction0 namespace: ' \
                        r'(.*?) activationId: ([a-fA-F0-9]+) '


def extract_count_from_string(extracted_str):
    pattern = r'\d+$'
    match = re.search(pattern, extracted_str)
    number = 0
    if match:
        number = match.group()
    return number


def extract_container_type_from_string(extracted_str):
    # Define the regular expression pattern to match the containerState
    pattern = r'containerState:\s+(\w+)'

    # Use re.search to find the pattern in the line
    match = re.search(pattern, extracted_str)

    if match:
        # Extract and return the containerState
        container_state = match.group(1)
        if 'cold' in container_state.lower():
            return 'cold'
        else:
            return 'warm'
    else:
        # Return None if containerState is not found in the line
        return None


def get_values_from_file(file_name):
    cold_start = 0
    warm_start = 0
    prewarm_start = 0
    health_starts = {}
    with open(file_name, 'r') as control:
        for line in control:
            result1 = re.search(pattern1, line)
            if result1:
                warm_start_count = extract_count_from_string(result1.string)
                if warm_start_count:
                    warm_start += int(warm_start_count)

            result2 = re.search(pattern2, line)
            if result2:
                cold_start_count = extract_count_from_string(result2.string)
                if cold_start_count:
                    cold_start += int(cold_start_count)

            result3 = re.search(pattern3, line)
            if result3:
                prewarm_start_count = extract_count_from_string(result3.string)
                if prewarm_start_count:
                    prewarm_start += int(prewarm_start_count)

            result4 = re.search(invoker_start_pattern, line)
            # # result5 = re.search(invoker_health_pattern, line)
            # if result4:
            #     container_type = extract_container_type_from_string(line)
            #     if container_type:
            #         if container_type == 'cold':
            #             cold_start -= 1
            #         else:
            #             warm_start -= 1

        return [cold_start, warm_start, prewarm_start]


if __name__ == '__main__':
    invoker_start_map = []
    algo_counts = {}
    for dirname in dir_names:
        for invoker_num in range(0, 9):
            invoker_file_path = f'./{dirname}/invoker{invoker_num}_logs.log'
            start_counts = get_values_from_file(invoker_file_path)

            if translate[dirname] in algo_counts.keys():
                algo_counts[translate[dirname]].append(start_counts)
            else:
                algo_counts[translate[dirname]] = [start_counts]

    if not os.path.isdir('./cold_warm_starts'):
        os.mkdir('./cold_warm_starts')

    bar_width = 0.2
    bar_gap = 0.05
    tot_algos = len(algo_counts.keys())

    consol_alg_counts = {}
    for key in algo_counts.keys():
        consol_alg_counts[key] = (sum([val[0] for val in algo_counts[key]]), sum([val[1] for val in algo_counts[key]]),
                                  sum([val[2] for val in algo_counts[key]])
                                  )
        print(f'Sum of all starts in {key}: {sum([val for val in consol_alg_counts[key]])}')

    cold_starts = [val[0] for val in consol_alg_counts.values()]
    warm_starts = [val[1] for val in consol_alg_counts.values()]
    prewarm_starts = [val[2] for val in consol_alg_counts.values()]

    plt.figure(figsize=(15, 12))
    for alg in consol_alg_counts.keys():
        rects1 = plt.bar(np.arange(0, tot_algos) - 0.2, cold_starts, color='red', width=0.2)
        rects2 = plt.bar(np.arange(0, tot_algos), warm_starts, color='blue', width=0.2)
        rects3 = plt.bar(np.arange(0, tot_algos) + 0.2, prewarm_starts, color='green', width=0.2)

        # Add data labels
        for rect in rects1:
            height = rect.get_height()
            plt.text(rect.get_x() + rect.get_width()/2., height, '%d' % int(height), ha='center', va='bottom')
        for rect in rects2:
            height = rect.get_height()
            plt.text(rect.get_x() + rect.get_width()/2., height, '%d' % int(height), ha='center', va='bottom')
        for rect in rects3:
            height = rect.get_height()
            plt.text(rect.get_x() + rect.get_width()/2., height, '%d' % int(height), ha='center', va='bottom')

    plt.xlabel('Algorithms')
    plt.xticks(np.arange(0, tot_algos), ['consistent_hashing', 'baseline', 'greedy', 'weighted_dist'])
    plt.ylabel('Cold/Warm start counts')
    plt.legend(['Cold Starts', 'Warm Starts', 'Pre-Warm Starts'])
    plt.savefig('./cold_warm_starts/consol_cold_warm_starts.png')
    plt.close() 

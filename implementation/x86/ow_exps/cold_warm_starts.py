import re
import os
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter, OrderedDict
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

dir_names = ['consistent_hashing_logs', 'baseline_logs', 'greedy_logs', 'weighted_dist_logs']
# dir_names = [ 'weighted_dist_logs']

translate = {
    'consistent_hashing_logs': 'Consistent',
    'baseline_logs': 'OpenWhisk',
    'greedy_logs': 'Greedy',
    'weighted_dist_logs': 'GreenWhisk'
}
pattern1 = r"posting topic '(\w+)' with activation id '(\w+)'"
escape_pattern = r"tid_sid_invokerHealth"

# pattern2 = r'\[(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z)\] \[INFO\] \[#tid_[a-fA-F0-9]+\] \[ContainerPool\] ' \
#            r'containerStart containerState: (\w+) container: (.*?) activations: (\d+) of max (\d+) action: (\w+) ' \
#            r'namespace: (\w+) activationId: ([a-fA-F0-9]+) '

# RIC
pattern2 = r'\[(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z)\] \[INFO\] \[#tid_[a-fA-F0-9]+\] \[ContainerPool\] containerStart containerState: (\w+) container: (.*?) activations: (\d+) of max (\d+) action: (\w+) namespace: (\w+\.\w+) activationId: ([a-fA-F0-9]+)'

# PI
# pattern2 = r'\[(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z)\] \[INFO\] \[#tid_[a-fA-F0-9]+\] \[ContainerPool\] containerStart containerState: (\w+) container: (.*?) activations: (\d+) of max (\d+) action: (\w+) namespace: (\w+) activationId: ([a-fA-F0-9]+)'

pattern3 = r"Rescheduling"
pattern4 = r"processing from buffer"

def get_start_type(string): 
    # warmed, warming, and warmingCold are warm
    if 'warm' in string.lower():
        return 'warm'
    elif 'prewarm' in string.lower():
        return 'prewarm'
    else:
        return 'cold'

if __name__ == "__main__":
   
    # id_counts = 0
    node_counts = OrderedDict()
    for dirname in dir_names:
        
        dropped_acts = OrderedDict()
        total_activations = 0
        invoker_functions_count = 0
        reschedule_count = 0
        activation_list = OrderedDict()

        invoker_activations = OrderedDict()
        node_num = translate[dirname]
        print(f'{node_num}\n')
        with open(f'./{dirname}/controller0_logs.log', 'r') as file1:
            for line in file1:
                result1 = re.search(pattern1, line)
                if result1 and not re.search(escape_pattern, line):
                    invoker = int(result1.group(1)[-1])
                    actId = result1.group(2)
                    total_activations += 1
                    activation_list[actId] = True # activation exists
                    
                    if invoker in invoker_activations.keys():
                        invoker_activations[invoker].append(actId)
                    else:
                        invoker_activations[invoker] = [actId]
                
                if total_activations >= 541:
                    break
            print("\n invokers: ", invoker_activations.keys())
            # if len(invoker_activations.keys()) == 0:
            #     print("No activations in invoker:", node_num)
            #     continue
                
            for key in invoker_activations.keys():
                actIds = OrderedDict()
                file_name = f'./{dirname}/invoker{key}_logs.log'
                print("Parsing invoker: ", key)
                with open(file_name, 'r') as file2:
                    for line in file2:
                        result2 = re.search(pattern2, line)
                        
                        if result2 and not re.search(escape_pattern, line):
                            activation = result2.group(8)
                            if not activation in activation_list.keys():
                                print("Not found", activation)
                            activation_list[activation] = False
                            if activation in invoker_activations[key]:
                                start_type = get_start_type(result2.group(2))
                                actIds[activation] = start_type
                                invoker_functions_count += 1
                                
                        elif re.search(pattern3, line) or re.search(pattern4, line):
                            reschedule_count += 1
                            # else:
                            #     print(line)
                        #print(" ---- \n")
                        
                if node_num in node_counts.keys():
                    node_counts[node_num].extend(list(actIds.values()))
                else:
                    node_counts[node_num] = list(actIds.values())

              
                    
        node_counts[node_num] = Counter(node_counts[node_num])
    activations_found = len([ x for x in activation_list.keys() if  activation_list[x]])
    print([ x for x in activation_list.keys() if  activation_list[x]][:20])
    print("invoker_activations_count: ", invoker_functions_count, activations_found, reschedule_count)
    print(node_counts)
    print("\nTotal activations in controller: ", total_activations)
    categories = list(node_counts.keys())
    cold_starts = [node_counts[key]['cold'] for key in categories]
    prewarm_starts = [node_counts[key]['prewarm'] for key in categories]
    warm_starts = [node_counts[key]['warm'] for key in categories]

    # Combine prewarm and warm starts
    combined_prewarm_warm_starts = [prewarm_starts[i] + warm_starts[i] for i in range(len(prewarm_starts))]

    # Create a figure and adjust bar positions
    fig, ax = plt.subplots(figsize=(10, 6))
    bar_width = 0.25
    index = np.arange(len(categories))

    bars1 = plt.bar(index - bar_width/2, cold_starts, color='green', width=bar_width, label='Cold Starts')
    bars2 = plt.bar(index + bar_width/2, combined_prewarm_warm_starts, color='red', width=bar_width, label='Warm Starts')

    # Add numbers on top of each bar with font size 16
    for bar in bars1 + bars2:
        height = bar.get_height()
        ax.annotate('{}'.format(height),
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')

    plt.xticks(index, categories)
    plt.yticks(fontsize=16)  # Set y-axis tick label font size
    ax.set_ylabel('Invocations', fontsize=16)  # Set y-axis label font size

    # Set legend with font size 16
    plt.legend(loc='lower center', bbox_to_anchor=(0.5, 1.05), shadow=False, frameon=False, ncol=2, fontsize=16)

    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout(pad=1.0)  # Adjust layout with padding
    plt.savefig('./cold_warm_starts/cold_warm_starts_combined.png')

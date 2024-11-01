import pandas as pd
import statistics

df = pd.read_csv('./invocations_per_function_md.anon.d10.csv')

# Dropping off unnecessary columns
df = df.drop(labels=['HashOwner', 'HashApp', 'Trigger'], axis=1)

df['total_invocations'] = df.iloc[:, 1:].sum(axis=1)
df = df[df['total_invocations'] >= 15]


def calculate_inter_arrival(row):
    invocations = row.iloc[1:].values.nonzero()[0]
    sum_inter_arrival_times = sum([(invocations[i + 1] - invocations[i]) for i in (range(len(invocations) - 1))])
    return sum_inter_arrival_times / len(invocations)


df['inter_arrival_time'] = df.apply(calculate_inter_arrival, axis=1)
df_sorted = df.sort_values(by=['total_invocations', 'inter_arrival_time'], ascending=[True, False])

df_sorted.reset_index(drop=True)
df_sorted.to_csv('./complete_rare_functions_sorted.csv')
df_sorted.iloc[:50, :].to_csv('./50_rare_functions_sorted.csv')
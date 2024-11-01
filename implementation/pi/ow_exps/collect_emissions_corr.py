import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pickle

dir_names = os.listdir('./EmissionsData')
em_df = pd.DataFrame()

if not os.path.isdir('./emissions_corr/'):
    os.mkdir('./emissions_corr/')

for name in dir_names:
    em_data = np.array([])
    child_dir_names = os.listdir(f'./EmissionsData/{name}/')
    for child_name in child_dir_names:
        df = pd.read_csv(f'./EmissionsData/{name}/{child_name}')
        data = df['MOER'].to_numpy()
        em_data = np.concatenate((em_data, data))
    em_df[name] = em_data

em_df = em_df.apply(lambda x: (x - x.min()) / (x.max() - x.min()))


corr = em_df.corr()
sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f")
plt.title(' Pearson correlation Heatmap')
plt.savefig('./emissions_corr/emissions_correlation_pearson.png')
plt.close()

num_bas = len(dir_names)
cross_corr_mat = np.zeros((num_bas, num_bas))
auto_corr = {}
em_values = em_df.to_numpy()

high_corr = ['PJM_SOUTHWEST', 'SPP_WESTINE', 'SPP_MEMPHIS', 'ERCOT']
low_corr = ['NEVP', 'BPA', 'SOCO', 'TVA']

color = {
    0: 'red',
    1: 'blue',
    2: 'green',
    3: 'purple'
}

# Line graphs
j = 0
plt.figure(figsize=(25, 20))
for column in high_corr:
    cr = color[j]
    y = em_df[column].to_numpy()[::6000]
    x = np.arange(0, len(y))
    plt.plot(x, y, label=column, color=cr)
    j += 1

plt.title('Emission saved trend')
plt.xlabel('Time')
plt.ylabel('MOER')
plt.legend()
plt.savefig('./emissions_corr/emissions_line_plot_high_corr.png')
plt.close()

j = 0
plt.figure(figsize=(25, 20))
for column in low_corr:
    cr = color[j]
    y = em_df[column].to_numpy()[::6000]
    x = np.arange(0, len(y))
    plt.plot(x, y, label=column, color=cr)
    j += 1

plt.title('Emission saved trend')
plt.xlabel('Time')
plt.ylabel('MOER')
plt.legend()
plt.savefig('./emissions_corr/emissions_line_plot_low_corr.png')
plt.close()

for i in range(num_bas):
    array1 = em_values[:, i]
    ac = np.correlate(array1, array1, mode='full')
    auto_corr[dir_names[i]] = ac/np.max(ac)
    for j in range(num_bas):
        if cross_corr_mat[i, j] == 0:
            array2 = em_values[:, j]
            cross_corr = np.correlate(array1, array2, mode='full')
            if abs(cross_corr.min()) >= cross_corr.max():
                cross_corr_mat[i, j] = cross_corr.min()
                cross_corr_mat[j, i] = cross_corr.min()
            else:
                cross_corr_mat[i, j] = cross_corr.max()
                cross_corr_mat[j, i] = cross_corr.max()
    print(f"Row {i} done")

sns.heatmap(cross_corr_mat, annot=False, cmap='coolwarm', fmt=".2f", square=True,
            xticklabels=dir_names, yticklabels=dir_names)

plt.title('Cross-Correlation Heatmap')
plt.savefig('./emissions_corr/emissions_correlation_cross_correlation.png')
plt.close()
print('Here')

plt.figure(figsize=(10, 6))
for i in range(num_bas):
    plt.plot(np.arange(-len(em_values[:, i]) + 1, len(em_values[:, i])), auto_corr[dir_names[i]], marker='o')
plt.title('Auto-Correlation Line Plot')
plt.xlabel('Time Lag')
plt.ylabel('Auto-Correlation')
plt.savefig('./emissions_corr/emissions_correlation_auto_correlation_line.png')
plt.close()
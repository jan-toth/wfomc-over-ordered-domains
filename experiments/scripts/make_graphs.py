import matplotlib.pyplot as plt
import numpy as np
import os

problem_ids = [ '7',  '8', '23',
               '29', '31', '33',
               '39', '42', '45',
               '47', '53', '80',
               '82', '96', '99',
               '102', '130', '137',
               '149', '175', '193',
               '231', '240', '243',
               '269', '284', '292',
               '309']

timec = [ 2.1593, 142.4770, 1.0800,
          1.1203, 0.0907, 1.0237,
          1.2903, 3.0933, 1.2990, 
          0.5853, 303.1333, 0.4497, 
          0.2757, 0.2627, 0.2350, 
          14.2157, 4485.9420, 0.5520, 
          2.3357, 0.4790, 1.2350,
          1.2577, 118.3950, 0.4457, 
          0.8930, 0.7047, 0.6643, 
          0.1810]  

timen = [ 0.780277411,  6.890678962, 0.138254166, 
          0.295500835,  0.105263313, 0.340973695,
          0.25483505 ,  0.167118073, 0.143273433,
          0.07846427 ,  58.10396711, 0.107978662,
          0.111083984,  0.107695738, 0.083938122, 
          11.49181445,  128.0329512, 0.13034447,
          0.0952034  ,  0.110994339, 0.079324405,
          0.114643097,  105.6098412, 0.072592974,
          0.344414473,  0.072847287, 0.122502406,
          0.111396789]

wfomc_times = dict()
ganak_times = dict()
d4_times = dict()

for root, dirs, files in os.walk("results"):
    for file in files:
        if file.endswith("time_wfomc.txt"):
            problem = file[:-14]
            with open("results/" + file, "r") as f:
                for line in f:
                    val = line
            wfomc_times[problem] = float(val)
        elif file.endswith("time_d4.txt"):
            problem = file[:-11]
            with open("results/" + file, "r") as f:
                for line in f:
                    val = line
            d4_times[problem] = float(val)
        elif file.endswith("time_ganak.txt"):
            problem = file[:-14]
            with open("results/" + file, "r") as f:
                for line in f:
                    val = line
            ganak_times[problem] = float(val)
        else:
            continue
        

sorted_indices = np.argsort(timen)
timen = [timen[i] for i in sorted_indices]
timec = [timec[i] for i in sorted_indices]
problem_ids = [problem_ids[i] for i in sorted_indices]

wfomc_np = np.zeros((len(wfomc_times)))
d4_np = np.zeros((len(wfomc_times)))
ganak_np = np.zeros((len(wfomc_times)))

i = 0
for problem, val in wfomc_times.items():
    wfomc_np[i] = wfomc_times[problem]
    ganak_np[i] = ganak_times[problem]
    d4_np[i] = d4_times[problem]
    i += 1

bar_width = 0.25
r1 = np.arange(len(wfomc_times))
r2 = [x + bar_width for x in r1]
r3 = [x + bar_width for x in r2]

plt.figure(figsize=(6, 4))
plt.bar(r1, wfomc_np, color='b', width=bar_width, edgecolor='grey', label='Incremental2')
plt.bar(r2, d4_np, color='r', width=bar_width, edgecolor='grey', label='d4')
plt.bar(r3, ganak_np, color='g', width=bar_width, edgecolor='grey', label='ganak')

plt.xlabel('Problem ID',labelpad=2, fontsize=20)
plt.ylabel('Runtime (s)',labelpad=-1, fontsize=20)
#plt.title('Practical Problem (a)',pad=1, y=-0.23)
plt.xticks([r + bar_width for r in range(len(wfomc_times))], wfomc_times.keys(), rotation=60, fontsize=8)
plt.yscale("log")
plt.tick_params(axis='y', labelsize=15)
plt.tick_params(axis='x', labelsize=9)
plt.subplots_adjust(top=0.95, bottom=0.175, left=0.175, right=0.95)
plt.legend(fontsize=11)
plt.tight_layout()
plt.get_current_fig_manager().set_window_title('comb_runtime')
#plt.show()
plt.savefig('some_runtimes.pdf', format='pdf', bbox_inches='tight')

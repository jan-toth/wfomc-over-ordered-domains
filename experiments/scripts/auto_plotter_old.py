from pathlib import Path

import natsort

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

RESULTS_PATH = Path(__file__).absolute().parent.parent.joinpath("results").joinpath("FROM_INFERENCE")


# inc = ht[ht['algo'] == 'inc']
# d4 = ht[ht['algo'] == 'd4']
# ganak = ht[ht['algo'] == 'ganak']

# inc = ht[ht['problem'] == 'inc']
# inc_times = inc[['problem', 'time']].groupby('problem').median()
# inc_times.sort_index(key=lambda x: np.argsort(natsort.index_natsorted(inc_times.index)))


def plot_seq(df, algo):
    df = df[df["algo"] == algo]
    times = df[['problem', 'time']].groupby('problem').median()
    times = times.sort_index(key=lambda x: np.argsort(natsort.index_natsorted(times.index)))
    return times

        
def split_wmc(df):
    e1_idx = df.index.str.endswith("_e1")
    e3_idx = df.index.str.endswith("_e3")
    def build_new_wmc_df(df, idx):
        filtered = df[idx]
        df.index.str.endswith("_e1")
        ids = [int(x.split('_')[0]) for x in filtered.index]
        times = filtered.to_numpy()
        return pd.DataFrame(times, index=ids, columns=['Time [s]'])
    return build_new_wmc_df(df, e1_idx), build_new_wmc_df(df, e3_idx)


def process_time_measurements(times):
    times = times.sort_index(key=lambda x: np.argsort(natsort.index_natsorted(times.index)))
    return times.index.astype(int).to_numpy(), times.to_numpy()


def foo(df):
    algs = df.algo.unique()
    out = dict()
    for alg in algs:
        select = df[df.algo == alg]
        # select = select[select.problem.str.split("_")[0].astype(int) < 60]
        times = select[['problem', 'time']].groupby('problem').median()
        # if alg in {'ganak', 'd4'}:
        #     e1_times, e3_times = split_wmc(times)
        #     # out[f'{alg}_e1'] = process_time_measurements(e1_times)
        #     out[f'{alg}_e3'] = process_time_measurements(e3_times)
        # else:
        out[alg] = process_time_measurements(times)
    return out


# if __name__ == "__main__":
# ht = pd.read_csv(str(RESULTS_PATH.joinpath("seq_ht_results.csv")), dtype={'problem': str, 'algo': str, "time": np.float64, "wfomc": str})
# ht = pd.read_csv(str(RESULTS_PATH.joinpath("seq_to_results.csv")), dtype={'problem': str, 'algo': str, "time": np.float64, "wfomc": str})
ht = pd.read_csv(str(RESULTS_PATH.joinpath("comb_smaller.csv")), dtype={'problem': str, 'algo': str, "time": np.float64, "wfomc": str})
data = foo(ht)

fig, ax = plt.subplots()
for label, (xs, ys) in data.items():
    line, = ax.plot(xs, ys, marker='x')
    line.set_label(str(label))

ax.set_yscale('log', base=10)
ax.legend()
fig.show()


# ht_e3
data = {'inc':  
        (np.array([   1,    5,   10,   15,   20,   25,   30,
         35,   40,   45,   50]), 
         np.array([[0.11248173704370856], [0.0173521 ], [0.01744301],[0.01859813], [0.02184571], [0.0210789 ], [0.02495382], [0.028465  ], [0.03244657], [0.03672267], [0.03859934]])),
       'd4_e3': (np.array([ 1,  5, 10, 15, 20, 25]), np.array([[7.60122435e-02],
       [8.14094406e-02],
       [1.74403800e-01],
       [4.05455209e+00],
       [1.60691391e+02],
       [6.59535544e+03]])),
       'ganak_e3': (np.array([ 1,  5, 10, 15, 20, 25]), np.array([[1.64388660e-02],
       [4.15949600e-01],
       [1.35748916e+00],
       [3.57003044e+00],
       [1.99965036e+01],
       [5.37600360e+02]]))}

# to_e3
data = {'inc': (np.array([   1,    5,   10,   15,   20]), np.array([[1.04285287e-01],
       [1.11878021e-02],
       [1.23111160e-02],
       [1.29207500e-02],
       [1.58771490e-02]])),
       'd4_e3': (np.array([ 1,  5, 10]), np.array([[ 0.08027144],
       [ 0.09102683],
       [11.07617112]])),
       'ganak_e3': (np.array([ 1,  5, 10]), np.array([[7.14070699e-03],
       [5.97555159e-01],
       [1.00279055e+01]]))
       }

# to_e1
data = {'inc': (np.array([   1,  50,  100,  150,  200,  250,  300,
        350,  400,  450,  500,  550,  600,  650,  700,  750,  800,  850,
        900,  950, 1000]), np.array([[1.04285287e-01],
       [3.96666119e-02],
       [1.29109192e-01],
       [3.11106184e-01],
       [6.24314907e-01],
       [1.08257548e+00],
       [1.82055752e+00],
       [2.92282663e+00],
       [4.41337502e+00],
       [6.70655675e+00],
       [9.87348176e+00],
       [1.41769749e+01],
       [2.02000167e+01],
       [2.82114775e+01],
       [3.84738968e+01],
       [5.30975885e+01],
       [7.04133823e+01],
       [9.12541554e+01],
       [1.18175026e+02],
       [1.51421025e+02],
       [1.89496298e+02]])), 'd4_e1': (np.array([   1,   50,  100,  150,  200,  250,  300,  350,  400,  450,
        500,  550,  600,  650,  700,  750,  800,  850,  900,  950, 1000]), np.array([[ 0.08613718],
       [ 0.09566074],
       [ 0.12731311],
       [ 0.17117484],
       [ 0.2656964 ],
       [ 0.424989  ],
       [ 0.67541052],
       [ 1.03185161],
       [ 1.5633107 ],
       [ 2.29812105],
       [ 3.3259861 ],
       [ 4.66343942],
       [ 6.36439903],
       [ 8.49980692],
       [11.2382047 ],
       [14.44908837],
       [18.76536804],
       [23.79331239],
       [29.29521735],
       [36.18574453],
       [43.53956038]])), 'ganak_e1': (np.array([  1,  50, 100, 150, 200, 250]), np.array([[1.85237125e-02],
       [7.55463081e+00],
       [2.91184267e+01],
       [6.65037574e+01],
       [1.17885616e+02],
       [1.86812002e+02]]))}

# comb
data = {'inc2': (np.array([  7,   8,  23,  29,  31,  33,  39,  42,  45,  47,  53,  80,  82,
        96,  99, 102, 130, 137, 149, 175, 193, 231, 240, 243, 269, 284,
       292, 309]), np.array([[ 1.08873954],
       [ 5.84274255],
       [ 0.25641763],
       [ 0.51572988],
       [ 0.30684318],
       [ 0.72127697],
       [ 0.28592398],
       [ 0.29260571],
       [ 0.28236892],
       [ 0.1851528 ],
       [18.00183208],
       [ 0.38589683],
       [ 0.29996376],
       [ 0.3035502 ],
       [ 0.2066    ],
       [ 4.0235185 ],
       [20.1419387 ],
       [ 0.30331244],
       [ 0.24807895],
       [ 0.30178788],
       [ 0.20158835],
       [ 0.27063251],
       [24.15587663],
       [ 0.166296  ],
       [ 0.5331066 ],
       [ 0.1921652 ],
       [ 0.26718153],
       [ 0.2979462 ]])), 'd4': (np.array([  7,   8,  23,  29,  31,  33,  39,  42,  45,  47,  53,  80,  82,
        96,  99, 102, 130, 137, 149, 175, 193, 231, 240, 243, 269, 284,
       292, 309]), np.array([[4.91314801e-01],
       [4.51768017e+01],
       [2.00828247e+00],
       [1.74035201e-01],
       [8.88036760e-02],
       [2.97080344e+00],
       [3.29881972e+00],
       [4.88954619e+00],
       [7.79352491e-01],
       [8.09260481e-01],
       [4.54878105e+02],
       [8.72410140e-02],
       [2.06929615e-01],
       [1.46822865e-01],
       [8.35060570e-02],
       [3.04295130e-01],
       [2.74145038e+01],
       [9.32686115e+00],
       [5.67155667e+01],
       [6.86053015e-01],
       [1.40519261e+00],
       [6.30737111e+00],
       [8.22701004e+00],
       [8.69228108e-01],
       [1.58458096e+00],
       [6.04049719e+00],
       [2.37702752e-01],
       [1.05408364e-01]])), 'ganak': (np.array([  7,   8,  23,  29,  31,  33,  39,  42,  45,  47,  53,  80,  82,
        96,  99, 102, 130, 137, 149, 175, 193, 231, 240, 243, 269, 284,
       292, 309]), np.array([[1.77470689e+00],
       [5.35418302e+01],
       [8.58160272e+00],
       [2.36724482e-01],
       [3.00126800e-02],
       [1.30975040e+01],
       [1.32306959e+01],
       [9.05413247e+00],
       [4.08382151e+00],
       [5.94309419e+00],
       [8.52529744e+01],
       [2.27142207e+00],
       [3.02677139e+00],
       [3.10308767e+00],
       [3.97399110e-02],
       [3.47685239e-01],
       [1.88502373e+01],
       [1.77939050e+01],
       [4.85164061e+01],
       [7.20578559e+00],
       [8.37474093e+00],
       [1.77079352e+01],
       [2.41367396e+01],
       [7.16641492e+00],
       [9.70888218e+00],
       [1.40168855e+01],
       [2.68231707e+00],
       [3.50069321e+00]])), 'rec': (np.array([  7,  23,  29,  31,  39,  42,  45,  47,  80,  82,  96,  99, 137,
       149, 175, 193, 231, 243, 284, 292, 309]), np.array([[4.68227373e+01],
       [9.38613566e+00],
       [9.75482016e+00],
       [6.61044840e-01],
       [1.65450124e+03],
       [2.24001070e+01],
       [9.30613946e+00],
       [1.50814450e+02],
       [2.35651101e+00],
       [8.01613548e+02],
       [2.32798299e+00],
       [3.35467522e-01],
       [6.90321341e+03],
       [4.50276907e+03],
       [6.46515811e+00],
       [4.17936278e+00],
       [9.29229907e+00],
       [2.75065944e+00],
       [3.88578412e+02],
       [4.20586261e+00],
       [2.00463463e+02]])), 'inc': (np.array([ 31,  80,  96,  99, 243]), np.array([[0.95664797],
       [7.02892308],
       [6.7842355 ],
       [0.30428507],
       [4.53192096]]))}


d = dict()
for key, val in zip(data['inc'][0], data['inc'][1]):
    d[str(key)] = float(val)

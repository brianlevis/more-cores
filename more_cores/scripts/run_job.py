import sys

import dill

id_number, num_cores = sys.argv[1:3]

with open('data_{}.pkl'.format(id_number), 'rb') as fp:
    func, args_set = dill.load(fp)

results = [
    func(*args) for args in args_set
]

with open('results_{}.pkl'.format(id_number), 'wb') as fp:
    dill.dump(results, fp)

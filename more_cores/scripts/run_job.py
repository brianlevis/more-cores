import pickle
import sys
import dill
from pathos.pools import ProcessPool

id_number, num_cores = sys.argv[1:3]

with open('data_{}.pkl'.format(id_number), 'rb') as fp:
    func, args_set = dill.load(fp)

pool = ProcessPool(nodes=int(num_cores))
results = list(pool.imap(func, *zip(*args_set)))

# results = [
#     func(*args) for args in args_set
# ]

with open('results_{}.pkl'.format(id_number), 'wb') as fp:
    pickle.dump(results, fp)

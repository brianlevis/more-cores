import itertools
import math
import time
from functools import wraps

import dill


DELAY_TIME = 1.0


class Iterable(list):
    """A thin wrapper used to flag an argument list for parallel iteration."""
    def __init__(self, lst):
        super().__init__()
        self.extend(lst)


def parallel_for(cores, dynamic=False, recursive=False):
    def _parallel_for(func):
        """The main stuff- document this pls"""
        @wraps(func)
        def run_jobs(*args, **kwargs):
            args_set = expand_parameters(args)
            # Divide args among cores
            num_servers = len(cores.server_dicts)
            chunk_size = int(math.ceil(len(args_set) / num_servers))
            # Create a package of the function and args for each core
            print('Distributing jobs')
            for i, sd in enumerate(cores.server_dicts):
                data_file = '_more_cores_{}.pkl'.format(i)
                with open(data_file, 'wb') as f:
                    dill.dump((
                        func, args_set[chunk_size * i:chunk_size * (i + 1)]
                    ), f)
                cores.connect(i)
                cores.send_file(data_file, data_file)
                cmd = 'nohup bash run_job {0} {1} {2} > nohup_{1}.out &'.format(
                    cores.requirements['python'], i, sd['cores']
                )
                print('Sending', cmd)
                ssh_stdin, ssh_stdout, ssh_stderr = cores.send_command(cmd)
                print('Sent')
                for line in ssh_stdout.readlines():
                    print(line)
                for line in ssh_stderr.readlines():
                    print(line)
                cores.disconnect()
            # Wait for all jobs to complete
            remaining = list(range(num_servers))
            return_data = [None] * num_servers
            while len(remaining) > 0:
                for r in list(remaining):
                    time.sleep(DELAY_TIME)
                    print('checking', r)
                    # Check for existence of file
                    cores.connect(r)
                    if cores.is_job_complete():
                        remaining.remove(r)
                        # Get function return values
                        # TODO
                        pass
                    cores.disconnect()
            return return_data

        return run_jobs

    return _parallel_for


def expand_parameters(params):
    # Locate iterations
    iterable_indices = [
        i for i, arg in enumerate(params) if type(arg) == Iterable
    ]
    # Compute the set product of all iterations
    parameter_combinations = itertools.product(*[
        params[i] for i in iterable_indices
    ])
    # Generate all parameter sets
    parameter_sets = []
    for p_c in parameter_combinations:
        new_set = list(params)
        for i, ii in enumerate(iterable_indices):
            new_set[ii] = p_c[i]
        parameter_sets.append(new_set)
    return parameter_sets

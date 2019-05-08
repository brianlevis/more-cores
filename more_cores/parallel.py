import itertools
import math
import os
import pickle
import time
from functools import wraps

import dill


DELAY_TIME = 5.0


class Iterable(list):
    """A thin wrapper used to flag an argument list for parallel iteration."""
    def __init__(self, lst):
        super().__init__()
        self.extend(lst)


class Timer:
    def __init__(self):
        self.timer = {
            'distribution': [],
            'run_and_check': [],
            'collection': [],
        }
        self.running_task = None
        self.time = None

    def __str__(self):
        output = []
        for task in self.timer:
            times = self.timer[task]
            output.append('{}: {}'.format(task, sum(times)))
            if len(times) > 1:
                output.append('mean: {}, min: {}, max: {}'.format(
                    sum(times) / len(times), min(times), max(times)
                ))
        return '\n'.join(output)

    def start(self, running_task):
        self.running_task = running_task
        self.time = time.time()

    def record(self):
        self.timer[self.running_task].append(time.time() - self.time)


def parallel_for(cores, dynamic=False):
    def _parallel_for(func):
        """The main stuff- document this pls"""
        @wraps(func)
        def run_jobs(*args, **kwargs):
            timer = Timer()
            args_set = expand_parameters(args)
            # Divide args among cores
            num_servers = len(cores.server_dicts)
            chunk_size = int(len(args_set) / num_servers)
            # Create a package of the function and args for each core
            print('Distributing jobs')
            for i, sd in enumerate(cores.server_dicts):
                timer.start('distribution')
                data_file = '_more_cores_{}.pkl'.format(i)
                with open(data_file, 'wb') as f:
                    print(chunk_size * (i + 1) - chunk_size * i)
                    obj = (
                        func, args_set[chunk_size * i:chunk_size * (i + 1)]
                    )
                    # print(dill.detect.baditems(func))
                    # print(dill.detect.badobjects(func))
                    # print(dill.detect.badtypes(func))
                    dill.dump(obj, f, recurse=True)
                cores.connect(i)
                cores.send_file(data_file, 'data_{}.pkl'.format(i))
                os.remove(data_file)
                # cmd = 'nohup bash run_job {0} {1} {2}'.format(
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
                timer.record()
            # Wait for all jobs to complete
            remaining = list(range(num_servers))
            return_data = [None] * len(args_set)
            timer.start('run_and_check')
            while len(remaining) > 0:
                for r in list(remaining):
                    time.sleep(DELAY_TIME)
                    print('checking', r)
                    # Check for existence of file
                    cores.connect(r)
                    if cores.is_job_complete():
                        timer.record()
                        timer.start('collection')
                        remaining.remove(r)
                        # Get function return values
                        results_file = 'results_{}.pkl'.format(r)
                        cores.get_file(results_file, results_file)
                        with open(results_file, 'rb') as f:
                            for i, result in enumerate(pickle.load(f)):
                                return_data[chunk_size * r + i] = result
                        timer.record()
                        timer.start('run_and_check')
                    cores.disconnect()
            timer.record()
            print(timer)
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

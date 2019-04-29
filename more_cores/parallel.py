import itertools

import dill


class Iterable(list):
    """A thin wrapper used to flag an argument list for parallel iteration."""
    def __init__(self, lst):
        super().__init__()
        self.extend(lst)


def parallel_for(func, dynamic=False):
    # Dump file
    with open('func.pkl', 'wb') as f:
        dill.dump(func, f)

    def inner1(*args, **kwargs):
        iterable_indices = [
            i for i, arg in enumerate(args) if type(arg) == Iterable
        ]
        parameter_combinations = itertools.product([
            args[i] for i in iterable_indices
        ])
        print(image_name_0, image_name_1, num_images, image_range)
        func(*args, **kwargs)

    return inner1

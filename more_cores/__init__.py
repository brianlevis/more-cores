from more_cores.cores import Cores, make_server_dict, make_requirements
from more_cores.parallel import parallel_for

name = "more_cores"

hive = Cores(
    [make_server_dict('hive21.cs.berkeley.edu', 'cs199-dlq')],
    make_requirements(['tensorflow'])
)


@parallel_for(hive)
def asdf(x, y, z):
    return x


asdf([1,2], 3, 4)

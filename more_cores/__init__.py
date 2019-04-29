from more_cores.cores import Cores, make_server_dict, make_requirements

name = "more_cores"

hive = Cores(
    make_server_dict('hive21.cs.berkeley.edu', 'cs199-dlq'),
    make_requirements(['tensorflow'])
)

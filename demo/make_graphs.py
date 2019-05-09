from itertools import groupby
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress


n = np.array([1, 2, 3, 4, 5, 6])
# Strong scaling
s = np.array([
    # distr, run, collection, total
    [0.5918669700622559, 529.6803040504456, 9.309041976928711, 8.99303198258082],
    [1.8108410835266113, 270.1959412097931, 15.396013259887695, 4.790057881673177],
    [2.0383732318878174, 188.6463587284088, 15.88695502281189, 3.442866106828054],
    [2.777017116546631, 158.66964769363403, 9.326416969299316, 2.846228917439779],
    [3.4988534450531006, 116.17787265777588, 16.39770245552063, 2.267911982536316],
    [6.474611043930054, 104.0037693977356, 13.058543682098389, 2.0589545647303265],
])
# Weak scaling
w = np.array([
    # distr, run, collection, total
    [0.5480248928070068, 219.1293888092041, 5.413635015487671, 3.7515245000521342],
    [1.6725523471832275, 217.75201082229614, 7.34630274772644, 3.779518397649129],
    [2.059065103530884, 209.39180660247803, 11.491988182067871, 3.7157195170720416],
    [2.629925012588501, 256.28443479537964, 16.01390767097473, 4.582146282990774],
    [3.8133208751678467, 249.47303009033203, 18.254082679748535, 4.525681483745575],
    [4.895831108093262, 434.50403213500977, 22.518120765686035, 7.698641033967336],
])

plt.clf()
plt.figure(figsize=(8, 8))
plt.plot(n, s[:, 0], 'o', linestyle=None, label='1. Distribution')
plt.plot(n, s[:, 1], 'o', linestyle=None, label='2. Run')
plt.plot(n, s[:, 2], 'o', linestyle=None, label='3. Collection')
plt.plot(n, s[:, 3] * 60, 'o', linestyle=None, label='Total')
plt.legend()
plt.xlabel('Machines')
plt.ylabel('Computation Time (s)')
# plt.gca().set_aspect('equal', adjustable='box')
plt.title('Strong Scaling (4 cores per machine)')
# plt.tight_layout()
plt.savefig('strong_scaling.png', bbox_inches='tight', dpi=300)

plt.clf()
plt.figure(figsize=(8, 8))
plt.plot(n, w[:, 0], 'o', linestyle=None, label='1. Distribution')
plt.plot(n, w[:, 1], 'o', linestyle=None, label='2. Run')
plt.plot(n, w[:, 2], 'o', linestyle=None, label='3. Collection')
plt.plot(n, w[:, 3] * 60, 'o', linestyle=None, label='Total')
plt.legend()
plt.xlabel('Machines (x1), Frames (x10)')
plt.ylabel('Computation Time (s)')
# plt.gca().set_aspect('equal', adjustable='box')
plt.title('Weak Scaling (4 cores per machine)')
# plt.tight_layout()
plt.savefig('weak_scaling.png', bbox_inches='tight', dpi=300)

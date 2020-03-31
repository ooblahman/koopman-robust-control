import torch
import hickle as hkl
import random
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import matplotlib
from scipy.integrate import odeint, ode
# matplotlib.use('tkagg')

import systems.duffing as duffing
from sampler.features import *
from sampler.operators import *
from experiments.duffing_mpc import mpc_loop
from experiments.duffing_plot import plot_perturbed, plot_posterior

device = 'cuda' if torch.cuda.is_available() else 'cpu'
set_seed(9001)
# torch.autograd.set_detect_anomaly(True)

# Select models
data = hkl.load('saved/duffing_controlled_nominal.hkl')
P, B = torch.from_numpy(data['P']).float(), torch.from_numpy(data['B']).float()
dt = data['dt']
print('Using dt:', dt)

data = hkl.load('saved/duffing_uncertainty_set.hkl')
Ps = [torch.from_numpy(s).float() for s in data['samples']]
posterior = data['posterior']
trajectories = data['trajectories']
beta = data['beta']

plot_perturbed(trajectories, 2, 6)
plot_posterior(posterior, beta)

# # xR = lambda t: torch.full(t.shape, 0.)
# xR = lambda t: torch.sign(torch.cos(t/4))
# # xR = lambda t: torch.floor(t/5)/5
# cost = lambda u, x, t: ((x[0] - xR(t))**2).sum()
# h = 50
# x0, y0 = .5, 0.


# hist_t, hist_u, hist_x = mpc_loop(x0, y0, [P], B, obs, cost, h, dt, 2000)

# results = {
# 	'dt': dt,
# 	't': hist_t,
# 	'u': hist_u,
# 	'x': hist_x,
# 	'r': xR(torch.Tensor(hist_t)).numpy(),
# }
# print('Saving...')
# hkl.dump(results, 'saved/duffing_mpc.hkl')

plt.show()

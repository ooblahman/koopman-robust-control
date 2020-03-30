import torch
import hickle as hkl
import random
import itertools
import numpy as np

from sampler.features import *
from sampler.kernel import *
from sampler.operators import *
from sampler.utils import *
from sampler.dynamics import *
import systems.duffing as duffing

device = 'cuda' if torch.cuda.is_available() else 'cpu'
# torch.autograd.set_detect_anomaly(True)

set_seed(9001)

data = hkl.load('saved/duffing_controlled_nominal.hkl')
P, B = torch.from_numpy(data['P']).float(), torch.from_numpy(data['B']).float()

# Init features
p, d, k = 5, 2, 15
obs = PolynomialObservable(p, d, k)

# Sample dynamics
beta = 10
step = 3e-5
leapfrog = 200
n_samples = 256
n_ics = 32
ic_step = 1e-5
T = 100

samples, posterior = perturb(n_samples, P, beta, method='kernel', n_ics=n_ics, hmc_step=step, hmc_leapfrog=leapfrog, ic_step=ic_step, kernel_T=T)

# Collect trajectories 
print('Saving trajectories...')
n_trajectories = 24
n_ics = 12
t = 800
trajectories = [sample_2d_dynamics(P, obs, t, (-2,2), (-2,2), n_ics, n_ics) for P in random.choices(samples, k=n_trajectories)]

results = {
	'step': step,
	'beta': beta,
	'leapfrog': leapfrog,
	'T': T,
	'nominal': P.numpy(),
	'posterior': posterior,
	'samples': [s.numpy() for s in samples],
	'trajectories': trajectories,
}
print('Saving..')
hkl.dump(results, 'saved/duffing_uncertainty_set.hkl')
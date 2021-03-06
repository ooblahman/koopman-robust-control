import torch
import hickle as hkl
import random

import sampler.reflections as reflections
from sampler.features import *
from sampler.kernel import *
from sampler.operators import *
from sampler.utils import *
from sampler.ugen import *
import systems.duffing as duffing

device = 'cuda' if torch.cuda.is_available() else 'cpu'
# torch.autograd.set_detect_anomaly(True)

set_seed(9001)

# Init features
p, d, k = 5, 2, 15
obs = PolynomialObservable(p, d, k)

# Init data 
t_max = 400
n_per = 8000
n_init = 12
x0s = np.linspace(-2.0, 2.0, n_init)
xdot0s = np.linspace(-2.0, 2.0, n_init)
X, Y = [], []
for x0 in x0s:
	for xdot0 in xdot0s:
		# Unforced duffing equation
		Xi, Yi = duffing.dataset(t_max, n_per, gamma=0.0, x0=x0, xdot0=xdot0)
		X.append(Xi)
		Y.append(Yi)
X, Y = torch.cat(tuple(X), axis=1), torch.cat(tuple(Y), axis=1)

X, Y = X.to(device), Y.to(device)
PsiX, PsiY = obs(X), obs(Y)

# Nominal operator
nominal = dmd(PsiX, PsiY)
nominal = nominal.to(device)
assert not torch.isnan(nominal).any().item()

# Sample dynamics

# method = 'baseline'
# method = 'kernel'
# method = 'constrained_kernel'
method = 'discounted_kernel'

beta = 5
step = 5e-5
leapfrog = 200
n_samples = 2000
n_ics = 200
ic_step = 1e-5
T = 80
L = 0.1

if method == 'baseline':
	samples, posterior = perturb(n_samples, nominal, beta, method='euclidean', n_ics=n_ics, hmc_step=step, hmc_leapfrog=leapfrog, ic_step=ic_step)
elif method == 'kernel':
	samples, posterior = perturb(n_samples, nominal, beta, method='kernel', n_ics=n_ics, hmc_step=step, hmc_leapfrog=leapfrog, ic_step=ic_step, kernel_T=T)
elif method == 'constrained_kernel':
	samples, posterior = perturb(n_samples, nominal, beta, method='kernel', n_ics=n_ics, hmc_step=step, hmc_leapfrog=leapfrog, ic_step=ic_step, kernel_T=T, use_spectral_constraint=True)
elif method == 'discounted_kernel':
	samples, posterior = perturb(n_samples, nominal, beta, method='kernel', n_ics=n_ics, hmc_step=step, hmc_leapfrog=leapfrog, ic_step=ic_step, kernel_T=T, kernel_L=L)

print('Saving trajectories...')
n_trajectories = 12
n_ics = 12
t = 800
trajectories = [sample_2d_dynamics(P, obs, t, (-2,2), (-2,2), n_ics, n_ics) for P in random.choices(samples, k=n_trajectories)]

results = {
	'method': method,
	'step': step,
	'beta': beta,
	'nominal': nominal.numpy(),
	'posterior': posterior,
	'samples': [s.numpy() for s in samples],
	'trajectories': trajectories,
}
print('Saving..')
hkl.dump(results, f'saved/duffing_{method}.hkl')

import torch
import numpy as np
import hickle as hkl

import sampler.reflections as reflections
from sampler.utils import *
from sampler.kernel import *
from sampler.ugen import *
import systems.lti2x2 as lti2x2

set_seed(9001)
device = 'cuda' if torch.cuda.is_available() else 'cpu'
# torch.autograd.set_detect_anomaly(True)

# method = 'baseline'
# method = 'kernel'
# method = 'constrained_kernel'
method = 'discounted_kernel'

beta = 5
step = 1e-4
leapfrog = 100
n_samples = 1000
n_ics = 50
ic_step = 3e-5
T = 80

results = {}

if method in ['kernel', 'constrained_kernel']:
	systems = lti2x2.semistable_systems
else:
	systems = lti2x2.systems

for i, (name, A) in enumerate(systems.items()):

	nominal = torch.from_numpy(diff_to_transferop(A)).float()
	
	if method == 'baseline':
		samples, posterior = perturb(n_samples, nominal, beta, method='euclidean', n_ics=n_ics, ic_step=ic_step, hmc_step=step)
	elif method == 'kernel':
		samples, posterior = perturb(n_samples, nominal, beta, method='kernel', n_ics=n_ics, ic_step=ic_step, hmc_step=step, kernel_T=T)
	elif method == 'constrained_kernel':
		samples, posterior = perturb(n_samples, nominal, beta, method='kernel', n_ics=n_ics, ic_step=ic_step, hmc_step=step, kernel_T=T, use_spectral_constraint=True)
	elif method == 'discounted_kernel':
		L = max(0, 2*np.log(spectral_radius(nominal).item()))
		samples, posterior = perturb(n_samples, nominal, beta, method='kernel', n_ics=n_ics, ic_step=ic_step, hmc_step=step, kernel_T=T, kernel_L=L)

	samples = [transferop_to_diff(s.numpy()) for s in samples]

	results[name] = {
		'method': method,
		'nominal': A,
		'posterior': posterior,
		'samples': samples,
		'step': step,
		'beta': beta,
	}

print('Saving..')
hkl.dump(results, f'saved/2x2_{method}.hkl')

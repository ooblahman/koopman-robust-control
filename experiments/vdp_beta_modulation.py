import torch
import matplotlib.pyplot as plt

from sampler.features import *
from sampler.kernel import *
from sampler.operators import *
from sampler.utils import *
from sampler.ugen import perturb
import systems.vdp as vdp

device = 'cuda' if torch.cuda.is_available() else 'cpu'
# torch.autograd.set_detect_anomaly(True)

set_seed(9001)

# Init features
p, d, k = 4, 2, 8
obs = PolynomialObservable(p, d, k)

# Init data
mu = 3.0
X, Y = vdp.dataset(mu, n=16000, b=40, skip=3500) # start on limit cycle
X, Y = X.to(device), Y.to(device)
PsiX, PsiY = obs(X), obs(Y)

# Initialize kernel
d, m, T = PsiX.shape[0], 2, 20
K = PFKernel(device, d, m, T)

# Nominal operator
P0 = dmd(PsiX, PsiY)
P0 = P0.to(device)
assert not torch.isnan(P0).any().item()

# Sample dynamics

baseline = False
dist_func = euclidean_matrix_kernel if baseline else (lambda x, y: K(x, y, normalize=True)) 

rms_dist = []

for beta in np.linspace(1, 100, 50):

	samples = perturb(
		30, P0, dist_func, beta,  
		sp_div=(1.0, 1.0), # leave spectral gap wide to purely determine effect of `beta`
		hmc_step=5e-4,
		hmc_leapfrog=25,
	)

	rms = np.array([dist_func(P0, P).item() for P in samples])
	rms = np.sqrt(np.mean(rms ** 2))
	rms_dist.append([beta, rms])

rms_dist = np.array(rms_dist)

plt.figure()
plt.plot(rms_dist[:,0], rms_dist[:, 1])

plt.show()


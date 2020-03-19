from typing import Callable
from collections import OrderedDict
import numpy as np
import random
import torch
import matplotlib.pyplot as plt

def set_seed(seed: int):
	random.seed(seed)
	np.random.seed(seed)
	torch.manual_seed(seed)

def zip_with(X: tuple, Y: tuple, f: Callable):
	return tuple(f(x,y) for (x,y) in zip(X, Y))

def spectral_radius(A: torch.Tensor, eps=None, n_iter=None):
	if eps is None and n_iter is None:
		# return _sp_radius_conv(A, 1e-4)
		return _sp_radius_niter(A, 1000)
	elif eps is not None:
		return _sp_radius_conv(A, eps)
	elif n_iter is not None:
		return _sp_radius_niter(A, n_iter)

def _sp_radius_conv(A: torch.Tensor, eps: float):
	v = torch.ones((A.shape[0], 1), device=A.device)
	v_new = v.clone()
	ev = v.t()@A@v
	ev_new = ev.clone()
	while (A@v_new - ev_new*v_new).norm() > eps:
		v = v_new
		ev = ev_new
		v_new = A@v
		v_new = v_new / v_new.norm()
		ev_new = v_new.t()@A@v_new
	return ev_new

def _sp_radius_niter(A: torch.Tensor, n_iter: int):
	v = torch.ones((A.shape[0], 1), device=A.device)
	for _ in range(n_iter):
		v = A@v
		v = v / v.norm()
	ev = v.t()@A@v
	return ev

def deduped_legend():
	handles, labels = plt.gca().get_legend_handles_labels()
	by_label = OrderedDict(zip(labels, handles))
	plt.legend(by_label.values(), by_label.keys())

def euclidean_matrix_kernel(A: torch.Tensor, B: torch.Tensor):
	return torch.sqrt((1 - torch.trace(torch.mm(A.t(), B)).pow(2) / (torch.trace(torch.mm(A.t(), A)) * torch.trace(torch.mm(B.t(), B)))).clamp(1e-8))

def zero_if_nan(x: torch.Tensor):
	return torch.zeros_like(x, device=x.device) if torch.isnan(x).any() else x

def is_semistable(P: torch.Tensor, eps=1e-2):
	return spectral_radius(P).item() <= 1.0 + eps

def plot_flow_field(ax, f, u_range, v_range, n_grid=100):
    """
	Credit: http://be150.caltech.edu/2017/handouts/dynamical_systems_approaches.html
    Plots the flow field of 2x2 system.
    
    Parameters
    ----------
    ax : Matplotlib Axis instance
        Axis on which to make the plot
    f : function for form f(y, t, *args)
        The right-hand-side of the dynamical system.
        Must return a 2-array.
    u_range : array_like, shape (2,)
        Range of values for u-axis.
    v_range : array_like, shape (2,)
        Range of values for v-axis.
    args : tuple, default ()
        Additional arguments to be passed to f
    n_grid : int, default 100
        Number of grid points to use in computing
        derivatives on phase portrait.

    """
    
    # Set up u,v space
    u = np.linspace(u_range[0], u_range[1], n_grid)
    v = np.linspace(v_range[0], v_range[1], n_grid)
    uu, vv = np.meshgrid(u, v)

    # Compute derivatives
    u_vel = np.empty_like(uu)
    v_vel = np.empty_like(vv)
    for i in range(uu.shape[0]):
        for j in range(uu.shape[1]):
            [[u_vel[i,j]], [v_vel[i,j]]] = f(np.array([[uu[i,j]], [vv[i,j]]]))

    # Compute speed
    speed = np.sqrt(u_vel**2 + v_vel**2)

    # Make linewidths proportional to speed,
    # with minimal line width of 0.5 and max of 3
    lw = 0.5 + 2.5 * speed / speed.max()

    # Make stream plot
    ax.streamplot(uu, vv, u_vel, v_vel, linewidth=lw, arrowsize=1.2, 
                  density=1, color='thistle')

    return ax

'''
Tests
'''
if __name__ == '__main__':
	set_seed(9001)
	device = 'cuda' if torch.cuda.is_available() else 'cpu'

	# Power iteration test
	for _ in range(1000):
		d = 100
		A = torch.randn((d, d), device=device)
		e = np.random.uniform(0.1, 1.10)
		L = torch.linspace(e, 0.01, d, device=device)
		P = torch.mm(torch.mm(A, torch.diag(L)), torch.pinverse(A))

		np_e_max = np.abs(np.linalg.eigvals(P.cpu().numpy())).max()
		pwr_e_max = spectral_radius(P).item()
		print('True:', e, 'numpy:', np_e_max, 'pwr_iter:', pwr_e_max)
		# assert np.abs(np_e_max - pwr_e_max) <= prec
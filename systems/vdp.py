from scipy import linspace
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt
import torch

def system(mu: float):
	return lambda t, z: [z[1], mu*(1-z[0]**2)*z[1] - z[0]]

def dataset(mu: float, a=0, b=10, n=500, skip=0):
	t = linspace(a, b, n)
	sol = solve_ivp(system(mu), [a, b], [1, 0], t_eval=t)
	X, Y = sol.y[:, skip:-1], sol.y[:, skip+1:] 
	return torch.from_numpy(X).float(), torch.from_numpy(Y).float()

if __name__ == '__main__':
	mu = 3

	X, Y = dataset(mu, b=20, n=8000, skip=3500)
	print(X.shape, Y.shape)
	plt.figure(figsize=(8,8))
	plt.plot(X[0], X[1])
	plt.plot([X[0][0]], [X[1][0]], marker='o', color='red')
	plt.show()
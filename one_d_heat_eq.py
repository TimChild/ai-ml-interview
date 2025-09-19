# 1-D rod, constant properties, explicit Euler.
# u_t = alpha * u_xx  on x in [0, L]
# Dirichlet BC: u(0,t)=T_left, u(L,t)=T_right

import numpy as np


def solve_heat_explicit(
    nx=51, nt=2000, L=1.0, alpha=1e-4, dt=0.01, T_left=400.0, T_right=300.0, T_init=300.0
):
    dx = L / (nx - 1)
    r = alpha * dt / (dx * dx)  # stability requires r <= 0.5 for this scheme
    u = np.full(nx, T_init, dtype=float)
    u[0], u[-1] = T_left, T_right

    for _ in range(nt):
        u_new = u.copy()
        for i in range(1, nx - 1):
            u_new[i] = u[i] + r * (u[i - 1] - 2 * u[i] + u[i + 1])
        u_new[0], u_new[-1] = T_left, T_right
        u = u_new
    return u


if __name__ == "__main__":
    u_final = solve_heat_explicit()
    print(u_final[:5], "...", u_final[-5:])

"""P74 iLQR, DDP, SQP, and local trajectory-optimization primitives."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

import numpy as np


@dataclass(frozen=True)
class QDerivatives:
    q_x: np.ndarray
    q_u: np.ndarray
    q_xx: np.ndarray
    q_ux: np.ndarray
    q_uu: np.ndarray


def ilqr_q_derivatives(f_x: Sequence, f_u: Sequence, l_x: Sequence, l_u: Sequence, l_xx: Sequence, l_ux: Sequence, l_uu: Sequence, value_x: Sequence, value_xx: Sequence) -> QDerivatives:
    fx, fu = np.asarray(f_x, dtype=np.float64), np.asarray(f_u, dtype=np.float64)
    lx, lu = np.asarray(l_x, dtype=np.float64), np.asarray(l_u, dtype=np.float64)
    lxx, lux, luu = np.asarray(l_xx, dtype=np.float64), np.asarray(l_ux, dtype=np.float64), np.asarray(l_uu, dtype=np.float64)
    vx, vxx = np.asarray(value_x, dtype=np.float64), np.asarray(value_xx, dtype=np.float64)
    if fx.ndim != 2 or fu.ndim != 2 or fx.shape[0] != vx.size or fu.shape[0] != vx.size or lx.shape != (fx.shape[1],) or lu.shape != (fu.shape[1],) or lxx.shape != (fx.shape[1], fx.shape[1]) or lux.shape != (fu.shape[1], fx.shape[1]) or luu.shape != (fu.shape[1], fu.shape[1]) or vxx.shape != (vx.size, vx.size):
        raise ValueError("iLQR derivative shapes are invalid")
    return QDerivatives(lx + fx.T @ vx, lu + fu.T @ vx, lxx + fx.T @ vxx @ fx, lux + fu.T @ vxx @ fx, luu + fu.T @ vxx @ fu)


def add_ddp_dynamics_curvature(q: QDerivatives, value_x: Sequence[float], f_xx: Sequence, f_ux: Sequence, f_uu: Sequence) -> QDerivatives:
    vx = np.asarray(value_x, dtype=np.float64)
    fxx, fux, fuu = np.asarray(f_xx, dtype=np.float64), np.asarray(f_ux, dtype=np.float64), np.asarray(f_uu, dtype=np.float64)
    if fxx.shape[0] != vx.size or fux.shape[0] != vx.size or fuu.shape[0] != vx.size or fxx.shape[1:] != q.q_xx.shape or fux.shape[1:] != q.q_ux.shape or fuu.shape[1:] != q.q_uu.shape:
        raise ValueError("DDP curvature shapes are invalid")
    return QDerivatives(q.q_x, q.q_u, q.q_xx + np.tensordot(vx, fxx, axes=1), q.q_ux + np.tensordot(vx, fux, axes=1), q.q_uu + np.tensordot(vx, fuu, axes=1))


def backward_control_law(q_u: Sequence[float], q_uu: Sequence, q_ux: Sequence, *, regularization: float = 0.0) -> tuple[np.ndarray, np.ndarray, float]:
    gradient = np.asarray(q_u, dtype=np.float64)
    hessian = np.asarray(q_uu, dtype=np.float64)
    cross = np.asarray(q_ux, dtype=np.float64)
    if hessian.shape != (gradient.size, gradient.size) or cross.shape[0] != gradient.size or regularization < 0.0:
        raise ValueError("backward pass inputs are invalid")
    regularized = 0.5 * (hessian + hessian.T) + regularization * np.eye(gradient.size)
    minimum = float(np.linalg.eigvalsh(regularized)[0])
    if minimum <= 0.0:
        raise ValueError("regularized control Hessian is not positive definite")
    return -np.linalg.solve(regularized, gradient), -np.linalg.solve(regularized, cross), minimum


def value_derivative_update(q: QDerivatives, feedforward: Sequence[float], feedback: Sequence) -> tuple[np.ndarray, np.ndarray]:
    k = np.asarray(feedforward, dtype=np.float64)
    gain = np.asarray(feedback, dtype=np.float64)
    if k.shape != q.q_u.shape or gain.shape != q.q_ux.shape:
        raise ValueError("value update inputs are invalid")
    value_x = q.q_x + gain.T @ q.q_uu @ k + gain.T @ q.q_u + q.q_ux.T @ k
    value_xx = q.q_xx + gain.T @ q.q_uu @ gain + gain.T @ q.q_ux + q.q_ux.T @ gain
    return value_x, 0.5 * (value_xx + value_xx.T)


def expected_cost_change(q_u_steps: Sequence, q_uu_steps: Sequence, feedforward_steps: Sequence, step_size: float) -> float:
    q_u = np.asarray(q_u_steps, dtype=np.float64)
    q_uu = np.asarray(q_uu_steps, dtype=np.float64)
    feedforward = np.asarray(feedforward_steps, dtype=np.float64)
    if q_u.shape != feedforward.shape or q_uu.shape != (q_u.shape[0], q_u.shape[1], q_u.shape[1]) or not 0.0 <= step_size <= 1.0:
        raise ValueError("expected reduction inputs are invalid")
    linear = sum(float(k @ g) for k, g in zip(feedforward, q_u, strict=True))
    quadratic = 0.5 * sum(float(k @ h @ k) for k, h in zip(feedforward, q_uu, strict=True))
    return step_size * linear + step_size**2 * quadratic


def finite_difference_jacobians(dynamics: Callable[[np.ndarray, np.ndarray], np.ndarray], state: Sequence[float], control: Sequence[float], *, epsilon: float = 1e-6) -> tuple[np.ndarray, np.ndarray]:
    x, u = np.asarray(state, dtype=np.float64), np.asarray(control, dtype=np.float64)
    base = np.asarray(dynamics(x, u), dtype=np.float64)
    if x.ndim != 1 or u.ndim != 1 or base.ndim != 1 or epsilon <= 0.0:
        raise ValueError("finite-difference inputs are invalid")
    fx, fu = np.empty((base.size, x.size)), np.empty((base.size, u.size))
    for index in range(x.size):
        direction = np.zeros_like(x)
        direction[index] = epsilon
        fx[:, index] = (dynamics(x + direction, u) - dynamics(x - direction, u)) / (2.0 * epsilon)
    for index in range(u.size):
        direction = np.zeros_like(u)
        direction[index] = epsilon
        fu[:, index] = (dynamics(x, u + direction) - dynamics(x, u - direction)) / (2.0 * epsilon)
    return fx, fu


def sqp_kkt_residual(hessian: Sequence, gradient: Sequence[float], constraint_matrix: Sequence, constraint_residual: Sequence[float], step: Sequence[float], multipliers: Sequence[float]) -> tuple[float, float]:
    h, g, a, c, delta, dual = (np.asarray(value, dtype=np.float64) for value in (hessian, gradient, constraint_matrix, constraint_residual, step, multipliers))
    if h.shape != (g.size, g.size) or a.ndim != 2 or a.shape[1] != g.size or c.shape != (a.shape[0],) or delta.shape != g.shape or dual.shape != c.shape:
        raise ValueError("SQP KKT inputs are invalid")
    stationarity = h @ delta + g + a.T @ dual
    feasibility = a @ delta + c
    return float(np.linalg.norm(stationarity)), float(np.linalg.norm(feasibility))

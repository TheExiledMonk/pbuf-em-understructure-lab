"""Deterministic, explicitly new EMX049 geometry/source primitive."""
from __future__ import annotations

import hashlib
import numpy as np

N = 11
DT = 0.04
STEPS = 180
NORM = 0.013259145044039137  # Frozen scale; it is not historical provenance.
DIRECTIONS = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))


def sha(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def geometry() -> np.ndarray:
    return np.asarray(DIRECTIONS, dtype=np.float64)


def shift(a: np.ndarray, direction: tuple[int, int, int]) -> np.ndarray:
    return np.roll(a, direction, axis=(0, 1, 2))


def normalize(u: np.ndarray) -> np.ndarray:
    return u * (NORM / np.sqrt(np.sum(u * u)))


def source(shape: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return initial displacement, momentum, and zero per-step source history."""
    u = np.zeros((N, N, N, 3), dtype=np.float64)
    # Off-centre location makes the predeclared mirror a real parity variant.
    u[(N // 2 + 1) % N, N // 2, N // 2, 0] = 1.0
    if shape == "ELONGATED":
        u = shift(u, (-1, 0, 0)) + u + shift(u, (1, 0, 0))
    elif shape == "MIRRORED":
        u = np.flip(u, axis=0).copy()
    elif shape == "SPLIT":
        u = shift(u, (-2, 0, 0)) + shift(u, (2, 0, 0))
    elif shape != "COMPACT":
        raise ValueError(shape)
    return normalize(u), np.zeros_like(u), np.zeros((STEPS + 1, N, N, N, 3), dtype=np.float64)


def force(u: np.ndarray) -> tuple[np.ndarray, float]:
    total = np.zeros_like(u)
    minimum = float("inf")
    for d in DIRECTIONS:
        r = geometry()[DIRECTIONS.index(d)] + shift(u, d) - u
        length = np.linalg.norm(r, axis=-1)
        minimum = min(minimum, float(length.min()))
        epsilon = length - 1.0
        sigma = epsilon / (1.0 - epsilon * epsilon)
        total += sigma[..., None] * r / length[..., None]
    return total, minimum


def history(u: np.ndarray, p: np.ndarray, source_history: np.ndarray, dt: float = DT, steps: int = STEPS) -> tuple[np.ndarray, float]:
    values, min_distance = [], float("inf")
    for t in range(steps + 1):
        values.append(float(np.sqrt(np.sum(u * u + p * p))))
        if t == steps:
            break
        f, d = force(u)
        min_distance = min(min_distance, d)
        p = p + 0.5 * dt * (f + source_history[t])
        u = u + dt * p
        f, d = force(u)
        min_distance = min(min_distance, d)
        p = p + 0.5 * dt * (f + source_history[t + 1])
    a = np.asarray(values)
    return np.array([a[0], a[-1], a.min(), a.max()]), min_distance


def local_history(u: np.ndarray, p: np.ndarray, dt: float = DT, steps: int = STEPS) -> np.ndarray:
    values = []
    for t in range(steps + 1):
        values.append(float(np.sqrt(np.sum(u * u + p * p))))
        if t == steps:
            break
        f = sum(shift(u, d) - u for d in DIRECTIONS)
        p = p + 0.5 * dt * f
        u = u + dt * p
        f = sum(shift(u, d) - u for d in DIRECTIONS)
        p = p + 0.5 * dt * f
    a = np.asarray(values)
    return np.array([a[0], a[-1], a.min(), a.max()])

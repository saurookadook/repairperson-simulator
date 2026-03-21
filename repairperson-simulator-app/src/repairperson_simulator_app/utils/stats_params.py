from __future__ import annotations

import math


def mu_and_sigma_from_median_and_cv(median: float, cv: float):
    """Convert median and coefficient of variation (CV) to mu and sigma for a lognormal distribution."""
    if median <= 0:
        raise ValueError("Median must be greater than 0.")
    if cv < 0:
        raise ValueError("Coefficient of variation (CV) must be non-negative.")

    sigma_squared = math.log(cv**2 + 1)
    sigma = math.sqrt(sigma_squared)
    mu = math.log(median)
    return mu, sigma


def mu_and_sigma_from_p50_and_p90(p50: float, p90: float):
    """Fit lognormal parameters using the 50th an 90th percentiles."""
    if p50 <= 0 or p90 <= 0:
        raise ValueError("Percentiles must be greater than 0.")
    if p90 <= p50:
        raise ValueError("p90 must be greater than p50.")

    z90 = 1.2815515655446004  # Phi^{-1}(0.9)
    ln50 = math.log(p50)
    ln90 = math.log(p90)
    sigma = (ln90 - ln50) / z90
    mu = ln50
    return mu, sigma

"""Fit a local Hall/current -> gap model and validate on a separate CSV.

CSV columns: gap_mm,hall1,hall2,current_a (hall2 optional with --hall-sensors 1).
Never enables hardware or rewrites
firmware. Holdout rows must come from independent sweeps, not duplicate samples.
"""
import argparse
import csv
from pathlib import Path
import numpy as np


def load(path, hall_sensors=2):
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    a = np.array([[float(r[k]) if k != "hall2" or hall_sensors == 2 else 0.0
                   for k in ("hall1", "hall2", "current_a", "gap_mm")]
                  for r in rows], dtype=float)
    if a.ndim != 2 or a.shape[0] < 8 or not np.isfinite(a).all():
        raise ValueError("Need at least 8 finite rows per dataset")
    if ((a[:, :hall_sensors] < 16) | (a[:, :hall_sensors] > 4079)).any():
        raise ValueError("Hall readings approach ADC rails: change placement/sensitivity")
    if (a[:, 2] < 0).any() or (a[:, 3] <= 0).any():
        raise ValueError("Current must be nonnegative; gap must be positive")
    return a


def fit(a, hall_sensors=2):
    if hall_sensors not in (1, 2):
        raise ValueError("Choose one or two Hall sensors")
    columns = [0, 2] if hall_sensors == 1 else [0, 1, 2]
    x = a[:, columns]
    mean, scale = x.mean(axis=0), x.std(axis=0)
    if (scale < 1e-9).any():
        raise ValueError("Vary each installed Hall signal and current during calibration")
    z = np.column_stack((np.ones(len(x)), (x-mean)/scale))
    if np.linalg.matrix_rank(z) != len(columns)+1 or np.linalg.cond(z) > 1000:
        raise ValueError("Sensors/current cannot be separated reliably: rank/conditioning failure")
    beta = np.linalg.lstsq(z, a[:, 3], rcond=None)[0]
    c = np.zeros(4)
    c[0] = beta[0]-np.sum(beta[1:]*mean/scale)
    c[np.array(columns)+1] = beta[1:]/scale
    return c


def evaluate(c, a):
    error = np.column_stack((np.ones(len(a)), a[:, :3])) @ c - a[:, 3]
    return float(np.sqrt(np.mean(error**2))), float(np.max(np.abs(error)))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("training", type=Path)
    p.add_argument("holdout", type=Path)
    p.add_argument("--hall-sensors", type=int, choices=(1, 2), default=2)
    p.add_argument("--max-rmse-mm", type=float, default=0.25)
    p.add_argument("--max-error-mm", type=float, default=0.5)
    args = p.parse_args()
    if args.training.resolve() == args.holdout.resolve():
        p.error("Use an independent holdout file")
    train, test = load(args.training, args.hall_sensors), load(args.holdout, args.hall_sensors)
    if test[:, 3].min() < train[:, 3].min() or test[:, 3].max() > train[:, 3].max():
        p.error("Holdout gap lies outside training range")
    if test[:, 2].min() < train[:, 2].min() or test[:, 2].max() > train[:, 2].max():
        p.error("Holdout current lies outside training range")
    c = fit(train, args.hall_sensors)
    for name, a in (("training", train), ("holdout", test)):
        rms, worst = evaluate(c, a)
        print(f"{name}: RMSE={rms:.4f} mm, max absolute error={worst:.4f} mm")
    rms, worst = evaluate(c, test)
    if rms > args.max_rmse_mm or worst > args.max_error_mm:
        raise SystemExit("FAIL: affine model is inadequate; improve sensing or restrict the range")
    print("Candidate hall_c = {" + ", ".join(f"{v:.9g}f" if "." in f"{v:.9g}" or "e" in f"{v:.9g}" else f"{v:.9g}.0f" for v in c) + "};")
    print("PASS numerical holdout only. Verify monotonicity, orientation, dynamics, and temperature on hardware.")


if __name__ == "__main__":
    main()

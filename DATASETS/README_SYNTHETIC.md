# OptiFreight AI synthetic dataset v1.0

This folder contains generated simulation data, not observed customer, carrier, driver, vehicle or shipment records.

## Contents

- `synthetic/simulated_backhaul_scenarios.csv` — 100,000 simulated candidate scenarios.
- `synthetic/model_a_labeled.csv` — Model A features and `label_score`.
- `synthetic/model_b_labeled.csv` — Model B risk features and delay/cost targets.
- `synthetic/approved_model_a_labels.md`, `synthetic/approved_model_b_labels.md` — target definitions.
- `synthetic/generation_config.json`, `synthetic/dataset_manifest.json` — reproducibility and SHA-256 metadata.
- `splits/model_a/`, `splits/model_b/` — chronological 60/20/20 train/validation/test splits and integrity manifests.

## Simulation design

- 10,000 simulated trips, with 10 eligible post-delivery backhaul candidates per trip.
- India-focused city/state labels and INR costs; cities are simulated examples, not live cargo listings or verified route geometry.
- All scenarios pass the simulated hard-eligibility gate. Delivery-on-planned-route status and driver exception permission are explicitly flagged; off-route exception cases are capped at 20 km total extra distance.
- Model A target is the minimum of four 0–100 simulated component outcomes: completion, punctuality, cost efficiency and fulfilment quality.
- Model B targets are nonnegative simulated delay minutes and incremental INR cost. Cost components are retained in the master scenario file.
- Model B excludes `net_contribution_inr`, in line with the current risk-feature contract.
- Timestamp values are timezone-aware ISO-8601 UTC values, with `Asia/Kolkata` retained as the source timezone metadata.
- Fixed seed: `20261125`.

## Important limitations

These are synthetic labels generated from the same simulation assumptions that generate the features. A model can learn those assumptions, but performance on these rows does not establish real-world accuracy, generalization to actual Indian road networks, carrier behavior, or market prices. Do not mix these rows with real operational data in a single training run. Keep simulation-only metrics clearly labelled. No actual model training was performed during generation.

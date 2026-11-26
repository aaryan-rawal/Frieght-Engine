# Model B simulated label definition — v1.0

Source: explicitly simulated OptiFreight scenarios; not observed freight outcomes.
Targets: `delay_minutes` (minutes) and `incremental_cost_inr` (INR).

`delay_minutes` is a nonnegative simulated additional delay outcome generated from synthetic congestion, extra active time, pickup-window slack, and stochastic noise. `incremental_cost_inr` is the simulated nonnegative incremental cost ledger: incremental fuel cost + incremental toll cost + incremental driver time cost + handling cost + stochastic cost noise, floored at zero. Cost components are retained in the scenario master file.

Model B uses the serving contract's risk features and intentionally excludes `net_contribution_inr`. Each row is one candidate scenario nested within a trip. These are simulated outcomes, not actual observed same-event route re-entry or accounting records.

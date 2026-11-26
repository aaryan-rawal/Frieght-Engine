# Model A simulated label definition — v1.1

Source: explicitly simulated OptiFreight scenarios; not observed freight outcomes.
Target: `label_score`, score points on an approved 0–100 scale.

For each candidate, generate four simulated component outcomes, each clipped to [0,100]: (1) verified-completion proxy, (2) punctuality proxy, (3) cost-efficiency proxy, and (4) fulfilment-quality proxy. The training label is the minimum of the four components: `label_score = min(completion_component_score, punctuality_component_score, cost_efficiency_component_score, fulfilment_quality_component_score)`. The components are simulation proxies, not measured verification.

Candidates are generated as hard-eligibility-passed post-delivery backhaul options. Simulated off-route excursions are capped at 40 km total extra distance. Ten candidates belong to each trip; ranking is within `trip_id`. Cancellation/disputed/missing-outcome cases are not simulated in this version.

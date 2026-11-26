# ML dataset audit and preparation status

## Current conclusion

No approved, project-ready labeled dataset is available for Model A or Model B, and no model was trained. The Belgium OBU archive is present, safely extracted, and fully inventoried without exporting cell values. Its contents cannot supply the project targets without operational trip, matching, delivery-event and INR cost records.

The archive `DATASETS/Belgium_OBU/archive (2).zip` passed ZIP integrity validation. Its SHA-256 is `1da2028eb92f630abe92167b1fc9debfdbf79139c5877402d0602b59b9047875`. It contains 34 entries totaling 11,417,903,798 uncompressed bytes and was extracted to `DATASETS/extracted/belgium_obu_archive_2`; extracted byte totals matched the archive listing. The original archive was not modified. Licensing approval is owner-reported and has not been independently reviewed.

The full privacy-conscious inventory found 29 headerless CSVs, four JSON files, and one GIF. Across the CSVs there are **301,483,881 nonblank records**. All rows have four fields; there are no blank rows or inconsistent row widths. Positional field 0 contains 288,347,682 timezone-naive ISO-parseable timestamp values and 13,136,199 missing values (4.36%). The other three fields have no missing or non-finite numeric values. No timezone-aware text timestamps or numeric epoch timestamp candidates were found. Field 0's event meaning and timezone are unknown; fields 1–3 remain unnamed and their units are unknown. See `DATASETS/manifests/belgium_obu_archive_2_inventory.json`; it contains no cell values.

## Other available sources

| Source | Workspace evidence | ML suitability now |
|---|---|---|
| DataCo Supply Chain | Raw and processed CSVs; 180,519 records in each. The raw source contains direct personal fields, including customer password/email/name fields. | Processed copy may support exploratory delay analysis only. It is not Indian road-freight/backhaul ground truth and does not satisfy the feature/target contract. |
| Tokenized access logs | Raw and privacy-filtered copies; 469,977 records. | Not vehicle movement, cargo, match, delay, or cost outcomes. Exclude from these models. |
| Olist | Nine extracted CSV files, about 126 MB uncompressed. | Brazilian e-commerce data, not Indian freight matching. Personal/location fields require a separate privacy audit before any use. |
| SynDelay | 155,488-row synthetic delivery-delay dataset. The source README calls it synthetic but does not establish the 0/1/2 label semantics. | Do not map its label to project delay or cost targets without primary-source definitions and an approved mapping. |
| SimMD / CVRP | 601 files of simulated capacitated routing instances. | Routing research only; not observed outcomes, road-network routes, or cargo offers. |
| AnonNet and disruption-monitoring research | Anonymized network data and a companion research archive. | Not shipment outcome labels or live cargo data. |
| Belgium OBU | 34 archive entries; 301,483,881 CSV records across 29 headerless files. | Traffic/movement research only pending source semantics, privacy, and license review. Field 0 is timezone-naive timestamp-like; the other fields and units are unknown. No matching or cost labels are established. |

## Target readiness and missing evidence

- **Model A (`label_score`, 0–100):** the OBU archive does not establish cargo-match acceptance, cancellation attribution, shipment completion, candidate-level ranking context, or a verified service-quality outcome. No observed labels can be created from it. The score formula and candidate-group semantics still require approval.
- **Model B (`delay_minutes`, `incremental_cost_inr`):** the OBU archive does not establish a planned-route re-entry event and its actual re-entry at the same event/location, nor a timezone-safe timestamp pair. It also has no linked baseline/actual trip ledger with INR cost components. Traffic observations are not shipment-delay or cost labels.
- **OBU identifiers and joins:** the CSV files have no header; no road-segment identifier semantics have been established. The three street GeoJSON files have no feature property keys, so a defensible CSV-to-street join key is not evident. Their CRS is CRS84; `bruxelles.json` has no CRS metadata.
- The 301 million OBU records are not 301 million training examples: none has an approved Model A/B target or a verified project feature contract. Training-split adequacy therefore cannot be inferred from the raw row count.
- **Feature alignment:** the project contract requires point-in-time cargo, payload, detour, route, slack and (for Model A) net-contribution features. The inventoried public/research datasets do not provide that complete Indian freight feature/target combination.
- No approved curated Model A/Model B CSVs, split datasets, or trained model artifacts are present. No training was run.

## Candidate Model A formula — proposal only

Do not generate labels until the owner approves a formula and its component definitions. One transparent, unweighted candidate is the minimum of four 0–100 measured components: verified completion, punctuality relative to an approved planned service window, cost efficiency relative to an approved baseline budget, and a verified fulfillment-quality score. Taking the minimum prevents a strong component from masking a severe failure and avoids arbitrary weights. It still requires decisions about cancellation handling, missing/disputed costs, quality measurement, and the exact service window; it is not an approved formula or an observed label.

## Split preparation and training safeguards

`ml/training/prepare_splits.py` accepts curated labeled CSVs, rejects files under `DATASETS/raw/`, validates features, targets and provenance, and requires a trip/shipment group, timezone-aware timestamp, timestamp-source field, and a reviewed label-definition file. It produces deterministic train/validation/test splits with strictly ordered, non-overlapping time windows and whole groups kept together. By default, any cross-split overlap in an audited entity is rejected; vehicle, driver, cargo, or corridor overlap can be permitted only by an explicit CLI exception and is recorded in the manifest. The manifest includes input/split/label-definition hashes, target units, timezone-source counts, source-type counts, time ranges, and overlap counts for vehicle, driver, cargo, corridor and source-record identifiers; it does not expose entity values.

`ml/training/train_models.py` now requires the prepared split bundle and verifies its manifest and hashes. It uses validation data for early stopping and opens the test CSV only after fitting, for final metrics. Real and simulated/synthetic source types must be trained separately. Fewer than 100 test rows are explicitly marked insufficient for reportable test metrics. These safeguards have been tested with synthetic fixtures only; they have not been run on project training data.

## Still required before training

1. Complete review of the full OBU inventory; obtain and review source documentation, field semantics, units, timezone, privacy characteristics, and license terms.
2. Obtain approved, privacy-safe operational outcomes that include trip/shipment IDs, point-in-time features, Model A candidate outcomes, and Model B same-event baseline/actual re-entry timestamps plus INR cost ledgers.
3. Approve Model A's score and cancellation/missing-data rules, and Model B's event, timezone, cost-component and disputed-cost rules.
4. Curate labeled rows with `source_type` and source provenance; keep real and simulated data separate.
5. Review split manifests and leakage audits, ensure adequate train/validation/test sample sizes, then train and report real-only and simulation-only results separately.

Simulation may exercise the code path only when each input, assumption, and target is explicitly marked `simulated` and kept separate from real evaluation. Simulation must not be presented as evidence of real-world performance. No labels were invented and no synthetic training rows were generated in this audit.

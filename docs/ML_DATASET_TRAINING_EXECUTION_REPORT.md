# Dataset acquisition, suitability, and conditional-training report

**Executed:** 2026-11-22  
**Project root:** `C:\Users\Aaryan Rawal\Downloads\OAI`  
**Repository status:** This workspace root is not a Git repository; no commit/status could be recorded.

## Result and stop decision

**No target passed the stated suitability gate. No model was trained.** Execution stops here as instructed. No labels, synthetic datasets, split datasets, model artifacts, or application changes were created during this execution. The unapproved Model A scoring proposal was not applied.

## Inventory of `DATASETS/`

After the two permitted acquisitions, the directory contains **684 files, 26 subdirectories, and 15,506,192,516 bytes (about 15.51 GB)**. The following table summarizes its immediate subdirectories; the four files directly under `DATASETS/` total 10,670 bytes.

| Directory | Files | Bytes | Contents |
|---|---:|---:|---|
| `Belgium_OBU` | 1 | 2,841,719,502 | Original OBU archive, unchanged |
| `extracted` | 46 | 11,545,147,972 | OBU extraction, Olist, AnonNet and related files |
| `incoming` | 1 | 388 | OBU intake note |
| `LaDe-D` | 6 | 290,237,227 | Five Parquet shards and upstream README |
| `LaDe-P` | 6 | 443,259,433 | Five Parquet shards and upstream README |
| `manifests` | 4 | 232,812 | Dataset, integrity, and OBU inventory manifests |
| `processed` | 2 | 122,772,977 | Sanitized DataCo and access-log copies |
| `raw` | 3 | 191,359,957 | DataCo source, field dictionary, and tokenized access logs |
| `repositories` | 609 | 71,450,965 | SimMD, SynDelay, and research files |
| `source_archives` | 2 | 613 | Archive documentation/placeholders |

Other sources already inventoried include nine Olist CSVs (about 126 MB), two AnonNet graph CSVs, 601 SimMD routing instances, 155,488 SynDelay rows with unresolved class meanings, and a supply-chain disruption research archive retained in the companion package. The prior DataCo inventory has 180,519 records and identifies personal fields, including customer credentials; those fields are excluded from modeling. The OBU archive has 301,483,881 headerless CSV records, but no project labels. Details and new file hashes are in `DATASETS/manifests/dataset_manifest.json`; the OBU structural report is `DATASETS/manifests/belgium_obu_archive_2_inventory.json`.

The file count reconciles as 626 entries in the prior SHA-256 integrity manifest, 34 extracted OBU entries plus the original archive, 12 LaDe files, and 11 additional documentation/placeholder files: `.gitkeep`, `BELGIUM_OBU_PROFILE.md`, `DATASET_INVENTORY.md`, `README.md`, `incoming/belgium_obu/README_PENDING.txt`, both OBU inventory manifest files, both dataset/integrity manifest files, and the two `source_archives` placeholder/readme files. Those 11 files are included in the recursive count and byte total but are not individually covered by the cited file-level data manifests. The OBU inventory CSV and LaDe acquisition manifest provide their respective file-level listings; the table above summarizes the rest by directory rather than repeating hundreds of paths.

## Acquisition attempts

| ID | Dataset | Outcome, access/licence evidence, and local path |
|---|---|---|
| D1 | [LaDe-D](https://huggingface.co/datasets/Cainiao-AI/LaDe-D) | Downloaded the five Parquet shards and upstream README to `DATASETS/LaDe-D/`, pinned to revision `e1f85a3339848b9eb606ce543fcaaba3f4be1893`. Hugging Face reported public/ungated and Apache-2.0; the README says research use. This is publisher-provided evidence, not an independent rights audit. All shard sizes and SHA-256 values match upstream metadata. |
| D2 | [LaDe-P](https://huggingface.co/datasets/Cainiao-AI/LaDe-P) | Downloaded the five Parquet shards and upstream README to `DATASETS/LaDe-P/`, pinned to revision `f1ddd8dd163028dd5a8ab7d7c83b198ebd2f2167`. Same access/licence caveat as D1. All shard sizes and SHA-256 values match upstream metadata. |
| D3 | [Freight Transportation & Route Efficiency](https://datahub.skdikshit.com/dataset.php?slug=freight-transportation-route-efficiency) | **Blocked:** page retrieval failed and `curl` reported Windows `SEC_E_UNTRUSTED_ROOT`. TLS verification was not bypassed; contents and licence could not be verified. |
| D4 | [India FASTag](https://dataful.in/datasets/21607/) | **Blocked:** Dataful metadata marks the dataset not freely accessible and under a custom licence. Its [terms](https://dataful.in/terms-and-conditions/) say paywalled data requires a subscription; its [free plan](https://dataful.in/plans/) only permits free datasets. No payment, account, or access-control workaround was attempted. Only public preview metadata was assessed. |
| D5 | [Last-Mile Delivery Route Records](https://gomask.ai/marketplace/datasets/last-mile-delivery-route-records) | **Blocked:** web retrieval failed and `curl` timed out after 20 seconds. No login or payment attempt. |
| D6 | [Freight Route Performance Analytics](https://gomask.ai/marketplace/datasets/freight-route-performance-analytics) | **Blocked:** web retrieval failed and `curl` timed out after 20 seconds. No login or payment attempt. |

The four blocked sources were not downloaded, and their contents or licence terms are not assumed. D4's public preview reports 331,062 monthly/plaza/vehicle-category aggregate rows for 2022–23 through 2026–27; it is not the downloadable dataset.

## Actual inspection of downloaded LaDe files

The Parquet files were inspected locally with PyArrow 26.0.1. The source-card schema matched the actual files. No record values were copied into this report.

| Dataset | Rows | Duplicate `order_id` values | Nulls observed | Other verified structure |
|---|---:|---:|---|---|
| LaDe-D | 4,514,661 | 0 | 3,377 each in `accept_gps_lng` and `accept_gps_lat` | 17 columns; five city shards; unique `order_id` count equals row count |
| LaDe-P | 6,136,147 | 0 | 1,792,862 each in pickup GPS time/coordinates; 2,782,371 each in accept GPS time/coordinates | 19 columns; five city shards; unique `order_id` count equals row count |

Both contain order/courier identifiers, location coordinates, and event-time strings. Coordinates are degrees; identifiers are not predictive measures. Time columns have no timezone field, and the integer `ds` date encoding/year is not established by the actual schema. No non-finite floating values were detected. Treat the real-world provenance as **publisher-claimed, not independently audited**. The files include courier/order identifiers and location traces; keep them local and do not use those identifiers or raw coordinates as features.

The upstream field tables call the package identifier `package_id`, while the actual Parquet schema uses `order_id`; LaDe-P documentation also describes `region_id` as a string while the file stores `int64`. These documentation/schema differences need source clarification before semantic transformations.

### Target-by-target decision

| Target | Decision | Evidence |
|---|---|---|
| Model A `label_score` | **BLOCKED** | Neither LaDe dataset nor other inventory contains backhaul candidate groups, match acceptance/rejection, attributed cancellation, or an approved score. Parcel completion/pickup is not an equivalent label. The candidate scoring formula remains unapproved. |
| Model B `delay_minutes` | **BLOCKED** | LaDe-D has parcel accept/delivery events but no comparable planned delivery baseline timestamp. LaDe-P has pickup windows and actual pickup, but no approved mapping to this HGV/backhaul target; its timestamps lack verified timezone/year semantics. OBU field 0 is timezone-naive with 4.36% missing and unknown event meaning. FASTag is monthly/plaza aggregate data. DataCo's shipment-duration fields are not the required same-event timezone-safe timestamp pair. |
| Model B `incremental_cost_inr` | **BLOCKED** | No acquired or existing source provides comparable baseline trip cost without backhaul and actual trip cost with backhaul for the same trip/accounting basis. FASTag aggregates are not individual trip toll ledgers. No currency conversion or cost components were invented. |

Other existing sources also fail the target gates: Olist is Brazilian parcel commerce; tokenized access logs are web behavior; SynDelay's synthetic `0/1/2` meanings are unresolved; SimMD provides simulated routing instances, not operational match outcomes; AnonNet and disruption research do not provide trip-level freight labels. None was relabeled or combined to imply backhaul ground truth.

## Training evidence and owner action

No target passed, so there are no training commands, split manifests, metrics, or model artifacts. Model B cannot be partially trained under the current design because neither delay nor cost is eligible.

Minimum evidence needed to revisit training:

1. For Model A, an approved score definition plus privacy-safe, candidate-level backhaul match outcomes and trip/cargo provenance. Do not derive scores from parcel success or the unapproved proposal.
2. For Model B, matched baseline/actual timestamps for the same approved trip event and location, with known timezone and units; and comparable baseline/actual trip cost ledgers in INR with component definitions.
3. Source documentation and applicable licence/privacy approval for OBU and any future freight dataset. Provide accessible, authorized URLs or credentials only through approved local means; no payment or authentication bypass was attempted.

No production database was accessed or changed.

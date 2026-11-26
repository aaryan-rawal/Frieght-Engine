# Client cargo CSV import

The Client portal accepts a client-provided UTF-8 CSV in HTTP/server mode. It is not a connector to DataCo, Olist, Belgium OBU, or an external freight marketplace. Imported entries remain user-supplied and unverified; regulatory and road-network checks still run independently and fail closed.

## Required headers

`source_record_id,title,category,weight_kg,pickup_name,pickup_lat,pickup_lng,drop_name,drop_lat,drop_lng`

## Optional headers

`rate_inr,pickup_window_start,pickup_window_end,loading_minutes,unloading_minutes,waiting_minutes,hazardous,hazardous_description,food_storage_type,package_count,volume_m3,required_vehicle_type,special_handling`

Example header and illustrative row:

```csv
source_record_id,title,category,weight_kg,pickup_name,pickup_lat,pickup_lng,drop_name,drop_lat,drop_lng,rate_inr,hazardous
source-001,Example cargo,steel_coils_sections,1000,Pickup,28.61,77.21,Drop,19.08,72.88,25000,false
```

Pickup windows, when supplied, must both be timezone-aware ISO-8601 timestamps and the end must be later than the start. `hazardous` accepts `true/false`, `yes/no`, or `1/0`. Empty optional numbers remain unknown, not zero.

## Import behavior

- Maximum file size: 5 MiB. Maximum data rows: 1,000.
- Header names are case-insensitive after trimming. Duplicate or unsupported headers reject the file.
- Each row is validated against the same `ManualCargoIn` schema used by manual publication.
- Duplicate `source_record_id` values in a file or already imported by the same client are rejected; a database unique constraint handles concurrent imports.
- The backend records `source_type=csv_import`, the supplied source record ID and SHA-256 of the uploaded file. It does not echo rejected row contents.
- A CSV is not evidence that a cargo listing is true, licensed for republication, compliant, or eligible. The client is responsible for source rights and accuracy.

Apply database migration `0014_cargo_csv_provenance` before using this route with an existing database. No migration was applied during this work.

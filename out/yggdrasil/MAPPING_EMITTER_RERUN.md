# Mapping emitter rerun

Date: 2026-09-11

`out/yggdrasil/yggdrasil_route_namespace_mapping_001.latest.json` is stale.

It lists `neon_genie_ideation` in `missing_routes_for_pipelines` and reports `route_count: 12`.
The route file is on main:

`contracts/yggdrasil/routes/neon_genie_ideation.route.v1.json`

Do not hand-edit the JSON. Packet hash is canonical.

Re-run on a machine with the repo:

```bash
python scripts/operator/run_yggdrasil_route_namespace_mapping.py
```

Expected after rerun: neon_genie drops out of the missing list. route_count becomes 13. Seven pipelines stay PARTIAL (no route file):

- beatoven_psyfi_integration
- familiar_ingestion
- hollersports_ticket
- level99_content
- memetic_futurecast
- noctis_dream
- phonomicon_artifact

This note does not mutate `core/yggdrasil/`.
Does not train.
Does not Hub.

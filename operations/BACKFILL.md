# Backfill Guidance

## AdStream

Historical RTB events can be replayed through the ingestion path.

Backfills must preserve:

- idempotent Bronze/Silver processing;
- duplicate protection;
- quarantine behavior;
- cross-layer reconciliation;
- downstream serving consistency.

After a replay, confirm:

- pipeline health is successful;
- Gold outputs reconcile with Silver;
- serving refresh completes;
- no duplicate records were introduced.

## Kenya Economic Platform

Backfills should preserve historical source revisions and must not overwrite valid provenance.

After a backfill, confirm:

- dbt build succeeds;
- source health remains valid;
- latest indicator marts are correct;
- pipeline status reflects the completed execution.

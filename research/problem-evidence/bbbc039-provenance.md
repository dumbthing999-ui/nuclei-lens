# BBBC039v1 Provenance

**Retrieved and checked:** 2026-10-08.

- Publisher: Broad Institute, Broad Bioimage Benchmark Collection.
- Official record: https://bbbc.broadinstitute.org/BBBC039
- Accession/version: BBBC039v1.
- License: CC0 as explicitly stated on the official record.
- Scope: fluorescence/Hoechst DNA-channel images from U2OS cells in a single high-throughput chemical-screen experiment; one field per compound.
- Official record reports 200 image fields at 520×696, 16-bit TIFF, and approximately 23,000 manually annotated nuclei.
- Annotations: colored PNG instance masks; touching nuclei receive distinct colors. Decode and verify colors/instance semantics before measuring; foreground union is not an instance count.
- Archives: [images](https://data.broadinstitute.org/bbbc/BBBC039/images.zip), [masks](https://data.broadinstitute.org/bbbc/BBBC039/masks.zip), [metadata](https://data.broadinstitute.org/bbbc/BBBC039/metadata.zip).

## Verified metadata download

Downloaded the official metadata archive without a personal-information form. Inspected its text files directly using Python's ZipFile; macOS resource-fork entries are excluded from text decoding.

- SHA-256: `a2c1f900bed9ba92a99553efd4c2ae98598433691c7401d818653ab61110deb2`.
- `metadata/training.txt`: 100 nonempty filename records.
- `metadata/validation.txt`: 50 nonempty filename records.
- `metadata/test.txt`: 50 nonempty filename records.
- Archive also includes a readme, filename/plate metadata, and a CellProfiler pipeline. Their inclusion is not permission to represent that existing pipeline as original project code.
- Downloaded archive is under ignored `data/raw/BBBC039/`. Image/mask archives have not yet been downloaded or verified.

## Leakage and domain limits

Use the official image-level partition. Keep test images out of exploration/tuning and annotations out of inference. The record notes overlap with BBBC038; pretrained models may therefore have dataset overlap and are excluded from the primary classical-pipeline experiment. One cell line/experiment does not establish general microscopy or clinical performance. Human annotations are a reference, not an infallible standard.

Recommended citation and originating study are linked on the official dataset page; see references 21 and 36 in [SOURCES.md](../SOURCES.md).

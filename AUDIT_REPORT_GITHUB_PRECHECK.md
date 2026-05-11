# VEHICLE-SUPRA — GitHub Pre-Upload Critical Audit

## Status
**Conditional pass for GitHub upload after the corrections in this package.**

## Corrections applied
- Python cache folders and build artifacts are excluded from the corrected GitHub-ready package: `__pycache__/`, `.pytest_cache/`, and `.pyc` files.
- Added `.gitignore` for Python caches, build artifacts, virtual environments, editor files, and generated demo outputs.
- Updated package version from `0.1.0` to `0.2.0` in `setup.py` and `CITATION.cff`.
- Updated repository URL references to `https://github.com/vehiclesystemslab/VEHICLE-SUPRA`.
- Removed the Zenodo DOI badge from the README because the VEHICLE-SUPRA project-specific DOI should only be added after Zenodo archives the GitHub release.
- Kept the existing DOI only as a reference to the broader VEHICLE Formula-as-Architecture foundation.
- Refined the GITEX demo output narrative so Step 4 is displayed as `A2 — Recovery in progress` and Step 5 as `A0 — Stable coherent operation restored`.
- Moved generated demo reports into `sample_outputs/` and kept `outputs/` as a runtime-generated folder.

## Validation performed
- Unit tests: `8 passed`.
- GITEX demo: executed successfully.
- Demo reports: generated successfully.

## Public wording rule
Do **not** present this as production self-healing AI. Present it as:

> A synthetic alpha research simulation showing how an AI agent can be modeled, monitored, classified, and guided toward recovery under VEHICLE-SUPRA.

## GitHub recommendation
Upload this corrected package, not the previous ZIP, as the first public GitHub version.

Recommended release tag:
`v0.2.1-gitex-demo`

Recommended release status:
`Pre-release`


## v0.2.1 corrective pass

- Updated `__version__`, `setup.py`, and `CITATION.cff` to `0.2.1`.
- Removed cache folders, `.pytest_cache`, `.pyc`, and generated egg-info artifacts from the source package.
- Removed generated `outputs/` files while preserving `outputs/.gitkeep`; sample outputs remain under `sample_outputs/`.
- Updated README repository structure to include GITEX and VEHICLE-LUNA files.
- Softened LUNA and enterprise demo language to avoid production uptime, robotics safety, and unvalidated physical-stand claims.
- Clarified the existing DOI as a framework DOI until Zenodo archives the VEHICLE-SUPRA GitHub release.

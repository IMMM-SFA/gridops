# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-10-19

This release rebuilds the project as `gridops`, replacing the `go` package
published as v0.1.0. Code written against v0.1.0 needs to be updated.

### Added
- New `gridops` package for the U.S. Western Interconnection economic
  dispatch model: `Model`, `GoSolver`, configuration and utility modules.
  The `east` and `ercot` regions are placeholders that raise
  `NotImplementedError`. The solver retry and restart-file logic from
  v0.1.0 carries over.
- `OutageAllowance` parameter, which relaxes the ramp-down constraint by
  the size of forced generator capacity reductions.
- Example input data, example outputs, an example restart file and an
  example configuration file (`example_config_file.yml`), shipped in
  `gridops/data`.
- Quickstarter notebook (`notebooks/quickstarter.ipynb`).
- Test suite covering configuration, solvers, utilities and a western
  interconnection integration run.
- GitHub Actions workflow that tests, builds and publishes the package to
  PyPI as `gridops` on every push to `main`.
- This changelog.

### Changed
- Renamed the package from `go` to `gridops`.
- Moved packaging from `setup.py`/`requirements.txt` (setuptools) to
  `pyproject.toml` (hatchling).
- Raised the minimum Python version from 3.9 to 3.10 and added support for
  Python 3.10–3.14.
- Removed the `numpy<2` upper bound.
- Added HiGHS (`highspy`) as a required dependency.
- Model parameters close to zero (below `1e-6`) are now set to zero to avoid
  numerical instability in the solver.
- Reworded log messages to be shorter and more consistent.
- Rewrote the README with installation, quickstart, configuration, supported
  solvers and reference sections, and
  updated the author and maintainer contact details.

### Removed
- The `go` package and all of its modules, including `mapper`,
  `network_reduction`, `preprocessor` and `install_supplement`.
- The `scripts/` directory of WECC data setup and run scripts.
- The Sphinx documentation sources in `docs/`.
- `package_data` and the dependency on `pkg_resources`. The default
  `config.yml` was renamed to `example_config_file.yml`.
- The old `build` GitHub Actions workflow and issue templates.

## [0.1.0] - 2025-05-13

- Initial release of the `go` grid operations model.

[1.0.0]: https://github.com/IMMM-SFA/gridops/compare/v0.1.0...v1.0.0
[0.1.0]: https://github.com/IMMM-SFA/gridops/releases/tag/v0.1.0

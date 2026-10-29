# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-10-29

This release removes BA-to-BA hurdle rates from the model. Configuration
files written for v1.0.0 must drop the `ba_to_ba_hurdle_scaled_file` and
`ba_to_ba_transmission_matrix_file` keys.

### Added
- Must-run (nuclear) output in `mwh_file`. Each bus with must-run capacity
  is reported as `<bus>_NUCLEAR` with `Type=Nuclear`, using the
  outage-adjusted must-run capacity for every hour.
- Documentation website built with Sphinx and the PyData theme, published
  to GitHub Pages at <https://immm-sfa.github.io/gridops>. It covers getting
  started, a rendered quickstarter notebook, a user guide (configuration,
  inputs, outputs, mathematical formulation, simulation and solvers), the
  API reference, contributing guidelines, publications, how to cite, release 
  notes, publications, authors, license and acknowledgement.
- GitHub Actions `docs` workflow that builds the documentation on pull
  requests and deploys it to the `gh-pages` branch on every push to `main`.
- Documentation of the `warmstart` option in the `Model` and `Model.run`
  docstrings.
- PyPI and docs badges in the README.

### Changed
- Fixed the sign convention of the example `line_to_bus.csv` so that each
  line has `+1` at its *from* bus and `-1` at its *to* bus; positive flow now
  runs from the *from* bus to the *to* bus. The example outputs were
  regenerated.
- Clarified the power-flow sign convention in the bus balance constraint.
- Updated the quickstarter notebook for the removed hurdle rates and the new
  nuclear output.
- Replaced the `docs` extra (`nbsphinx`, `sphinx-panels`, `sphinx-rtd-theme`,
  `setuptools`) with `sphinx`, `pydata-sphinx-theme`, `sphinx-design`,
  `sphinx-copybutton` and `myst-nb`.
- Reworded the README and noted that HiGHS installs with the `highspy`
  dependency.

### Removed
- BA-to-BA hurdle rates: the `ba_to_ba_hurdle_scaled_file` and
  `ba_to_ba_transmission_matrix_file` configuration keys, the `exchanges`
  set, the `ExchangeHurdle` and `ExchangeMap` parameters, the exchange cost
  term in the objective, and the example files
  `BA_to_BA_hurdle_scaled.csv` and `BA_to_BA_transmission_matrix.csv`.

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
  PyPI as `gridops` on every push to `main`, then creates a tagged GitHub
  release with notes taken from this changelog.
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

[1.1.0]: https://github.com/IMMM-SFA/gridops/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/IMMM-SFA/gridops/compare/v0.1.0...v1.0.0
[0.1.0]: https://github.com/IMMM-SFA/gridops/releases/tag/v0.1.0

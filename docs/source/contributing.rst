Contributing
============

You're welcome to contribute, whether you've found a typo in the documentation,
found a bug, or want to add functionality that makes gridops more useful. Thank you for your valuable contributions!

Opening issues
--------------

If you find a bug or have an idea for a new feature, please
`open an issue <https://github.com/IMMM-SFA/gridops/issues>`_. For substantial changes,
discuss the approach in an issue before writing code.

Contribution workflow
---------------------

1. `Fork the gridops repository <https://github.com/IMMM-SFA/gridops/fork>`_ and clone
   it locally:

   .. code-block:: bash

      git clone https://github.com/<your-user-name>/gridops
      cd gridops

   Install the package in editable (development) mode with the test extras. Your
   code changes then take effect without reinstalling:

   .. code-block:: bash

      pip install -e ".[test]"

2. Create a branch for your changes:

   .. code-block:: bash

      git checkout -b bug/some-bug
      # or
      git checkout -b feature/some-feature

3. Make your changes and make sure all tests pass:

   .. code-block:: bash

      python -m pytest tests --cov=gridops --cov-report=term-missing

   The integration test runs the bundled Western Interconnection example with HiGHS.

4. Documentation lives in ``docs/source`` as reStructuredText and Markdown files. To
   preview your changes, install the documentation extras and build the site:

   .. code-block:: bash

      pip install -e ".[docs]"
      sphinx-build -W --keep-going -b html docs/source docs/build/html

   Open ``docs/build/html/index.html`` in your browser. When your changes are merged
   into the ``main`` branch, a GitHub Actions workflow rebuilds the documentation and
   publishes it to GitHub Pages.

5. Commit and push your changes:

   .. code-block:: bash

      git add <my-file-name>
      git commit -m "<my short message>"
      git push origin <my-branch-name>

6. Open a pull request that describes:

   * **Purpose**: Why you're making the change.
   * **Summary**: Your environment (OS, Python version, solver), the logic, any
     caveats, and what changed.
   * **Validation**: How you tested the change.

   Continuous integration runs the test suite on every supported Python version.

7. If approved, a gridops maintainer merges your pull request. gridops follows
   `semantic versioning <https://semver.org/>`_, and notable changes are recorded in
   the :doc:`release_notes`.

Coding conventions
------------------

Please follow the conventions already used in the gridops code base so that new code
reads like the existing code.

Python style
~~~~~~~~~~~~

* gridops supports Python 3.10 to 3.14. Use Python language features accordingly.
* Start every module with ``from __future__ import annotations`` and add type hints
  to every function signature (for example ``Dict[str, Any]``, ``Optional[int]``,
  ``Union[str, None]``).
* Use ``snake_case`` for functions and variables, ``PascalCase`` for classes and
  ``UPPER_CASE`` for module-level constants. Put a one-line comment above each
  constant that states what it means and its unit, for example
  ``# Penalty for unserved energy/load shedding ($/MWh).``
* Prefix private helpers with an underscore (such as ``_update_horizon_params``). The
  ``configuration`` and ``utilities`` modules are re-exported with
  ``from .module import *`` in ``gridops/__init__.py``, so any name without a leading
  underscore becomes part of the public ``gridops`` namespace.
* Group related code under section separator comments: a short title between two
  ``# -----`` lines, as in ``gridops/utilities.py``.
* Open text files with an explicit ``encoding="utf-8"``.
* State physical units in comments and docstrings (MW, MWh, $/MWh,
  $/MMBtu, p.u.).

Docstrings
~~~~~~~~~~

* Functions and classes have NumPy-style docstrings with ``Parameters``,
  ``Returns`` and ``Raises`` sections. They are rendered in the :doc:`api`.
* Refer to other objects with Sphinx roles, for example
  ``:func:`~gridops.utilities.write_restart_file```.
* If you add a public function or class, add it to ``docs/source/api.rst``.

Logging and errors
~~~~~~~~~~~~~~~~~~

* Don't use ``print``. Get a logger with ``logging.getLogger(__name__)`` so that
  messages go through the package-level ``gridops`` logger configured in
  ``gridops/__init__.py``. Keep log messages short and consistent with the existing
  ones.
* Raise specific exceptions with a clear message, for example ``ValueError`` for
  invalid input data and ``NotImplementedError`` for regions or problem types that
  are not available yet.

Optimization models
~~~~~~~~~~~~~~~~~~~

* Build the Pyomo model once. Store time-varying data in mutable parameters
  (``mutable=True``) and update them in place between horizons instead of
  rebuilding the model.
* Write each constraint and objective rule as a module-level function named
  ``_<name>_rule`` with a docstring that describes the equation.
* Use ``pyo.quicksum`` and the precomputed sparse lookups (``_lines_at_bus``,
  ``_gens_at_bus``, ...) instead of looping over full incidence matrices.
* Keep penalty and cost constants at the top of the module and document any change
  to them, or to the equations, in :doc:`user_guide/formulation`.

Tests
~~~~~

* New behavior comes with a test in ``tests/test_<module>.py``. Tests are
  ``unittest.TestCase`` classes run with ``pytest``. Give every test method a
  one-line docstring that states what it checks.
* Write temporary files to a ``tempfile.mkdtemp()`` directory and remove it in
  ``tearDown``.
* Tests must not need a commercial solver license or network access. Use HiGHS for
  tests that solve a model.

Documentation
~~~~~~~~~~~~~

* The documentation build treats warnings as errors (``sphinx-build -W``), so check
  that it builds cleanly before opening a pull request.
* Notebooks in ``notebooks/`` are copied into the documentation and rendered from
  their stored outputs; they are not executed during the build. If you change a
  notebook, run it from top to bottom and save it with its outputs.

Versioning and changelog
~~~~~~~~~~~~~~~~~~~~~~~~

* gridops follows `semantic versioning <https://semver.org/>`_. The version number
  is set in two places that must match: ``version`` in ``pyproject.toml`` and
  ``__version__`` in ``gridops/__init__.py``.
* Add an entry to ``CHANGELOG.md`` under the next release, using the
  `Keep a Changelog <https://keepachangelog.com/en/1.1.0/>`_ headings (``Added``,
  ``Changed``, ``Removed``, ...).
* Every push to ``main`` runs the publishing workflow. When the version number has
  changed, the package is published to PyPI and a GitHub release is created with the
  notes from ``CHANGELOG.md``.

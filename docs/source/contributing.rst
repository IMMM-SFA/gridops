Contributing to gridops
=======================

You're welcome to contribute, whether you've found a typo in the documentation,
found a bug, or want to add functionality that makes gridops more useful.

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

   * **Purpose**: why you're making the change, in short.
   * **Summary**: your environment (OS, Python version, solver), the logic, any
     caveats, and what changed.
   * **Validation**: how you tested the change.

   Continuous integration runs the test suite on every supported Python version.

7. If approved, a gridops maintainer merges your pull request. gridops follows
   `semantic versioning <https://semver.org/>`_, and notable changes are recorded in
   the :doc:`release_notes`.

Coding conventions
------------------

* Public functions and classes have NumPy-style docstrings with ``Parameters``,
  ``Returns`` and ``Raises`` sections.
* New behavior comes with a unit test in ``tests/``.
* Add an entry to ``CHANGELOG.md`` under the next release.

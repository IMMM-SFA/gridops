Getting started
===============

About gridops
-------------

**gridops** is an open-source production cost model (PCM) for the U.S. bulk power
system. It represents a reduced version of each interconnection's transmission network
as buses connected by lines. It then solves a linear DC Optimal Power Flow (DC-OPF)
problem for every hour of the simulation, using a rolling horizon. Each horizon
dispatches thermal, hydro, wind, solar, offshore-wind, must-run (nuclear) and storage
resources at least cost. The solve respects transmission limits, ramp rates, hydro
energy budgets and forced-outage capacity losses.

gridops is written in Python and builds its optimization models with
`Pyomo <https://www.pyomo.org/>`_. Models can be solved with the open-source
`HiGHS <https://highs.dev/>`_ solver (installed with gridops) or with the commercial
`Gurobi <https://www.gurobi.com/>`_ solver.

Model availability
------------------

The table below shows which region and problem combinations ``gridops.Model`` accepts
in the current release.

.. list-table::
   :header-rows: 1
   :widths: 25 25 20 30

   * - Region (``region=``)
     - Problem (``problem=``)
     - Status
     - Notes
   * - ``"west"``
     - ``"linear"``
     - Available
     - U.S. Western Interconnection economic dispatch (LP).
   * - ``"west"``
     - ``"mixed_integer"``
     - Planned
     - Unit commitment (MILP); raises ``NotImplementedError``.
   * - ``"east"``
     - any
     - Planned
     - U.S. Eastern Interconnection; raises ``NotImplementedError``.
   * - ``"ercot"``
     - any
     - Planned
     - ERCOT (Texas) Interconnection; raises ``NotImplementedError``.

Python version support
----------------------

gridops supports Python 3.10, 3.11, 3.12, 3.13 and 3.14. Every supported version is
tested in continuous integration.

Installation
------------

Install the latest release from PyPI:

.. code-block:: bash

   pip install gridops

To install the development version from GitHub instead:

.. code-block:: bash

   git clone https://github.com/IMMM-SFA/gridops.git
   cd gridops
   pip install -e .

Check the installation:

.. code-block:: python

   import gridops as go

   print(go.__version__)

Dependencies
~~~~~~~~~~~~

The following packages are installed with gridops:

.. list-table::
   :header-rows: 1
   :widths: 30 20 50

   * - Package
     - Minimum version
     - Used for
   * - `pyomo <https://www.pyomo.org/>`_
     - 6.0.1
     - Building and solving the optimization model
   * - `highspy <https://pypi.org/project/highspy/>`_
     - 1.10.0
     - Default open-source HiGHS solver
   * - `pandas <https://pandas.pydata.org/>`_
     - 2.2.2
     - Reading inputs and writing outputs
   * - `numpy <https://numpy.org/>`_
     - 1.26.4
     - Numerical operations and outage-group file
   * - `pyarrow <https://arrow.apache.org/docs/python/>`_
     - 17.0.0
     - Parquet output files
   * - `cloudpickle <https://github.com/cloudpipe/cloudpickle>`_
     - 3.0.0
     - Restart files
   * - `PyYAML <https://pyyaml.org/>`_
     - 5.4.1
     - Configuration file parsing
   * - `requests <https://requests.readthedocs.io/>`_
     - 2.25.1
     - Declared runtime dependency

Optional extras are available for development:

.. code-block:: bash

   pip install "gridops[test]"   # pytest and pytest-cov
   pip install "gridops[docs]"   # Sphinx and the documentation theme

Solvers
~~~~~~~

.. tab-set::

   .. tab-item:: HiGHS (default)

      HiGHS is open source and is installed automatically through the ``highspy``
      dependency. Select it with ``solver_name="appsi_highs"``. No license is
      required.

   .. tab-item:: Gurobi

      Gurobi is a commercial solver and needs a
      `valid license <https://www.gurobi.com/academics>`_
      (free academic licenses are available). Install the Python bindings with:

      .. code-block:: bash

         pip install gurobipy

      Then select ``solver_name="appsi_gurobi"`` (persistent APPSI interface, which
      supports warm starts) or ``solver_name="gurobi"``.

See :doc:`user_guide/solvers` for solver options, warm starts and the automatic retry
logic.

Example data
------------

gridops ships with a small example dataset for the U.S. Western Interconnection,
installed with the package under ``gridops/data``:

.. code-block:: text

   gridops/data/
   ├── example_config_file.yml      # configuration template pointing at the files below
   ├── example_inputs/              # 2 days of hourly inputs on a 125-bus, 786-line network
   ├── example_outputs/             # destination for the Parquet outputs
   └── example_restart_files/       # destination for restart files and solver logs

You can find the folder on your machine with:

.. code-block:: python

   from importlib.resources import files

   print(files("gridops").joinpath("data"))

The example network has 1,696 generators (natural gas combined cycle, biomass,
geothermal, oil, coal, solar, wind and hydro), six nuclear units represented as
must-run capacity at three buses, and 64 storage units (batteries and pumped storage
hydro). The inputs cover 48 hours, so the example can run for up to two days.

Next steps
----------

* Run the example in the :doc:`Quickstart <notebooks/quickstarter>`.
* Read the :doc:`user_guide/index` to prepare your own inputs.
* Browse the :doc:`api`.

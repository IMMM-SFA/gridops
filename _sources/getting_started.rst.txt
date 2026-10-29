Getting started
===============

About gridops
-------------

**gridops** is an open-source production cost model (PCM) for three major U.S. interconnections 
(Western, Eastern, and ERCOT). It represents a reduced version of each interconnection's 
network as nodes connected by transmission lines. It then uses a linear DC Optimal Power Flow 
(DC-OPF) approximation to optimize hourly unit commitment and economic dispatch over a rolling horizon. 
Each horizon dispatches generators and storage units to minimize the operating cost. The solve respects 
transmission limits, generator ramp rates, hydro energy budgets among many other constraints.

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

Optional extras are available for development:

.. code-block:: bash

   pip install "gridops[test]"
   pip install "gridops[docs]"

Check the installation:

.. code-block:: python

   import gridops as go

   print(go.__version__)

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

      Select ``solver_name="appsi_gurobi"`` (persistent APPSI interface, which
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
   ├── example_inputs/              # 2 days of inputs on a 125-node, 786-line network
   ├── example_outputs/             # destination for the Parquet outputs
   └── example_restart_files/       # destination for restart files and solver settings

You can find the folder on your machine with:

.. code-block:: python

   from importlib.resources import files

   print(files("gridops").joinpath("data"))

The example network represents a 125-node, 786-line network. 
The inputs cover 48 hours, so the example can be run for up to two days.

Next steps
----------

* Run the example in the :doc:`Quickstart <notebooks/quickstarter>`.
* Read the :doc:`user_guide/index` to get familiar with the gridops and prepare your own inputs.
* Browse the :doc:`api`.

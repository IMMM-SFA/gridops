Quickstart
==========

This page runs the bundled U.S. Western Interconnection example from start to finish,
then shows how to point gridops at your own data. For a version with plots, see the
:doc:`notebooks/quickstarter` notebook.

Run the example
---------------

A gridops simulation has two steps: create a :class:`~gridops.model.Model`, then call
:meth:`~gridops.model.Model.run`.

.. code-block:: python

   import os
   from importlib.resources import files

   import gridops as go

   # The example configuration uses paths relative to the gridops/data folder
   data_dir = files("gridops").joinpath("data")
   os.chdir(data_dir)

   model = go.Model(
       region="west",              # U.S. Western Interconnection
       problem="linear",           # linear programming (economic dispatch)
       solver_name="appsi_highs",  # open-source HiGHS solver
       solver_params={"log_to_console": False, "output_flag": False},  # silence HiGHS
   )

   model.run(
       config_file="example_config_file.yml",
       n_days=2,           # the example inputs cover 48 hours
       horizon_hours=24,   # one 24-hour optimization window per day
   )

gridops logs its progress (configuration, data loading, every horizon, output writing)
at the ``INFO`` level. When the run finishes, eight Parquet files are written to
``example_outputs/`` and a ``solver_parameters.json`` audit file to
``example_restart_files/``.

.. tip::

   The paths in a configuration file can be absolute, or relative to the
   **current working directory**. Use absolute paths in your own configuration files
   so you don't need ``os.chdir``.

Read the outputs
----------------

Every output is a long-format table with a ``Time`` column. ``Time`` is the
1-based absolute hour of the simulation.

.. code-block:: python

   import pandas as pd

   lmp = pd.read_parquet("example_outputs/duals.parquet")      # Node, Time, Value ($/MWh)
   slack = pd.read_parquet("example_outputs/slack.parquet")    # Node, Time, Value (MWh)
   gen = pd.read_parquet("example_outputs/mwh.parquet")        # Generator, Type, Time, Value (MWh)

   # Hourly average LMP across all buses
   avg_lmp = lmp.groupby("Time")["Value"].mean()

   # Hourly total unserved energy
   unserved = slack.groupby("Time")["Value"].sum()

   # Generation mix (share of total energy by type)
   mix = gen.groupby("Type")["Value"].sum()
   print((100 * mix / mix.sum()).round(2))

See :doc:`user_guide/outputs` for every output file and its columns.

Use your own data
-----------------

1. Copy the configuration template and edit the paths:

   .. code-block:: python

      import shutil
      from importlib.resources import files

      shutil.copy(files("gridops").joinpath("data/example_config_file.yml"), "my_config.yml")

2. Prepare the input files described in :doc:`user_guide/inputs`. The easiest way to
   start is to copy the example inputs and replace their values.

3. Run the model for as many days as your hourly inputs cover:

   .. code-block:: python

      model = go.Model(region="west", problem="linear", solver_name="appsi_highs")
      model.run(config_file="my_config.yml", n_days=365, horizon_hours=24)

Configure without a YAML file
-----------------------------

If ``config_file`` is ``None``, the keyword arguments passed to
:meth:`~gridops.model.Model.run` are used to build the
:class:`~gridops.configuration.Config` directly. Every configuration key must be
supplied:

.. code-block:: python

   model.run(
       config_file=None,
       n_days=2,
       generator_parameters_file="inputs/data_genparams.csv",
       generator_matrix_file="inputs/gen_mat.csv",
       # ... every other input, output and restart key ...
       restart_file_directory="restart",
   )

Long runs and restarts
----------------------

Year-long simulations can take hours. gridops writes a restart file every
``restart_write_frequency`` horizons (default 30). If a run stops, calling
:meth:`~gridops.model.Model.run` again with the same arguments resumes it from the
latest restart file:

.. code-block:: python

   model.run(
       config_file="my_config.yml",
       n_days=365,
       restart_write_frequency=7,  # write a restart file every 7 horizons
       clear_restart=False,        # keep restart files after a successful run
   )

   # Resume from a specific day instead of the latest restart file
   model.run(config_file="my_config.yml", n_days=365, restart_day=140)

   # Ignore any previous restart files and start from scratch
   model.run(config_file="my_config.yml", n_days=365, fresh_start=True)

See :doc:`user_guide/simulation` for how horizons, restarts and the retry logic work.

Choose a solver
---------------

.. code-block:: python

   # HiGHS with a one-hour time limit per horizon
   model = go.Model(
       region="west",
       problem="linear",
       solver_name="appsi_highs",
       solver_params={"time_limit": 3600, "presolve": "on"},
   )

   # Gurobi (license required), warm-starting each horizon from the previous basis
   model = go.Model(
       region="west",
       problem="linear",
       solver_name="appsi_gurobi",
       solver_params={"Threads": 8},
       warmstart=True,
   )

See :doc:`user_guide/solvers` for the warm-start policy and the retry search grid.

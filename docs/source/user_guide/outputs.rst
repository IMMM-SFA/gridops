Outputs
=======

When all horizons have been solved, gridops writes eight Parquet files to the paths
in the configuration file and a JSON audit file to the restart directory. Every
Parquet file is a long-format table. ``Time`` is the **1-based absolute hour** of the
simulation, so hour 25 is the first hour of day 2.

Parquet files
-------------

.. list-table::
   :header-rows: 1
   :widths: 22 30 13 35

   * - Configuration key
     - Columns
     - Unit of ``Value``
     - Description
   * - ``mwh_file``
     - ``Generator``, ``Type``, ``Time``, ``Value``
     - MWh
     - Hourly dispatch of each generator. ``Type`` is the model set (``Coal``,
       ``Oil``, ``Gas``, ``Hydro``, ``Solar``, ``Wind``, ``OffshoreWind``,
       ``Biomass``, ``Geothermal``). Must-run output appears with
       ``Type == "Nuclear"`` and ``Generator == "<bus>_NUCLEAR"``.
   * - ``duals_file``
     - ``Node``, ``Time``, ``Value``
     - $/MWh
     - Locational marginal price: the dual of the bus power-balance constraint.
   * - ``slack_file``
     - ``Node``, ``Time``, ``Value``
     - MWh
     - Unserved energy (load shedding) at each bus.
   * - ``flow_file``
     - ``Line``, ``Time``, ``Value``
     - MW
     - DC line flow. Positive values flow from the line's ``+1`` bus to its ``-1``
       bus.
   * - ``vlt_angle_file``
     - ``Node``, ``Time``, ``Value``
     - rad
     - Bus voltage angle relative to the reference bus.
   * - ``storage_soc_file``
     - ``Storage``, ``Time``, ``Value``
     - MWh
     - State of charge at the end of the hour.
   * - ``storage_charge_file``
     - ``Storage``, ``Time``, ``Value``
     - MW
     - Charging power drawn from the bus.
   * - ``storage_discharge_file``
     - ``Storage``, ``Time``, ``Value``
     - MW
     - Discharging power delivered to the bus.

Because each horizon is one hour per time step, MW and MWh are numerically equal for
the hourly dispatch values.

Working with the outputs
------------------------

.. code-block:: python

   import pandas as pd

   gen = pd.read_parquet("example_outputs/mwh.parquet")

   # Wide table: one column per generator type, one row per hour
   by_type = gen.pivot_table(index="Time", columns="Type", values="Value", aggfunc="sum")

   # Daily average LMP at every bus
   lmp = pd.read_parquet("example_outputs/duals.parquet")
   lmp["Day"] = (lmp["Time"] - 1) // 24 + 1
   daily_lmp = lmp.pivot_table(index="Day", columns="Node", values="Value", aggfunc="mean")

   # Hours with any unserved energy
   slack = pd.read_parquet("example_outputs/slack.parquet")
   stressed_hours = slack.loc[slack["Value"] > 0, "Time"].unique()

   # Line loading as a fraction of the thermal limit
   flow = pd.read_parquet("example_outputs/flow.parquet")
   limits = pd.read_csv("example_inputs/line_param.csv", index_col="line")["limit"]
   flow["Loading"] = flow["Value"].abs() / flow["Line"].map(limits)

Solver audit file
-----------------

``<restart_file_directory>/solver_parameters.json`` records the solver options used
for each horizon. Horizons are keyed by their 0-based index as strings. This makes it
easy to see which horizons needed a different solver configuration during a retry.
Load it with :func:`~gridops.utilities.load_solver_parameters`, which converts the keys
back to integers:

.. code-block:: python

   from gridops import load_solver_parameters

   params = load_solver_parameters("example_restart_files/solver_parameters.json")
   params[0]   # {'log_to_console': False, 'output_flag': False, 'solver': 'ipm', 'run_crossover': 'on'}

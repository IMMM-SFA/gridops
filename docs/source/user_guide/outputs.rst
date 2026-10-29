Output data
===========

When all horizons have been solved, gridops writes output Parquet files to the paths
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
       ``Biomass``, ``Geothermal``). Must-run output appears as ``Nuclear``.
   * - ``duals_file``
     - ``Node``, ``Time``, ``Value``
     - $/MWh
     - Hourly locational marginal price (LMP) at each bus; the dual of the bus power balance constraint.
   * - ``slack_file``
     - ``Node``, ``Time``, ``Value``
     - MWh
     - Hourly unserved energy (load shedding) at each bus.
   * - ``flow_file``
     - ``Line``, ``Time``, ``Value``
     - MW
     - Hourly power flow at each transmission line.
   * - ``vlt_angle_file``
     - ``Node``, ``Time``, ``Value``
     - radian
     - Hourly voltage angle at each bus.
   * - ``storage_soc_file``
     - ``Storage``, ``Time``, ``Value``
     - MWh
     - Hourly state of charge at each storage unit.
   * - ``storage_charge_file``
     - ``Storage``, ``Time``, ``Value``
     - MW
     - Hourly power charged at each storage unit.
   * - ``storage_discharge_file``
     - ``Storage``, ``Time``, ``Value``
     - MW
     - Hourly power discharged at each storage unit.

Because temporal resolution of gridops is hourly, MW and MWh are numerically equal for
the hourly dispatch values.

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

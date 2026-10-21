Running simulations
===================

This page explains what happens when you call :meth:`gridops.model.Model.run`: how
the simulation period is split into horizons, how state carries from one horizon to
the next, how restart files work, and what happens when a horizon fails to solve.

Rolling horizon
---------------

The simulation length ``n_days`` is split into consecutive, non-overlapping horizons
of ``horizon_hours`` hours (default 24):

.. math::

   N_{horizons} = \left\lfloor \frac{24 \cdot \text{n_days}}{\text{horizon_hours}} \right\rfloor

Horizon :math:`k` (0-based) covers absolute hours :math:`kH + 1` to :math:`(k+1)H`.
Every hour of every horizon is kept in the outputs. If ``24 * n_days`` is not a
multiple of ``horizon_hours``, the leftover hours at the end are not simulated.

The Pyomo model is built **once**. Before each solve, gridops updates the model's
mutable parameters in place:

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Data
     - Value used for horizon :math:`k`
   * - Demand, solar, wind, offshore wind
     - The :math:`H` hourly rows of the horizon.
   * - Fuel prices, hydro min/max
     - The row for the day that contains the horizon's first hour.
   * - Hydro energy budget
     - Sum of ``max(1, horizon_hours // 24)`` daily rows, starting at that day.
   * - Coal/Gas capacity, must-run capacity
     - Base capacity minus the hourly losses in ``lost_capacity_file``.

State carry-over
~~~~~~~~~~~~~~~~

At the end of each horizon:

* the output of every thermal unit in the last hour becomes :math:`p^{0}_g` for the
  next horizon's ramp constraints (clipped at zero), and
* the state of charge of every storage unit in the last hour becomes
  :math:`SoC^{0}_s` (clipped to :math:`[\underline{SoC}_s, \overline{SoC}_s]`).

A fresh run starts with all thermal output at zero, storage at its minimum state of
charge, and the hour-1 ramp constraints switched off in the first horizon.

Sanity checks
~~~~~~~~~~~~~

A horizon is treated as failed if the solver does not return an *optimal* termination
condition with an *ok* status, or if any generator output is below ``-1e-3`` MW.

Restart files
-------------

Long simulations save their progress in restart files. These are cloudpickle files
in ``restart_file_directory`` that hold the Pyomo model, the results so far, the input
data and the solver settings used for each horizon.

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - ``Model.run`` argument
     - Effect
   * - ``restart_write_frequency`` (default 30)
     - Write a restart file after every *N* solved horizons.
   * - ``restart_day`` (default ``None``)
     - ``None`` resumes from the newest restart file, or starts fresh if there is
       none. An integer resumes from the newest file for that day and raises an
       error if no such file exists.
   * - ``fresh_start`` (default ``False``)
     - Delete all restart files before starting.
   * - ``clear_restart`` (default ``True``)
     - Delete all restart files after every day has been solved. Files are kept if
       the run fails.

Restart files are named ``model_restart_file_day{DDD}_v{VVV}.pkl``. ``DDD`` is the day
of the last completed horizon, and ``VVV`` is a version number that increases if a
file for the same day already exists. When a horizon fails, gridops first writes a
restart file for the last successful horizon, so a later run can resume right
before the failure.

The restart helpers are also available directly. See
:func:`~gridops.utilities.get_restart_file`,
:func:`~gridops.utilities.get_prior_restart_file_day`,
:func:`~gridops.utilities.write_restart_file` and
:func:`~gridops.utilities.clear_restart_files`.

.. code-block:: python

   from gridops import clear_restart_files, get_restart_file

   print(get_restart_file("example_restart_files"))           # newest file or None
   n_deleted = clear_restart_files("example_restart_files")

.. warning::

   Restart files are Python pickles. Only load restart files that you created
   yourself or that come from a trusted source.

Automatic retry
---------------

Large LPs can occasionally fail to solve because of numerical difficulties. If a
horizon fails and ``allow_retry=True`` (the default), :meth:`~gridops.model.Model.run`
calls :meth:`~gridops.model.Model.retry`. This method tries a series of alternative
solver configurations, each starting from the latest restart file and solving a
single horizon:

* **HiGHS**: a Cartesian product of algorithms, tolerances, simplex strategies and
  ``retry_n_seeds`` random seeds. The search grid comes from
  :data:`~gridops.model.HIGHS_RETRY_DEFAULTS` and can be overridden with
  ``retry_options``.
* **Gurobi**: ``max_retries`` random values of the ``Seed`` parameter.

At most ``max_retries`` trials (default 30) are attempted. Once a trial succeeds,
gridops goes back to the original solver settings and continues the run.

If every trial fails and ``retry_backoff=True`` (the default), gridops rewinds to the
**previous** restart day, sets a new random seed and tries again from there. If no
earlier restart file exists, or back-off is disabled, the last error is raised.

.. code-block:: python

   model.run(
       config_file="my_config.yml",
       n_days=365,
       max_retries=10,
       retry_n_seeds=2,
       retry_options={"solver_list": ["ipm"], "ipm_optimality_tolerance": [1e-7, 1e-6]},
   )

   # Fail immediately instead of retrying
   model.run(config_file="my_config.yml", n_days=365, allow_retry=False)

Logging
-------

gridops logs to the ``gridops`` logger at the ``INFO`` level, with a stream handler
attached when the package is imported. Use the standard :mod:`logging` module to
change the verbosity or send the logs to a file:

.. code-block:: python

   import logging

   logging.getLogger("gridops").setLevel(logging.WARNING)

   handler = logging.FileHandler("gridops_run.log")
   logging.getLogger("gridops").addHandler(handler)

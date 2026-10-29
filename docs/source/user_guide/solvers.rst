Solvers
=======

gridops passes its Pyomo model to a solver through :class:`~gridops.solvers.GoSolver`,
a thin wrapper around Pyomo's ``SolverFactory``.

Supported solvers
-----------------

.. list-table::
   :header-rows: 1
   :widths: 22 18 60

   * - Solver name (``solver_name=``)
     - License
     - Notes
   * - ``"appsi_highs"`` (default)
     - Open source
     - HiGHS through Pyomo's persistent APPSI interface. Installed with gridops via
       ``highspy``.
   * - ``"appsi_gurobi"``
     - Commercial
     - Gurobi through the persistent APPSI interface (``gurobipy``). Supports warm
       starts.
   * - ``"gurobi"``
     - Commercial
     - Gurobi through Pyomo's standard interface. Does not support warm starts.

Any other name raises an error when the :class:`~gridops.model.Model` is created.

Solver options
--------------

``solver_params`` is a dictionary of options passed to the solver unchanged. gridops
doesn't add defaults of its own, apart from the warm start policy below. Option names
are solver-specific: see the
`HiGHS options <https://ergo-code.github.io/HiGHS/stable/options/definitions/>`_ and the
`Gurobi parameters <https://docs.gurobi.com/projects/optimizer/en/current/reference/parameters.html>`_.

.. code-block:: python

   import gridops as go

   model = go.Model(
       region="west",
       problem="linear",
       solver_name="appsi_highs",
       solver_params={
           "presolve": "on",
           "solver": "ipm",
           "time_limit": 3600,
           "threads": 8,
           "log_to_console": False,
       },
   )

Warm starts
-----------

Consecutive horizons often have similar solutions. With warm starts enabled, the
solver begins each horizon from the previous horizon's basis. Set ``warmstart`` when
creating the model, or override it for one run with
``Model.run(..., warmstart=...)``. Depending on the solver and the setting, gridops
adjusts ``solver_params`` as follows:

.. list-table::
   :header-rows: 1
   :widths: 18 14 68

   * - Solver
     - Warm start setting (``warmstart=``)
     - Effective settings
   * - ``appsi_highs``
     - ``False`` (default)
     - ``solver="ipm"`` and ``run_crossover="on"`` unless you set them. The HiGHS
       state is cleared before every horizon after the first.
   * - ``appsi_highs``
     - ``True``
     - ``solver="simplex"`` and ``run_crossover="off"``, so the persistent
       interface reuses the previous basis.
   * - ``appsi_gurobi``
     - ``False``
     - ``LPWarmStart=0``. ``PreDual=1`` unless you set it.
   * - ``appsi_gurobi``
     - ``True``
     - ``LPWarmStart=1``, or keeps ``LPWarmStart=2`` if
       you set it. A user value of ``0`` is overridden with a warning.
   * - ``gurobi``
     - ``False``
     - ``PreDual=1`` unless you set it.
   * - ``gurobi``
     - ``True``
     - Switches to ``appsi_gurobi`` with ``LPWarmStart=1`` (or keeps ``2``) and logs a
       warning.

With HiGHS, choosing ``solver="simplex"`` always turns crossover off.

User guide
==========

This guide describes how gridops works and what it expects from you. It covers the
configuration file, the input and output data, the optimization model, and the
rolling-horizon simulation, including restarts and solver settings.

.. grid:: 1 1 2 2
   :gutter: 3

   .. grid-item-card:: Configuration file
      :link: configuration
      :link-type: doc

      Every YAML key, what it points to, and how paths are resolved.

   .. grid-item-card:: Input data
      :link: inputs
      :link-type: doc

      Layout, units and consistency rules for each input file.

   .. grid-item-card:: Outputs
      :link: outputs
      :link-type: doc

      Columns and units of the Parquet outputs and the solver audit file.

   .. grid-item-card:: Mathematical formulation
      :link: formulation
      :link-type: doc

      Sets, parameters, variables, objective and constraints of the Western
      Interconnection linear DC-OPF.

   .. grid-item-card:: Running simulations
      :link: simulation
      :link-type: doc

      Rolling horizons, state carry-over, outage adjustments, restart files and the
      retry/back-off logic.

   .. grid-item-card:: Solvers
      :link: solvers
      :link-type: doc

      Supported solvers, passing options, warm starts and the retry search grid.

Workflow at a glance
--------------------

.. code-block:: text

   example_config_file.yml ──► generate_config() ──► Config
                                                       │
   input CSV / NPY files ──► load_simulation_data() ◄──┘
                                   │
                                   ▼
                         build_west_linear()  (Pyomo ConcreteModel, built once)
                                   │
              ┌────────────────────┴─────────────────────┐
              │  for each horizon:                       │
              │    update time-varying parameters        │
              │    solve (HiGHS / Gurobi)                │
              │    collect results, carry state forward  │
              │    write restart file every N horizons   │
              └────────────────────┬─────────────────────┘
                                   ▼
                   Parquet outputs + solver_parameters.json

.. toctree::
   :maxdepth: 2
   :hidden:

   configuration
   inputs
   outputs
   formulation
   simulation
   solvers

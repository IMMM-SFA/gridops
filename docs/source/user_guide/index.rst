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

      Layout, units, and consistency rules for each input file.

   .. grid-item-card:: Output data
      :link: outputs
      :link-type: doc

      Layout and units of the Parquet outputs and the solver audit file.

   .. grid-item-card:: Mathematical formulation
      :link: formulation
      :link-type: doc

      Sets, parameters, variables, objective function, and constraints of the gridops.

   .. grid-item-card:: Running simulations
      :link: simulation
      :link-type: doc

      Rolling horizons, state carry-over, restart files, and the
      retry/back-off logic.

   .. grid-item-card:: Solvers
      :link: solvers
      :link-type: doc

      Supported solvers, passing options, and warm starts.

.. toctree::
   :maxdepth: 2
   :hidden:

   configuration
   inputs
   outputs
   formulation
   simulation
   solvers

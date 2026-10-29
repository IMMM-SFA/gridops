:html_theme.sidebar_secondary.remove:

gridops
=======

.. rst-class:: go-tagline

An open-source, customizable production cost model (PCM) for the U.S. interconnections.

.. rst-class:: go-meta

Version |release| · `Source <https://github.com/IMMM-SFA/gridops>`_ · `Issues and ideas <https://github.com/IMMM-SFA/gridops/issues>`_ · `Reference paper <https://doi.org/10.1088/2753-3751/ad1751>`_

.. code-block:: bash

   pip install gridops

**gridops** is a nodal grid operations model for three major U.S. interconnections
(Western, Eastern, and ERCOT). It uses a linear DC Optimal Power Flow (DC-OPF)
approximation to optimize hourly unit commitment and economic dispatch over a
rolling horizon that you configure. Pyomo builds the model, which can be solved
with the open-source (e.g., HiGHS) or commercial (e.g., Gurobi) solvers.

gridops was created to:

1. Address weather and water dynamics and associated vulnerabilities in U.S. bulk
   power systems.
2. Link with a wide range of hydrometeorological datasets and energy system/machine
   learning models to explore future uncertainty in grid operations.
3. Analyze current and future grid stress and reliability trends under a wide range of
   weather conditions, generation mixes, and demand growth scenarios.
4. Create simple and user-tailored representations of the U.S. interconnections that
   balance model accuracy and run time for the research question at hand.

.. figure:: _static/gridops_network_map.png
   :alt: Reduced network topology used by gridops
   :width: 100%
   :class: go-figure

   Reduced network topology represented in gridops. Three interconnections run separately.

.. grid:: 1 1 2 2
   :gutter: 3

   .. grid-item-card:: :fas:`rocket` Getting started
      :link: getting_started
      :link-type: doc

      What gridops does, which regions and problem types are available, and how to
      install the package and a solver.

   .. grid-item-card:: :fas:`play` Quickstart
      :link: notebooks/quickstarter
      :link-type: doc

      Run the bundled two-day Western Interconnection example notebook, then plot
      hourly locational marginal prices, unserved energy, and the generation mix.

   .. grid-item-card:: :fas:`book` User guide
      :link: user_guide/index
      :link-type: doc

      Configuration file reference, input data requirements, output data, the full
      mathematical formulation, rolling-horizon simulation, restarts, and solvers.

   .. grid-item-card:: :fas:`code` API reference
      :link: api
      :link-type: doc

      Detailed descriptions of every public class and function, the restart utilities, 
      and the grid operations model builder.

How it works
------------

.. grid:: 1 1 3 3
   :gutter: 3

   .. grid-item-card:: 1. Configure

      Point a YAML configuration file at the network, generator parameters, storage, 
      load, solar, wind, hydro, fuel price and generator outage inputs, and at the 
      model output destinations.

   .. grid-item-card:: 2. Optimize

      gridops builds one Pyomo DC-OPF model and solves it horizon by horizon. Before
      each solve it updates the time-varying parameters and carries generator output
      and storage state of charge forward.

   .. grid-item-card:: 3. Analyze

      Hourly generator dispatch, transmission line flows, voltage angles, unserved energy,
      locational marginal prices and storage operations are written to Parquet files.

The objective minimizes total system operating cost. The model enforces
nodal power balance, DC power flow, transmission line limits, generator ramp rates, 
hydro energy budgets, renewable availability, generator capacity losses, and storage dynamics. 
See :doc:`user_guide/formulation` for more detailed description and the full set of equations.

.. toctree::
   :hidden:
   :caption: User documentation

   getting_started
   Quickstart <notebooks/quickstarter>
   user_guide/index
   api
   contributing
   how_to_cite

.. toctree::
   :hidden:
   :caption: Project

   release_notes
   publications
   authors
   license
   acknowledgement

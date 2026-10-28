Input data
==========

This page describes every input file needed by the model. In the descriptions below, 
*bus* means a network node: a column name such as ``bus_100011`` that must be spelled 
the same way in every file.

.. note::

   Numeric inputs with an absolute value below ``1e-6`` are set to zero when they are
   loaded (see ``SNAP_TOL`` in :mod:`gridops.west.launch`). This avoids badly scaled
   coefficients in the solver.

Time coverage
-------------

Hourly files must have at least ``n_days * 24`` rows. Daily files must have at least
``n_days`` rows. Row ``i`` (0-based) of an hourly file is absolute hour ``i + 1``, and
row ``d`` (0-based) of a daily file is day ``d + 1``. The exception is
``lost_capacity_file``, which is indexed by its explicit 1-based ``Time`` column.

Network and load
----------------

``line_to_bus_file``
~~~~~~~~~~~~~~~~~~~~

Line-to-bus incidence matrix. The first column holds the line names, and each remaining
column is a bus. Each row has ``+1`` at the line's *from* bus, ``-1`` at its *to* bus
and ``0`` elsewhere. The row index defines the set of lines.

.. code-block:: text

   line,bus_100011,bus_100221,...
   line_301441_301741,0,0,...

``line_parameters_file``
~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 20 15 65

   * - Column
     - Unit
     - Description
   * - ``line``
     - –
     - Line name (index; must match line names in ``line_to_bus_file``).
   * - ``reactance``
     - p.u. (100 MVA base)
     - Line reactance. Together with the voltage angles at the two ends of a
       line, it determines how much power flows on a line.
   * - ``limit``
     - MW
     - Thermal line limit. The flow on the line can't exceed this value in either
       direction.

``nodal_load_file``
~~~~~~~~~~~~~~~~~~~

Hourly demand in MW. Rows are hours and columns are buses. **Every bus in the system must appear
here, even if its demand is zero** because the column names of this file define the model's set of buses.

Generators
----------

``generator_parameters_file``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

One row per generator (e.g., thermal, hydro, solar, onshore wind, and offshore wind). Nuclear units
are not listed here, they enter through ``must_run_file``.

.. list-table::
   :header-rows: 1
   :widths: 15 15 70

   * - Column
     - Unit
     - Description
   * - ``name``
     - –
     - Unique generator name.
   * - ``typ``
     - –
     - Generator type (see the accepted values below).
   * - ``node``
     - –
     - Bus where the unit is located. For hydro, solar, onshore wind, and offshore wind, this is
       the column read from the matching time-series file.
   * - ``maxcap``
     - MW
     - Maximum capacity.
   * - ``mincap``
     - MW
     - Minimum stable output (reserved for unit commitment).
   * - ``heat_rate``
     - MMBtu/MWh
     - Heat rate; fuel burned per MWh generated (thermal units).
   * - ``var_om``
     - $/MWh
     - Variable operation and maintenance (O&M) cost.
   * - ``no_load``
     - $/h
     - No-load cost (reserved for unit commitment).
   * - ``st_cost``
     - $/start
     - Start-up cost (reserved for unit commitment).
   * - ``ramp``
     - MW/h
     - Ramp rate; the largest change in output from one hour to the next (thermal
       units).
   * - ``minup``
     - h
     - Minimum up time (reserved for unit commitment).
   * - ``mindn``
     - h
     - Minimum down time (reserved for unit commitment).

Accepted ``typ`` values:

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Model set
     - ``typ`` values
   * - Coal
     - ``Coal``, ``coal``
   * - Oil
     - ``Oil``, ``oil``, ``Petroleum``, ``petroleum``
   * - Gas
     - ``NatGas``, ``Nat_Gas``, ``Natgas``, ``Nat_gas``, ``natgas``, ``nat_gas``,
       ``NaturalGas``, ``Natural_Gas``, ``Naturalgas``, ``Natural_gas``, ``naturalgas``,
       ``natural_gas``, ``Gas``, ``gas``, ``NGCC``, ``ngcc``,
       ``NGCT``, ``ngct``, ``NGST``, ``ngst``, ``NGGT``,
       ``nggt``, ``NG``, ``ng``, ``GT``, ``gt``
   * - Hydro
     - ``Hydro``, ``hydro``, ``Hydropower``,
       ``hydropower``, ``Hydro_power``, ``hydro_power``
   * - Solar
     - ``Solar``, ``solar``
   * - Wind
     - ``Wind``, ``wind``
   * - OffshoreWind
     - ``OffshoreWind``, ``Offshorewind``, ``Offshore_Wind``, ``Offshore_wind``,
       ``offshorewind``, ``offshore_wind``
   * - Biomass
     - ``Bio``, ``bio``, ``Biomass``, ``biomass``
   * - Geothermal
     - ``Geo``, ``geo``, ``Geothermal``, ``geothermal``

An unrecognized ``typ`` raises an error. Coal, Oil, Gas, Biomass and Geothermal
make up the **thermal** set. Coal and Gas units are also subject to generator outage
capacity losses.

``generator_matrix_file``
~~~~~~~~~~~~~~~~~~~~~~~~~

Generator-to-bus incidence matrix. The first column holds the generator names, and
each remaining column is a bus. A ``1`` places the generator's output in that bus's
power balance. Otherwise, ``0`` is written. It must agree with the ``node`` column of
``generator_parameters_file``.

.. code-block:: text

   name,bus_100011,bus_100221,...
   generator_x,0,1,...

``fuel_prices_file``
~~~~~~~~~~~~~~~~~~~~

Daily fuel price in $/MMBtu. Rows are days and columns are thermal generator
names. Every Coal, Oil, Gas, Biomass and Geothermal unit must have a column, or an
error is raised.

``must_run_file``
~~~~~~~~~~~~~~~~~

A single row of must-run (e.g., nuclear) capacity in MW. Only buses that have must-run
units need a column. This capacity is fixed, minus any nuclear generator outage losses
(see ``lost_capacity_file``), and is injected directly into the bus power balance.

``thermal_generators_file``
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Thermal fleet listing with columns ``Name``, ``Bus``, ``Fuel``, ``Max_Cap``,
``Min_Cap`` and ``Heat_Rate``. Only rows with ``Fuel == "NUC (Nuclear)"`` are used.
They give the number of nuclear units, which is needed to share the nuclear
generator outage losses among the units.

Hydropower
----------

The three hydro files have daily rows and bus columns. Each hydro generator reads
the column of its ``node``.

.. list-table::
   :header-rows: 1
   :widths: 30 15 55

   * - Key
     - Unit
     - Description
   * - ``daily_hydro_maximum_file``
     - MW
     - Maximum hourly output for that day.
   * - ``daily_hydro_minimum_file``
     - MW
     - Minimum hourly output for that day.
   * - ``daily_hydro_total_file``
     - MWh
     - Energy budget for that day. For horizons longer than 24 hours, the budgets of
       all ``horizon_hours // 24`` days are added up to give the horizon's budget.

Variable renewables
-------------------

``nodal_solar_file``, ``nodal_wind_file`` and ``nodal_offshore_wind_file`` give hourly
available generation in MW. Rows are hours and columns are buses. Each solar, wind
or offshore-wind generator reads the column of its ``node``. Missing columns are treated as zero.

Storage
-------

``storage_params_file``
~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 20 15 65

   * - Column
     - Unit
     - Description
   * - ``name``
     - –
     - Unique storage unit name.
   * - ``s_typ``
     - –
     - Storage technology label (e.g., ``battery`` or ``pumped_storage_hydro``).
   * - ``s_node``
     - –
     - Bus where the unit is located.
   * - ``charge_rate``
     - MW
     - Maximum charging power.
   * - ``discharge_rate``
     - MW
     - Maximum discharging power.
   * - ``duration``
     - h
     - Energy-to-power ratio.
   * - ``max_SoC``
     - MWh
     - Maximum state of charge.
   * - ``min_SoC``
     - MWh
     - Minimum state of charge. This is also the initial state of charge of a fresh
       run.
   * - ``charge_eff``
     - fraction (between 0 and 1)
     - Charging efficiency; the share of the power drawn from the grid that is
       stored.
   * - ``discharge_eff``
     - fraction (between 0 and 1)
     - Discharging efficiency; the share of the stored energy taken out that
       reaches the grid.

``bus_to_storage_matrix_file``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Storage-to-bus incidence matrix. The first column holds the storage names, and each
remaining column is a bus. A ``1`` places the storage unit's charge/discharge in that bus's
power balance. Otherwise, ``0`` is written. It must agree with the ``s_node`` column of
``storage_params_file``.

Generator outages
--------------

``generator_outage_file``
~~~~~~~~~~~~~~~~~~~~~~~~~

A NumPy ``.npy`` file containing a pickled ``dict`` that maps each outage-group name
to a list of generator names, for example:

.. code-block:: python

   import numpy as np

   groups = {
       "Gas_below_50": ["generator_x", ...],
       "Coal_200_300": ["generator_y", ...],
   }
   np.save("gen_outage_cat.npy", groups)

Requirements:

* Group names become Pyomo set names on the model, so they must be valid Python
  identifiers and must not clash with existing model component names.
* Groups may only contain **Coal**, **Gas**, and **Nuclear** generators. These are the generators
  that carry an hourly capacity limit.
* Each group name must also be a column of ``lost_capacity_file``. See ``gridops/data/example_inputs`` for an example ``generator_outage_file``.

``lost_capacity_file``
~~~~~~~~~~~~~~~~~~~~~~

Hourly capacity lost to generator outages, in MW. The first column must be ``Time``
(1-based absolute hour), followed by one column per outage group. Each group's loss
is split equally among its generators and subtracted from their maximum capacity. 
See ``gridops/data/example_inputs`` for an example ``lost_capacity_file``.

.. code-block:: text

   Time,Coal_100_200,Coal_200_300,...,Gas_ovr_1000,...,Nuclear_ovr_1000
   1,0.0,0.0,...,0.0,...,0.0

Example dataset
---------------

The example inputs in ``gridops/data/example_inputs`` describe a 125-bus,
786-line reduced topology of the Western Interconnection covering 48 hours. 
Please refer to ``gridops/data/example_inputs`` for guidance on the required 
file structures.

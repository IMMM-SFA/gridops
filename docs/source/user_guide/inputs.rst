Input data
==========

This page describes every input file read by the Western Interconnection linear model.
In the descriptions below, *bus* means a network node: a column name such as
``bus_100011`` that must be spelled the same way in every file.

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

Network
-------

``line_to_bus_file``
~~~~~~~~~~~~~~~~~~~~

DC-OPF incidence matrix. The first column holds the line names, and each remaining
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
     - Line name (index; must match ``line_to_bus_file``).
   * - ``reactance``
     - p.u. (100 MVA base)
     - Series reactance :math:`X_l`.
   * - ``limit``
     - MW
     - Thermal limit :math:`\overline{F}_l`. Flows are bounded to
       :math:`[-\overline{F}_l, \overline{F}_l]`.

``nodal_load_file``
~~~~~~~~~~~~~~~~~~~

Hourly demand in MW. Rows are hours and **columns are buses**. The column names of
this file define the model's set of buses, so every bus in the system must appear
here, even if its demand is zero.

Generators
----------

``generator_parameters_file``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

One row per generator (thermal, hydro, wind, solar and offshore wind). Nuclear units
are not listed here; they enter through ``must_run_file``.

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
     - Bus where the unit is located. For hydro, wind, solar and offshore wind, this is
       the column read from the matching time-series file.
   * - ``maxcap``
     - MW
     - Maximum capacity :math:`\overline{P}_g`.
   * - ``mincap``
     - MW
     - Minimum stable output (reserved for unit commitment).
   * - ``heat_rate``
     - MMBtu/MWh
     - Heat rate :math:`HR_g` (thermal units).
   * - ``var_om``
     - $/MWh
     - Variable O&M cost :math:`VOM_g`.
   * - ``no_load``
     - $/h
     - No-load cost (reserved for unit commitment).
   * - ``st_cost``
     - $/start
     - Start-up cost (reserved for unit commitment).
   * - ``ramp``
     - MW/h
     - Ramp rate :math:`R_g` (thermal units).
   * - ``minup``
     - h
     - Minimum up time (reserved for unit commitment).
   * - ``mindn``
     - h
     - Minimum down time (reserved for unit commitment).

Accepted ``typ`` values (case variants shown are all recognized):

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
     - ``Gas``, ``NatGas``, ``Nat_Gas``, ``NaturalGas``, ``Natural_Gas``, ``NG``,
       ``NGCC``, ``NGCT``, ``NGST``, ``NGGT``, ``GT`` (and their lower/mixed-case forms)
   * - Hydro
     - ``Hydro``, ``Hydropower``, ``Hydro_power`` (and lower-case forms)
   * - Solar
     - ``Solar``, ``solar``
   * - Wind
     - ``Wind``, ``wind``
   * - OffshoreWind
     - ``OffshoreWind``, ``Offshorewind``, ``Offshore_Wind``, ``Offshore_wind``,
       ``offshorewind``, ``offshore_wind``
   * - Biomass
     - ``Biomass``, ``Bio`` (and lower-case forms)
   * - Geothermal
     - ``Geothermal``, ``Geo`` (and lower-case forms)

An unrecognized ``typ`` raises a ``ValueError``. Coal, Oil, Gas, Biomass and Geothermal
make up the **thermal** set. Coal and Gas units are also subject to forced-outage
capacity losses.

``generator_matrix_file``
~~~~~~~~~~~~~~~~~~~~~~~~~

Generator-to-bus incidence matrix. The first column holds the generator names, and
each remaining column is a bus. A ``1`` places the generator's output in that bus's
power balance. It must agree with the ``node`` column of
``generator_parameters_file``.

``fuel_prices_file``
~~~~~~~~~~~~~~~~~~~~

Daily fuel price in $/MMBtu. Rows are days and **columns are thermal generator
names**. Every Coal, Oil, Gas, Biomass and Geothermal unit must have a column, or a
``ValueError`` is raised. The marginal cost of a thermal unit is
:math:`HR_g \cdot FP_{g} + VOM_g`.

``must_run_file``
~~~~~~~~~~~~~~~~~

A single row of must-run (nuclear) capacity in MW. Only buses that have must-run
units need a column. This capacity is fixed, minus any nuclear forced-outage losses
(see ``lost_capacity_file``), and is injected directly into the bus balance.

``thermal_generators_file``
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Thermal fleet listing with columns ``Name``, ``Bus``, ``Fuel``, ``Max_Cap``,
``Min_Cap`` and ``Heat_Rate``. Only rows with ``Fuel == "NUC (Nuclear)"`` are used,
to count the number of nuclear units :math:`N^{nuc}` that share the nuclear
forced-outage losses.

Hydropower
----------

The three hydro files have daily rows and **bus columns**. Each hydro generator reads
the column of its ``node``.

.. list-table::
   :header-rows: 1
   :widths: 30 15 55

   * - Key
     - Unit
     - Description
   * - ``daily_hydro_maximum_file``
     - MW
     - Maximum hourly output for that day, :math:`\overline{H}_{g}`.
   * - ``daily_hydro_minimum_file``
     - MW
     - Minimum hourly output for that day, :math:`\underline{H}_{g}`.
   * - ``daily_hydro_total_file``
     - MWh
     - Energy budget for that day. For horizons longer than 24 hours, the budgets of
       all ``horizon_hours // 24`` days are summed into :math:`E^{H}_{g}`.

Variable renewables
-------------------

``nodal_solar_file``, ``nodal_wind_file`` and ``nodal_offshore_wind_file`` give hourly
available generation in MW. Rows are hours and columns are buses. Each solar, wind
or offshore-wind generator is capped by the value in the column of its ``node``.
Missing columns are treated as zero.

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
     - Unique storage unit name (defines the storage set).
   * - ``s_typ``
     - –
     - Storage technology label (for example ``battery`` or ``pumped_storage_hydro``).
   * - ``s_node``
     - –
     - Bus where the unit is located.
   * - ``charge_rate``
     - MW
     - Maximum charging power :math:`\overline{C}_s`.
   * - ``discharge_rate``
     - MW
     - Maximum discharging power :math:`\overline{D}_s`.
   * - ``duration``
     - h
     - Energy-to-power ratio (informational).
   * - ``max_SoC``
     - MWh
     - Maximum state of charge :math:`\overline{SoC}_s`.
   * - ``min_SoC``
     - MWh
     - Minimum state of charge :math:`\underline{SoC}_s`. This is also the initial
       state of charge of a fresh run.
   * - ``charge_eff``
     - fraction
     - Charging efficiency :math:`\eta^{c}_s`.
   * - ``discharge_eff``
     - fraction
     - Discharging efficiency :math:`\eta^{d}_s`.

``bus_to_storage_matrix_file``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Storage-to-bus incidence matrix. The first column holds the storage names, and each
remaining column is a bus (0/1).

Forced outages
--------------

``generator_outage_file``
~~~~~~~~~~~~~~~~~~~~~~~~~

A NumPy ``.npy`` file containing a pickled ``dict`` that maps each outage-group name
to a list of generator names, for example:

.. code-block:: python

   import numpy as np

   groups = {
       "Gas_below_50": ["ID_c_20110386", ...],
       "Coal_200_300": [...],
   }
   np.save("gen_outage_cat.npy", groups)

Requirements:

* Group names become Pyomo set names on the model, so they must be valid Python
  identifiers and must not clash with existing model component names.
* Groups may only contain **Coal** and **Gas** generators. These are the generators
  that carry an hourly capacity limit.
* Each group name must also be a column of ``lost_capacity_file``.

``lost_capacity_file``
~~~~~~~~~~~~~~~~~~~~~~

Hourly capacity lost to forced outages, in MW. The first column must be ``Time``
(1-based absolute hour), followed by one column per outage group. Each group's loss
is split equally among its generators and subtracted from their maximum capacity.

If the system has nuclear units, a ``Nuclear_ovr_1000`` column is also required. Its
value is divided by :math:`N^{nuc}` and subtracted from the must-run capacity of
every bus. Additional columns are ignored.

.. code-block:: text

   Time,Coal_100_200,Coal_200_300,...,Gas_ovr_1000,...,Nuclear_ovr_1000
   1,0.0,0.0,...,0.0,...,0.0

Example dataset
---------------

The example inputs in ``gridops/data/example_inputs`` describe a 125-bus,
786-line reduction of the Western Interconnection for 48 hours:

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - File
     - Shape (rows × columns)
   * - ``data_genparams.csv``
     - 1,696 generators × 12
   * - ``gen_mat.csv``
     - 1,696 × (name + 125 buses)
   * - ``line_to_bus.csv``
     - 786 × (line + 125 buses)
   * - ``line_param.csv``
     - 786 × 3
   * - ``nodal_load.csv``, ``nodal_solar.csv``, ``nodal_wind.csv``, ``nodal_offshore_wind.csv``
     - 48 hours × 125 buses
   * - ``hydro_max.csv``, ``hydro_min.csv``, ``hydro_total.csv``
     - 2 days × 125 buses
   * - ``fuel_prices.csv``
     - 2 days × 1,508 thermal generators
   * - ``must_run.csv``
     - 1 × 3 buses
   * - ``storage_params.csv``
     - 64 units × 10
   * - ``storage_mat.csv``
     - 64 × (name + 125 buses)
   * - ``thermal_gens.csv``
     - 1,514 units × 6 (including 6 nuclear units)
   * - ``lost_capacity.csv``
     - 48 hours × (Time + 36 groups)
   * - ``gen_outage_cat.npy``
     - 24 outage groups

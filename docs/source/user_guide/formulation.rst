Mathematical formulation
========================

This page documents the linear economic dispatch model for the U.S. Western
Interconnection, built by :func:`gridops.west.linear.build_west_linear`. The same
problem is solved for every horizon of :math:`H` hours (``horizon_hours``). Only the
time-varying parameters change between horizons, together with the initial
generator output and storage state of charge carried over from the previous horizon.

Nomenclature
------------

Sets
~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Symbol
     - Description
   * - :math:`\mathcal{T} = \{1, \dots, H\}`
     - Hours in the current horizon.
   * - :math:`\mathcal{B}`
     - Buses (columns of ``nodal_load_file``). :math:`b^{ref}` is the reference bus.
   * - :math:`\mathcal{L}`
     - Transmission lines.
   * - :math:`\mathcal{G}`
     - All generators: :math:`\mathcal{G}^{TH} \cup \mathcal{G}^{HY} \cup \mathcal{G}^{S} \cup \mathcal{G}^{W} \cup \mathcal{G}^{OW}`.
   * - :math:`\mathcal{G}^{TH}`
     - Thermal generators: Coal, Oil, Gas, Biomass and Geothermal.
   * - :math:`\mathcal{G}^{O} \subseteq \mathcal{G}^{TH}`
     - Outage-eligible generators: Coal and Gas.
   * - :math:`\mathcal{G}^{HY}, \mathcal{G}^{S}, \mathcal{G}^{W}, \mathcal{G}^{OW}`
     - Hydro, solar, onshore wind and offshore wind generators.
   * - :math:`\mathcal{G}^{D} = \mathcal{G}^{TH} \cup \mathcal{G}^{HY}`
     - Dispatchable generators.
   * - :math:`\mathcal{G}_b`, :math:`\mathcal{S}_b`
     - Generators and storage units located at bus :math:`b`.
   * - :math:`\mathcal{S}`
     - Storage units.
   * - :math:`\mathcal{K}`, :math:`\mathcal{G}_k`
     - Outage groups and the generators in group :math:`k`.

Parameters
~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Symbol
     - Unit
     - Description
   * - :math:`D_{b,t}`
     - MW
     - Demand at bus :math:`b`.
   * - :math:`A_{l,b}`
     - –
     - Line-to-bus incidence (:math:`+1` from bus, :math:`-1` to bus).
   * - :math:`X_l`, :math:`\overline{F}_l`
     - p.u., MW
     - Line reactance and thermal limit.
   * - :math:`S^{base}`
     - MVA
     - Per-unit power base, ``PU_BASE_MVA`` = 100.
   * - :math:`\overline{P}_g`, :math:`R_g`
     - MW, MW/h
     - Maximum capacity and ramp rate.
   * - :math:`HR_g`, :math:`VOM_g`
     - MMBtu/MWh, $/MWh
     - Heat rate and variable O&M cost.
   * - :math:`FP_g`
     - $/MMBtu
     - Fuel price on the day of the horizon's first hour.
   * - :math:`\overline{P}_{g,t}`
     - MW
     - Outage-adjusted capacity of :math:`g \in \mathcal{G}^{O}`.
   * - :math:`\Delta_{g,t}`
     - MW
     - Ramp-down allowance caused by a drop in outage-adjusted capacity.
   * - :math:`\underline{H}_g`, :math:`\overline{H}_g`
     - MW
     - Daily minimum and maximum hourly hydro output.
   * - :math:`E^{H}_g`
     - MWh
     - Hydro energy budget for the horizon.
   * - :math:`AV_{g,t}`
     - MW
     - Available solar, wind or offshore-wind generation at the unit's bus.
   * - :math:`MR_{b,t}`
     - MW
     - Must-run (nuclear) injection at bus :math:`b`, net of outages.
   * - :math:`L_{k,t}`, :math:`L^{nuc}_t`
     - MW
     - Capacity lost in outage group :math:`k` and in the nuclear fleet.
   * - :math:`N^{nuc}`
     - –
     - Number of nuclear units.
   * - :math:`\overline{C}_s`, :math:`\overline{D}_s`
     - MW
     - Maximum charge and discharge power.
   * - :math:`\underline{SoC}_s`, :math:`\overline{SoC}_s`
     - MWh
     - Minimum and maximum state of charge.
   * - :math:`\eta^{c}_s`, :math:`\eta^{d}_s`
     - –
     - Charge and discharge efficiencies.
   * - :math:`p^{0}_g`, :math:`SoC^{0}_s`
     - MW, MWh
     - Generation and state of charge at the end of the previous horizon.
   * - :math:`c^{LS}`
     - $/MWh
     - Unserved energy penalty, ``SLACK_PENALTY`` = 2000.
   * - :math:`c^{R}`
     - $/MWh
     - Renewable and hydro dispatch cost, ``RENEWABLE_GEN_COST`` = 0.01.
   * - :math:`c^{F}`
     - $/MWh
     - Absolute-flow penalty, ``DUMMY_FLOW_PENALTY`` = 0.01.
   * - :math:`c^{ST}`
     - $/MWh
     - Storage charge/discharge cost, ``STORAGE_COST`` = 0.001.

Decision variables
~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Symbol
     - Unit
     - Description
   * - :math:`p_{g,t} \ge 0`
     - MW
     - Generator output (Pyomo ``mwh``).
   * - :math:`s_{b,t} \ge 0`
     - MW
     - Unserved energy at bus :math:`b` (Pyomo ``S``).
   * - :math:`f_{l,t}`
     - MW
     - Line flow (Pyomo ``Flow``).
   * - :math:`\hat{f}_{l,t} \ge 0`
     - MW
     - Absolute-value proxy of the line flow (Pyomo ``DummyFlow``).
   * - :math:`\theta_{b,t}`
     - rad
     - Bus voltage angle (Pyomo ``Theta``).
   * - :math:`c_{s,t}, d_{s,t} \ge 0`
     - MW
     - Storage charge and discharge (Pyomo ``Charge``, ``Discharge``).
   * - :math:`e_{s,t}`
     - MWh
     - Storage state of charge (Pyomo ``SoC``).

Objective
---------

Minimize total system operating cost over the horizon:

.. math::

   \min \sum_{t \in \mathcal{T}} \Bigg[
       \sum_{g \in \mathcal{G}^{TH}} \left( HR_g \, FP_g + VOM_g \right) p_{g,t}
       + c^{LS} \sum_{b \in \mathcal{B}} s_{b,t}
       + c^{R} \sum_{g \in \mathcal{G}^{HY} \cup \mathcal{G}^{S} \cup \mathcal{G}^{W} \cup \mathcal{G}^{OW}} p_{g,t}
       + c^{F} \sum_{l \in \mathcal{L}} \hat{f}_{l,t}
       + c^{ST} \sum_{s \in \mathcal{S}} \left( c_{s,t} + d_{s,t} \right)
   \Bigg]

The fuel and O&M term is the only economically meaningful cost. The remaining
terms do the following:

* make load shedding a last resort (:math:`c^{LS}`),
* break ties between zero-cost resources so the dispatch is unique (:math:`c^{R}`),
* discourage needless circulating flows (:math:`c^{F}`),
* stop storage from charging and discharging at the same time (:math:`c^{ST}`).

Constraints
-----------

Bus power balance
~~~~~~~~~~~~~~~~~

Kirchhoff's current law at every bus and hour. Its dual variable
:math:`\lambda_{b,t}` is the **locational marginal price** written to ``duals_file``.

.. math::

   \sum_{g \in \mathcal{G}_b} p_{g,t} + s_{b,t} + MR_{b,t}
   - \sum_{l \in \mathcal{L}} A_{l,b} \, f_{l,t}
   = D_{b,t} + \sum_{s \in \mathcal{S}_b} \left( c_{s,t} - d_{s,t} \right)
   \qquad \forall b \in \mathcal{B},\ t \in \mathcal{T}

DC power flow
~~~~~~~~~~~~~

.. math::

   \begin{aligned}
   X_l \, f_{l,t} &= S^{base} \sum_{b \in \mathcal{B}} A_{l,b} \, \theta_{b,t}
       && \forall l \in \mathcal{L},\ t \in \mathcal{T} \\
   -\overline{F}_l \le f_{l,t} &\le \overline{F}_l
       && \forall l \in \mathcal{L},\ t \in \mathcal{T} \\
   \theta_{b^{ref},t} &= 0
       && \forall t \in \mathcal{T} \\
   -\pi \le \theta_{b,t} &\le \pi
       && \forall b \in \mathcal{B},\ t \in \mathcal{T}
   \end{aligned}

The reference bus is ``REFERENCE_BUS`` (``bus_100011``). The angle bound is
implemented as :math:`\pm 3.1415`.

Absolute-flow linearization
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. math::

   \hat{f}_{l,t} \ge f_{l,t}, \qquad \hat{f}_{l,t} \ge -f_{l,t}
   \qquad \forall l \in \mathcal{L},\ t \in \mathcal{T}

Generator capacity
~~~~~~~~~~~~~~~~~~

.. math::

   \begin{aligned}
   p_{g,t} &\le \overline{P}_{g,t}
       && \forall g \in \mathcal{G}^{O},\ t \in \mathcal{T} \\
   p_{g,t} &\le \overline{P}_g
       && \forall g \in \mathcal{G}^{D} \setminus \mathcal{G}^{O},\ t \in \mathcal{T}
   \end{aligned}

The outage-adjusted capacity removes each group's lost capacity, split equally among
the group's members, and never goes below zero:

.. math::

   \overline{P}_{g,t} = \max\!\left(0,\ \overline{P}_g
       - \sum_{k \in \mathcal{K} : g \in \mathcal{G}_k} \frac{L_{k,t}}{|\mathcal{G}_k|} \right)

Ramp rates
~~~~~~~~~~

.. math::

   \begin{aligned}
   p_{g,t} - p_{g,t-1} &\le R_g
       && \forall g \in \mathcal{G}^{TH},\ t \in \mathcal{T} \\
   p_{g,t-1} - p_{g,t} &\le R_g + \Delta_{g,t}
       && \forall g \in \mathcal{G}^{TH},\ t \in \mathcal{T}
   \end{aligned}

where :math:`p_{g,0} = p^{0}_g` is the output in the last hour of the previous
horizon. The ramp-down allowance lets a unit drop as fast as a forced outage removes
its capacity:

.. math::

   \Delta_{g,t} =
   \begin{cases}
     \max\!\left(0,\ \overline{P}_{g,t-1} - \overline{P}_{g,t}\right) & g \in \mathcal{G}^{O},\ t > 1 \\
     \max\!\left(0,\ p^{0}_{g} - \overline{P}_{g,1}\right) & g \in \mathcal{G}^{O},\ t = 1 \\
     0 & g \in \mathcal{G}^{TH} \setminus \mathcal{G}^{O}
   \end{cases}

Both ramp constraints are switched off for :math:`t = 1` of the very first horizon of
a fresh run, because there is no previous dispatch yet.

Hydropower
~~~~~~~~~~

.. math::

   \begin{aligned}
   \underline{H}_g \le p_{g,t} &\le \overline{H}_g
       && \forall g \in \mathcal{G}^{HY},\ t \in \mathcal{T} \\
   \sum_{t \in \mathcal{T}} p_{g,t} &\le E^{H}_g
       && \forall g \in \mathcal{G}^{HY}
   \end{aligned}

Variable renewables
~~~~~~~~~~~~~~~~~~~

.. math::

   p_{g,t} \le AV_{g,t}
   \qquad \forall g \in \mathcal{G}^{S} \cup \mathcal{G}^{W} \cup \mathcal{G}^{OW},\ t \in \mathcal{T}

Must-run generation
~~~~~~~~~~~~~~~~~~~

Nuclear output is not a decision variable. It is a fixed injection, reduced by the
fleet-wide nuclear outage split across the nuclear units:

.. math::

   MR_{b,t} = \max\!\left(0,\ MR_b - \frac{L^{nuc}_t}{N^{nuc}} \right)
   \qquad \forall b \in \mathcal{B},\ t \in \mathcal{T}

Storage
~~~~~~~

.. math::

   \begin{aligned}
   e_{s,t} &= e_{s,t-1} + \eta^{c}_s \, c_{s,t} - \frac{d_{s,t}}{\eta^{d}_s}
       && \text{state-of-charge balance} \\
   c_{s,t} &\le \frac{\overline{SoC}_s - e_{s,t-1}}{\eta^{c}_s}
       && \text{charge headroom} \\
   d_{s,t} &\le \left( e_{s,t-1} - \underline{SoC}_s \right) \eta^{d}_s
       && \text{available energy} \\
   d_{s,t} &\le \overline{D}_s - \frac{\overline{D}_s}{\overline{C}_s} \, c_{s,t}
       && \text{joint charge/discharge limit} \\
   0 \le c_{s,t} \le \overline{C}_s, \quad
   0 \le d_{s,t} &\le \overline{D}_s, \quad
   \underline{SoC}_s \le e_{s,t} \le \overline{SoC}_s
       && \text{bounds}
   \end{aligned}

These hold for all :math:`s \in \mathcal{S}` and :math:`t \in \mathcal{T}`, with
:math:`e_{s,0} = SoC^{0}_s`. A fresh run starts every unit at
:math:`\underline{SoC}_s`.

Pyomo component reference
-------------------------

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Pyomo component
     - Equation
   * - ``SystemCost``
     - Objective
   * - ``Bus_Constraint``
     - Bus power balance
   * - ``DC_Flow_Constraint``, ``ThetaB_Constraint``
     - DC power flow, reference angle
   * - ``DummyFlow1_Constraint``, ``DummyFlow2_Constraint``
     - Absolute-flow linearization
   * - ``MaxCap``, ``MaxCap2``
     - Capacity of outage-eligible and other dispatchable generators
   * - ``RampCon1``, ``RampCon2``
     - Ramp up, ramp down
   * - ``HydroMAX``, ``HydroMIN``, ``HydroTOTAL``
     - Hydropower limits and energy budget
   * - ``SolarConstraint``, ``WindConstraint``, ``OffshoreWindConstraint``
     - Renewable availability
   * - ``SoCBalance_Constraint``, ``MaxCharge_Constraint``, ``MaxDischarge_Constraint``, ``SimChargeDischarge_Constraint``
     - Storage

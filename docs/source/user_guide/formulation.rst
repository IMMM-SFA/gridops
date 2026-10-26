Mathematical formulation
========================

This page documents the linear economic dispatch model for the U.S. Western
Interconnection, built by :func:`gridops.west.linear.build_west_linear`.

Overview
--------

gridops solves a **linear program (LP)** that decides, hour by hour, how much power
each generator produces, how much each storage unit charges or discharges and how
power flows over the transmission network, so that demand is met at the lowest total
operating cost.

The main modeling choices are:

* **Hourly time step.** Every decision is made for one-hour intervals. Because each
  interval lasts one hour, a power level in MW equals an energy amount in MWh, and
  costs in $/MWh multiply power directly.
* **Rolling horizon.** The simulation period is split into horizons of :math:`H`
  hours (``horizon_hours``). The same LP is solved for every horizon. Only the
  time-varying parameters change between horizons, together with the generator
  output and storage state of charge carried over from the end of the previous
  horizon (see :doc:`simulation`).
* **Economic dispatch.** Units have no on/off (commitment) decisions, minimum stable
  output, start-up or no-load costs, so the model stays linear and continuous.
* **DC power flow.** The network is represented by the linearized (DC) power-flow
  approximation: voltage magnitudes are fixed at 1 p.u., line resistance and losses
  are ignored, and the flow on a line is proportional to the difference in voltage
  angle between its two ends.
* **Load shedding as a last resort.** Each bus can shed load at a high penalty
  cost, so the problem always has a feasible solution. The amount shed is reported
  as unserved energy.

Nomenclature
------------

Calligraphic letters denote sets, upper-case letters denote parameters (input data)
and lower-case letters denote decision variables. Subscripts give the index: :math:`g`
for generators, :math:`b` for buses, :math:`l` for lines, :math:`s` for storage
units, :math:`k` for outage groups and :math:`t` for hours.

Sets
~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Symbol
     - Description
   * - :math:`\mathcal{T} = \{1, \dots, H\}`
     - Hours in the current horizon.
   * - :math:`\mathcal{B}`
     - Buses (columns of ``nodal_load_file``). :math:`b^{ref} \in \mathcal{B}` is the
       reference bus.
   * - :math:`\mathcal{L}`
     - Transmission lines.
   * - :math:`\mathcal{G}`
     - All generators: :math:`\mathcal{G}^{TH} \cup \mathcal{G}^{HY} \cup \mathcal{G}^{S} \cup \mathcal{G}^{W} \cup \mathcal{G}^{OW}`.
   * - :math:`\mathcal{G}^{TH}`
     - Thermal generators: Coal, Oil, Gas, Biomass and Geothermal.
   * - :math:`\mathcal{G}^{O} \subseteq \mathcal{G}^{TH}`
     - Outage-eligible generators: Coal and Gas.
   * - :math:`\mathcal{G}^{HY}`, :math:`\mathcal{G}^{S}`, :math:`\mathcal{G}^{W}`, :math:`\mathcal{G}^{OW}`
     - Hydro, solar, onshore wind and offshore wind generators.
   * - :math:`\mathcal{G}^{VRE} = \mathcal{G}^{S} \cup \mathcal{G}^{W} \cup \mathcal{G}^{OW}`
     - Variable renewable generators.
   * - :math:`\mathcal{G}^{D} = \mathcal{G}^{TH} \cup \mathcal{G}^{HY}`
     - Dispatchable generators.
   * - :math:`\mathcal{S}`
     - Storage units.
   * - :math:`\mathcal{G}_b \subseteq \mathcal{G}`, :math:`\mathcal{S}_b \subseteq \mathcal{S}`
     - Generators and storage units located at bus :math:`b`.
   * - :math:`\mathcal{K}`
     - Outage groups.
   * - :math:`\mathcal{G}_k \subseteq \mathcal{G}^{O}`
     - Generators in outage group :math:`k`. :math:`|\mathcal{G}_k|` is the number of
       generators in the group.

Parameters
~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 15 55

   * - Symbol
     - Unit
     - Description
   * - :math:`D_{b,t}`
     - MW
     - Demand at bus :math:`b` in hour :math:`t`.
   * - :math:`A_{l,b}`
     - –
     - Line-to-bus incidence: :math:`+1` if bus :math:`b` is the *from* bus of line
       :math:`l`, :math:`-1` if it is the *to* bus, :math:`0` otherwise.
   * - :math:`X_l`
     - p.u.
     - Line reactance.
   * - :math:`\overline{F}_l`
     - MW
     - Line thermal limit.
   * - :math:`S^{base}`
     - MVA
     - Per-unit power base, ``PU_BASE_MVA`` = 100.
   * - :math:`\overline{P}_g`
     - MW
     - Maximum (nameplate) capacity of generator :math:`g`.
   * - :math:`\overline{P}^{O}_{g,t}`
     - MW
     - Outage-adjusted capacity of :math:`g \in \mathcal{G}^{O}` in hour :math:`t`.
   * - :math:`R_g`
     - MW/h
     - Ramp rate of generator :math:`g`.
   * - :math:`HR_g`
     - MMBtu/MWh
     - Heat rate of generator :math:`g`.
   * - :math:`VOM_g`
     - $/MWh
     - Variable operation and maintenance cost of generator :math:`g`.
   * - :math:`FP_g`
     - $/MMBtu
     - Fuel price of generator :math:`g` on the day of the horizon's first hour.
   * - :math:`\Delta_{g,t}`
     - MW
     - Ramp-down allowance caused by a drop in outage-adjusted capacity.
   * - :math:`\underline{H}_g`, :math:`\overline{H}_g`
     - MW
     - Minimum and maximum hourly hydro output on the day of the horizon's first
       hour.
   * - :math:`E^{H}_g`
     - MWh
     - Hydro energy budget for the horizon.
   * - :math:`AV_{g,t}`
     - MW
     - Available solar, wind or offshore-wind generation at the bus of generator
       :math:`g`.
   * - :math:`\overline{MR}_b`
     - MW
     - Must-run (nuclear) capacity at bus :math:`b`.
   * - :math:`MR_{b,t}`
     - MW
     - Must-run injection at bus :math:`b` in hour :math:`t`, net of nuclear
       outages.
   * - :math:`L_{k,t}`
     - MW
     - Capacity lost to forced outages in outage group :math:`k`.
   * - :math:`L^{nuc}_t`
     - MW
     - Capacity lost to forced outages in the nuclear fleet.
   * - :math:`N^{nuc}`
     - –
     - Number of nuclear units.
   * - :math:`\overline{P}^{ch}_s`, :math:`\overline{P}^{dis}_s`
     - MW
     - Maximum charging and discharging power of storage unit :math:`s`.
   * - :math:`\underline{SoC}_s`, :math:`\overline{SoC}_s`
     - MWh
     - Minimum and maximum state of charge.
   * - :math:`\eta^{ch}_s`, :math:`\eta^{dis}_s`
     - –
     - Charging and discharging efficiencies, between 0 and 1.
   * - :math:`p^{0}_g`
     - MW
     - Output of thermal generator :math:`g` in the last hour of the previous horizon.
   * - :math:`SoC^{0}_s`
     - MWh
     - State of charge of storage unit :math:`s` at the end of the previous horizon.
   * - :math:`\gamma^{LS}`
     - $/MWh
     - Unserved energy penalty, ``SLACK_PENALTY`` = 2000.
   * - :math:`\gamma^{R}`
     - $/MWh
     - Hydro and variable renewable dispatch cost, ``RENEWABLE_GEN_COST`` = 0.01.
   * - :math:`\gamma^{F}`
     - $/MWh
     - Absolute-flow penalty, ``DUMMY_FLOW_PENALTY`` = 0.01.
   * - :math:`\gamma^{ST}`
     - $/MWh
     - Storage charge/discharge cost, ``STORAGE_COST`` = 0.001.

Decision variables
~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 15 55

   * - Symbol
     - Unit
     - Description
   * - :math:`p_{g,t} \ge 0`
     - MW
     - Generator output (Pyomo ``mwh``).
   * - :math:`u_{b,t} \ge 0`
     - MW
     - Unserved energy (load shedding) at bus :math:`b` (Pyomo ``S``).
   * - :math:`f_{l,t}`
     - MW
     - Line flow, positive from the *from* bus to the *to* bus (Pyomo ``Flow``).
   * - :math:`\hat{f}_{l,t} \ge 0`
     - MW
     - Absolute value of the line flow (Pyomo ``DummyFlow``).
   * - :math:`\theta_{b,t}`
     - rad
     - Bus voltage angle (Pyomo ``Theta``).
   * - :math:`c_{s,t} \ge 0`
     - MW
     - Storage charging power (Pyomo ``Charge``).
   * - :math:`d_{s,t} \ge 0`
     - MW
     - Storage discharging power (Pyomo ``Discharge``).
   * - :math:`e_{s,t}`
     - MWh
     - Storage state of charge at the end of hour :math:`t` (Pyomo ``SoC``).

Objective
---------

The objective is to minimize the total system operating cost over the horizon:

.. math::

   \min \sum_{t \in \mathcal{T}} \Bigg[
       \sum_{g \in \mathcal{G}^{TH}} \left( HR_g \, FP_g + VOM_g \right) p_{g,t}
       + \gamma^{LS} \sum_{b \in \mathcal{B}} u_{b,t}
       + \gamma^{R} \sum_{g \in \mathcal{G}^{HY} \cup \mathcal{G}^{VRE}} p_{g,t}
       + \gamma^{F} \sum_{l \in \mathcal{L}} \hat{f}_{l,t}
       + \gamma^{ST} \sum_{s \in \mathcal{S}} \left( c_{s,t} + d_{s,t} \right)
   \Bigg]

The five terms are:

1. **Thermal generation cost.** The marginal cost of a thermal unit is the fuel it
   burns per MWh (heat rate :math:`HR_g`) times the fuel price :math:`FP_g`, plus the
   variable O&M cost :math:`VOM_g`. This is the only term that represents a real
   economic cost, and it determines the merit order: cheaper units are dispatched
   first.
2. **Unserved energy penalty.** :math:`\gamma^{LS}` = 2000 $/MWh is well above the
   marginal cost of generators, so the model sheds load only when no combination
   of generation, storage and transmission can meet demand.
3. **Hydro and renewable cost.** Hydro, solar and wind have no fuel cost. A small
   cost :math:`\gamma^{R}` breaks ties between these zero-cost resources so the
   dispatch is unique.
4. **Absolute-flow penalty.** A small cost :math:`\gamma^{F}` on the absolute value
   of every line flow discourages needless circulating flows that don't change the
   total cost.
5. **Storage cycling cost.** A small cost :math:`\gamma^{ST}` on charging and
   discharging stops a unit from charging and discharging in the same hour, which
   would otherwise waste energy through the efficiency losses at no cost.

Because the last four costs are small or are penalties, the objective value is not
exactly the system's operating cost. Use the dispatch and the LMPs in the
:doc:`outputs` for cost analyses.

Constraints
-----------

Bus power balance
~~~~~~~~~~~~~~~~~

At every bus and in every hour, the power injected must equal the power withdrawn
(Kirchhoff's current law):

.. math::

   \sum_{g \in \mathcal{G}_b} p_{g,t} + u_{b,t} + MR_{b,t}
   - \sum_{l \in \mathcal{L}} A_{l,b} \, f_{l,t}
   = D_{b,t} + \sum_{s \in \mathcal{S}_b} \left( c_{s,t} - d_{s,t} \right)
   \qquad \forall b \in \mathcal{B},\ t \in \mathcal{T}

The left-hand side is the supply at the bus: generation from the bus's generators,
unserved energy, must-run nuclear output, minus the net power leaving the bus over
transmission lines. Because :math:`A_{l,b} = +1` at a line's *from* bus and
:math:`-1` at its *to* bus, :math:`\sum_{l} A_{l,b} f_{l,t}` is the total flow leaving
bus :math:`b` minus the total flow entering it. The right-hand side is the demand at
the bus plus the net charging of the storage units located there.

The dual variable :math:`\lambda_{b,t}` of this constraint is the cost of serving one
more MW of demand at bus :math:`b` in hour :math:`t`. This is the **locational
marginal price (LMP)**, written to ``duals_file``. LMPs differ between buses when
transmission limits are binding (congestion). At buses where load is shed, the LMP
is set by the unserved energy penalty :math:`\gamma^{LS}`.

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

The first equation is the DC power-flow approximation. Since each line has one
*from* bus (:math:`A_{l,b} = +1`) and one *to* bus (:math:`A_{l,b} = -1`), the sum
equals the angle difference across the line, and the equation can be written as

.. math::

   f_{l,t} = S^{base} \, \frac{\theta_{from(l),t} - \theta_{to(l),t}}{X_l}

Power flows from the bus with the larger voltage angle to the bus with the smaller
one, and lines with lower reactance carry more of the flow. Reactance is given in
per unit, so multiplying by :math:`S^{base}` = 100 MVA converts the flow to MW.
Unlike a transport model, the flow on each line is fixed by the physics of the
network once the bus injections are known: the solver can't route power freely.

The second constraint keeps each flow within the line's thermal limit in both
directions. The third fixes the angle of the reference bus ``REFERENCE_BUS``
(``bus_100011``) at zero. Only angle differences matter, so without a reference the
angles would not be unique. The last constraint bounds the angles to
:math:`\pm\pi`, implemented as :math:`\pm 3.1415`.

Absolute-flow linearization
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. math::

   \hat{f}_{l,t} \ge f_{l,t}, \qquad \hat{f}_{l,t} \ge -f_{l,t}
   \qquad \forall l \in \mathcal{L},\ t \in \mathcal{T}

The absolute value :math:`|f_{l,t}|` is not a linear function, so it can't appear in
an LP directly. These two constraints make :math:`\hat{f}_{l,t}` at least as large as
both :math:`f_{l,t}` and :math:`-f_{l,t}`. Because :math:`\hat{f}_{l,t}` has a positive
cost in the objective, the solver pushes it down to the larger of the two, which is
exactly :math:`|f_{l,t}|`.

Generator capacity
~~~~~~~~~~~~~~~~~~

.. math::

   \begin{aligned}
   p_{g,t} &\le \overline{P}^{O}_{g,t}
       && \forall g \in \mathcal{G}^{O},\ t \in \mathcal{T} \\
   p_{g,t} &\le \overline{P}_g
       && \forall g \in \mathcal{G}^{D} \setminus \mathcal{G}^{O},\ t \in \mathcal{T}
   \end{aligned}

Coal and gas units are limited by their outage-adjusted capacity
:math:`\overline{P}^{O}_{g,t}`, which changes every hour. All other dispatchable units
(oil, biomass, geothermal and hydro) are limited by their nameplate capacity.

The outage-adjusted capacity represents forced outages, for which
``lost_capacity_file`` gives the total capacity lost in each outage group and hour.
The loss is split equally among the generators of the group and subtracted from
their nameplate capacity. Capacity can't be negative:

.. math::

   \overline{P}^{O}_{g,t} = \max\!\left(0,\ \overline{P}_g
       - \sum_{k \in \mathcal{K} : g \in \mathcal{G}_k} \frac{L_{k,t}}{|\mathcal{G}_k|} \right)
   \qquad \forall g \in \mathcal{G}^{O},\ t \in \mathcal{T}

:math:`\overline{P}^{O}_{g,t}` is computed before the solve, so the constraint stays
linear. Splitting the loss equally is an approximation: the input data says how much
capacity a group loses, not which units are out.

Ramp rates
~~~~~~~~~~

.. math::

   \begin{aligned}
   p_{g,t} - p_{g,t-1} &\le R_g
       && \forall g \in \mathcal{G}^{TH},\ t \in \mathcal{T} \\
   p_{g,t-1} - p_{g,t} &\le R_g + \Delta_{g,t}
       && \forall g \in \mathcal{G}^{TH},\ t \in \mathcal{T}
   \end{aligned}

Thermal units can't change their output faster than their ramp rate :math:`R_g`. The
first constraint limits how much output can increase from one hour to the next
(ramp up), and the second how much it can decrease (ramp down). For the first hour
of a horizon, the previous output is the output in the last hour of the previous
horizon: :math:`p_{g,0} = p^{0}_g`. This links consecutive horizons, so a unit can't
jump to a different output level at midnight.

A forced outage can remove capacity faster than the unit could ramp down. Without
an adjustment, the capacity limit and the ramp-down limit could then contradict each
other and make the problem infeasible. The ramp-down allowance :math:`\Delta_{g,t}`
relaxes the ramp-down limit by the size of the drop in outage-adjusted capacity:

.. math::

   \Delta_{g,t} =
   \begin{cases}
     \max\!\left(0,\ \overline{P}^{O}_{g,t-1} - \overline{P}^{O}_{g,t}\right) & g \in \mathcal{G}^{O},\ t > 1 \\
     \max\!\left(0,\ p^{0}_{g} - \overline{P}^{O}_{g,1}\right) & g \in \mathcal{G}^{O},\ t = 1 \\
     0 & g \in \mathcal{G}^{TH} \setminus \mathcal{G}^{O}
   \end{cases}

For :math:`t = 1`, the allowance compares the previous output (instead of the
previous capacity) with the new capacity, so a unit can always drop to its new limit
at the start of a horizon.

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

Hydropower is limited by the water available, which the model takes as given from
the daily hydro input files. These constraints describe what a hydro plant can do
with that water:

* The first constraint keeps the hourly output of every hydro unit between a minimum
  and a maximum. The minimum :math:`\underline{H}_g` represents required releases,
  such as minimum flows for the environment or navigation, that produce electricity
  whether or not it is needed. The maximum :math:`\overline{H}_g` reflects the
  turbine capacity and water conditions of the day.
* The second constraint is an **energy budget**: the total hydro generation over the
  horizon can't exceed the energy :math:`E^{H}_g` that the available water can
  produce. Within this budget, the model is free to shift hydro generation to the
  hours where it saves the most cost, typically the hours of highest demand.
  Generation may be lower than the budget.

The hourly limits use the values for the day of the horizon's first hour. The budget
is the sum of the daily budgets of all days in the horizon. Hydro units are also
subject to their nameplate capacity (see `Generator capacity`_).

Variable renewables
~~~~~~~~~~~~~~~~~~~

.. math::

   p_{g,t} \le AV_{g,t}
   \qquad \forall g \in \mathcal{G}^{VRE},\ t \in \mathcal{T}

Solar, onshore wind and offshore wind output depends on the weather, so it can't be
scheduled at will. :math:`AV_{g,t}` is the generation that the weather allows in each
hour, read from the nodal solar, wind and offshore wind files at the bus of each
unit.

The constraint is an inequality: a unit can produce up to the available amount but
may produce less. The difference, :math:`AV_{g,t} - p_{g,t}`, is **curtailment**.
Renewable energy is curtailed when using all of it would violate another constraint,
for example when transmission lines out of a region are congested or when must-run
and minimum hydro output already cover demand. The small cost :math:`\gamma^{R}`
means curtailment has almost no effect on the objective.

Must-run generation
~~~~~~~~~~~~~~~~~~~

Nuclear output is not a decision variable. Nuclear plants usually run at a constant
output, so the model treats them as a fixed injection :math:`MR_{b,t}` in the bus
power balance. The injection is the must-run capacity at the bus, reduced by the
fleet-wide nuclear forced-outage loss divided by the number of nuclear units:

.. math::

   MR_{b,t} = \max\!\left(0,\ \overline{MR}_b - \frac{L^{nuc}_t}{N^{nuc}} \right)
   \qquad \forall b \in \mathcal{B},\ t \in \mathcal{T}

The per-unit loss :math:`L^{nuc}_t / N^{nuc}` is subtracted once at every bus with
must-run capacity, and the result can't be negative. :math:`L^{nuc}_t` is the
``Nuclear_ovr_1000`` column of ``lost_capacity_file``. Because must-run output is
fixed, the other resources are dispatched around it.

Storage
~~~~~~~

.. math::

   \begin{aligned}
   e_{s,t} &= e_{s,t-1} + \eta^{ch}_s \, c_{s,t} - \frac{d_{s,t}}{\eta^{dis}_s}
       && \text{(1) state-of-charge balance} \\
   c_{s,t} &\le \frac{\overline{SoC}_s - e_{s,t-1}}{\eta^{ch}_s}
       && \text{(2) charging headroom} \\
   d_{s,t} &\le \left( e_{s,t-1} - \underline{SoC}_s \right) \eta^{dis}_s
       && \text{(3) available energy} \\
   \frac{c_{s,t}}{\overline{P}^{ch}_s} + \frac{d_{s,t}}{\overline{P}^{dis}_s} &\le 1
       && \text{(4) joint charge/discharge limit} \\
   0 \le c_{s,t} \le \overline{P}^{ch}_s, \quad
   0 \le d_{s,t} &\le \overline{P}^{dis}_s, \quad
   \underline{SoC}_s \le e_{s,t} \le \overline{SoC}_s
       && \text{(5) bounds}
   \end{aligned}

These hold for all :math:`s \in \mathcal{S}` and :math:`t \in \mathcal{T}`, with
:math:`e_{s,0} = SoC^{0}_s`, the state of charge at the end of the previous horizon.
A fresh run starts every unit at its minimum state of charge
:math:`\underline{SoC}_s`.

Storage units (batteries and pumped storage hydro) move energy in time: they charge
when power is cheap and discharge when it is expensive. The constraints work as
follows:

1. **State-of-charge balance.** The energy stored at the end of an hour is the energy
   at the end of the previous hour, plus the energy added by charging, minus the
   energy removed by discharging. Only the fraction :math:`\eta^{ch}_s` of the power
   drawn from the grid is stored, and :math:`1/\eta^{dis}_s` MWh must be removed from
   storage to deliver 1 MWh to the grid. The round-trip efficiency is
   :math:`\eta^{ch}_s \eta^{dis}_s`.
2. **Charging headroom.** A unit can't charge more than fits between the state of
   charge at the start of the hour and the maximum state of charge.
3. **Available energy.** A unit can't deliver more than the energy stored above its
   minimum state of charge at the start of the hour, after discharging losses.
4. **Joint charge/discharge limit.** Charging and discharging in the same hour share
   the unit's power capability. Charging at full power leaves no room for
   discharging, and vice versa. In the code this is written as
   :math:`d_{s,t} \le \overline{P}^{dis}_s - (\overline{P}^{dis}_s / \overline{P}^{ch}_s)\, c_{s,t}`.
   Together with the storage cycling cost in the objective, this keeps the model
   from charging and discharging at the same time.
5. **Bounds.** Charging and discharging power are limited by the unit's power
   ratings, and the state of charge stays within its limits.

The storage power enters the bus power balance at the unit's bus: charging is extra
demand and discharging is extra supply.

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
     - Variable renewable availability
   * - ``SoCBalance_Constraint``, ``MaxCharge_Constraint``, ``MaxDischarge_Constraint``, ``SimChargeDischarge_Constraint``
     - Storage (1), (2), (3) and (4)
   * - Variable bounds on ``Flow``, ``Theta``, ``Charge``, ``Discharge`` and ``SoC``
     - Line limits, angle bounds and storage bounds (5)

Mutable parameters updated before each horizon: ``HorizonDemand``, ``HorizonSolar``,
``HorizonWind``, ``HorizonOffshoreWind``, ``HorizonGenLimit``
(:math:`\overline{P}^{O}_{g,t}`), ``HorizonMustrunLimit`` (:math:`MR_{b,t}`),
``HorizonHydro_MAX``, ``HorizonHydro_MIN``, ``HorizonHydro_TOTAL``, ``FuelPrice``,
``InitialMwh`` (:math:`p^{0}_g`), ``InitialSoC`` (:math:`SoC^{0}_s`) and
``OutageAllowance`` (:math:`\Delta_{g,t}`).

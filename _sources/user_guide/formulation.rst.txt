Mathematical formulation
========================

This page documents the linear economic dispatch model utilized by gridops.

Overview
--------

gridops solves a linear program (LP) that decides, hour by hour, how much power
each generator produces, how much each storage unit charges or discharges and how
power flows over the transmission network, so that demand is met at the lowest total
operating cost.

The main modeling choices are:

* **Hourly time step:** Temporal resolution is hourly. Because each
  interval lasts one hour, a power level in MW equals an energy amount in MWh, and
  costs in $/MWh multiply power directly.
* **Rolling horizon:** The simulation period is split into horizons of :math:`H`
  hours (``horizon_hours``). The same LP is solved for every horizon. Only the
  time-varying parameters change between horizons, together with the generator
  output and storage state of charge carried over from the end of the previous
  horizon (see :doc:`simulation`).
* **Economic dispatch:** Generators have no on/off (commitment) decisions, minimum stable
  output, start-up or no-load costs, minimum up and down times, so the model stays 
  linear and continuous.
* **DC power flow:** The network is represented by the linearized DC power flow
  approximation. The flow on a transmissionline is proportional to the difference 
  in voltage angle between its two ends.
* **Load shedding as a last resort:** Each bus can shed load at a high penalty
  cost, so the problem always has a feasible solution. The load shedding amount 
  is reported as unserved energy.

Nomenclature
------------

Calligraphic letters denote sets, upper-case letters denote parameters
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
     - Buses. :math:`b^{ref} \in \mathcal{B}` is the
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
     - Line-to-bus incidence; :math:`+1` if bus :math:`b` is the *from* bus of line
       :math:`l`, :math:`-1` if it is the *to* bus, :math:`0` otherwise.
   * - :math:`X_l`
     - p.u.
     - Line reactance of line :math:`l`.
   * - :math:`\overline{F}_l`
     - MW
     - Line thermal limit of line :math:`l`.
   * - :math:`S^{base}`
     - MVA
     - Per-unit power base; equals to 100.
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
     - Fuel price of generator :math:`g` for the horizon.
   * - :math:`\Delta_{g,t}`
     - MW
     - Ramp-down allowance caused by a drop in generator outage adjusted capacity 
       for generator :math:`g` in hour :math:`t`.
   * - :math:`\underline{H}_g`, :math:`\overline{H}_g`
     - MW
     - Minimum and maximum hourly hydro output of generator :math:`g` for the horizon.
   * - :math:`E^{H}_g`
     - MWh
     - Hydro energy budget of generator :math:`g` for the horizon.
   * - :math:`AV_{g,t}`
     - MW
     - Available solar, wind or offshore-wind generation at the bus of generator
       :math:`g` in hour :math:`t`.
   * - :math:`\overline{MR}_b`
     - MW
     - Must-run (e.g., nuclear) capacity at bus :math:`b`.
   * - :math:`MR_{b,t}`
     - MW
     - Must-run injection at bus :math:`b` in hour :math:`t`, after considering nuclear
       generator outages.
   * - :math:`L_{k,t}`
     - MW
     - Capacity lost to generator outages in outage group :math:`k` in hour :math:`t`.
   * - :math:`L^{nuc}_t`
     - MW
     - Capacity lost to generator outages in nuclear generators in hour :math:`t`.
   * - :math:`N^{nuc}`
     - –
     - Number of nuclear units.
   * - :math:`\overline{P}^{ch}_s`, :math:`\overline{P}^{dis}_s`
     - MW
     - Maximum charging and discharging power of storage unit :math:`s`.
   * - :math:`\underline{SoC}_s`, :math:`\overline{SoC}_s`
     - MWh
     - Minimum and maximum state of charge of storage unit :math:`s`.
   * - :math:`\eta^{ch}_s`, :math:`\eta^{dis}_s`
     - –
     - Charging and discharging efficiencies of storage unit :math:`s`; between 0 and 1.
   * - :math:`p^{0}_g`
     - MW
     - Output of thermal generator :math:`g` at the end of the previous horizon.
   * - :math:`SoC^{0}_s`
     - MWh
     - State of charge of storage unit :math:`s` at the end of the previous horizon.
   * - :math:`\gamma^{LS}`
     - $/MWh
     - Unserved energy penalty; equals to 2000.
   * - :math:`\gamma^{R}`
     - $/MWh
     - Hydro and variable renewable dispatch cost; equals to 0.01.
   * - :math:`\gamma^{F}`
     - $/MWh
     - Absolute-flow penalty; equals to 0.01.
   * - :math:`\gamma^{ST}`
     - $/MWh
     - Storage charge/discharge cost; equals to 0.001.

Decision variables
~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 15 55

   * - Symbol
     - Unit
     - Description
   * - :math:`p_{g,t} \ge 0`
     - MWh
     - Hourly dispatch of each generator :math:`g` in hour :math:`t`.
   * - :math:`u_{b,t} \ge 0`
     - MWh
     - Hourly unserved energy (load shedding) at bus :math:`b` in hour :math:`t`.
   * - :math:`f_{l,t}`
     - MW
     - Hourly power flow at each transmission line :math:`l` in hour :math:`t`.
   * - :math:`\hat{f}_{l,t} \ge 0`
     - MW
     - Absolute value of hourly power flow at each transmission line :math:`l` in hour :math:`t`.
   * - :math:`\theta_{b,t}`
     - radian
     - Hourly voltage angle at each bus :math:`b` in hour :math:`t`.
   * - :math:`c_{s,t} \ge 0`
     - MW
     - Hourly power charged at each storage unit :math:`s` in hour :math:`t`.
   * - :math:`d_{s,t} \ge 0`
     - MW
     - Hourly power discharged at each storage unit :math:`s` in hour :math:`t`.
   * - :math:`e_{s,t} \ge 0`
     - MWh
     - Hourly state of charge at each storage unit :math:`s` in hour :math:`t`.

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

1. **Thermal generation cost:** The marginal cost of a thermal unit is the fuel it
   burns per MWh (heat rate (:math:`HR_g`)) times the fuel price (:math:`FP_g`), plus the
   variable O&M cost (:math:`VOM_g`). This determines the merit order so that 
   cheaper units are dispatched first.
2. **Unserved energy penalty:** Cost penalty for load shedding (:math:`\gamma^{LS}`) is well 
   above the marginal cost of generators, so the model sheds load only when no combination
   of generation, storage and transmission can meet demand.
3. **Hydro and renewable cost:** Hydro, solar, onshore wind, and offshore wind have no fuel cost. 
   A small cost (:math:`\gamma^{R}`) breaks ties between these zero-cost resources.
4. **Absolute-flow penalty:** A small cost (:math:`\gamma^{F}`) on the absolute value
   of every line flow discourages needless circulating flows that don't change the
   total cost. This also discourages moving unserved energy through the network unnecessarily.
5. **Storage cycling cost:** A small cost (:math:`\gamma^{ST}`) on charging and
   discharging stops a unit from charging and discharging in the same hour, which
   would otherwise waste energy through the efficiency losses at no cost.

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
unserved energy, must-run output, minus the net power leaving the bus over
transmission lines. Because :math:`A_{l,b} = +1` at a line's *from* bus and
:math:`-1` at its *to* bus, :math:`\sum_{l} A_{l,b} f_{l,t}` is the total flow leaving
bus :math:`b` minus the total flow entering it. The right-hand side is the demand at
the bus plus the net charging of the storage units located there.

Must-run (e.g., nuclear) output is not a decision variable. Nuclear plants usually run at a constant
output, so the model treats them as a fixed injection :math:`MR_{b,t}` in the bus
power balance. The injection is the must-run capacity at the bus, reduced by the
fleet-wide nuclear outage loss divided by the number of nuclear units:

.. math::

   MR_{b,t} = \max\!\left(0,\ \overline{MR}_b - \frac{L^{nuc}_t}{N^{nuc}} \right)
   \qquad \forall b \in \mathcal{B},\ t \in \mathcal{T}

The per-unit loss can't be negative. Because must-run output is
fixed, the other resources are dispatched around it.

The dual variable :math:`\lambda_{b,t}` of this constraint is the cost of serving one
more MW of demand at bus :math:`b` in hour :math:`t`. This is the **locational
marginal price (LMP)**, written to ``duals_file``. LMPs differ between buses when
transmission limits are binding (i.e., congestion). At buses where load is shed, the LMP
is set by the unserved energy penalty (:math:`\gamma^{LS}`).

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
network once the bus injections are known so the solver can't route power freely.

The second constraint keeps each flow within the line's thermal limit in both
directions. The third fixes the angle of the reference bus at zero. Only angle 
differences matter, so without a reference the angles would not be unique. 
The last constraint bounds the angles to
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

The outage-adjusted capacity represents generator outages. The
``lost_capacity_file`` gives the total capacity lost in each outage group and hour.
The loss is split equally among the generators of the group and subtracted from
their nameplate capacity. Capacity can't be negative:

.. math::

   \overline{P}^{O}_{g,t} = \max\!\left(0,\ \overline{P}_g
       - \sum_{k \in \mathcal{K} , g \in \mathcal{G}_k} \frac{L_{k,t}}{|\mathcal{G}_k|} \right)
   \qquad \forall g \in \mathcal{G}^{O},\ t \in \mathcal{T}

:math:`\overline{P}^{O}_{g,t}` is computed before the solve, so the constraint stays
linear. Splitting the loss equally is an approximation. The input data says how much
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

A generator outage can remove capacity faster than the unit could ramp down. Without
an adjustment, the capacity limit and the ramp-down limit could then contradict each
other and make the problem infeasible. The ramp-down allowance :math:`\Delta_{g,t}`
relaxes the ramp-down limit by the size of the drop in outage-adjusted capacity.

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

Hydropower is limited by the water availability, which the model takes as given from
the daily hydro input files. These constraints describe what a hydro plant can do
with that water:

* The first constraint keeps the hourly output of every hydro unit between a minimum
  and a maximum. The minimum :math:`\underline{H}_g` represents required releases,
  such as minimum flows for the environment, that produce electricity
  whether or not it is needed. The maximum :math:`\overline{H}_g` reflects the
  turbine capacity and water conditions of the day.
* The second constraint is an energy budget: the total hydro generation over the
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
may produce less. The difference, :math:`AV_{g,t} - p_{g,t}`, is curtailment.
Renewable energy is curtailed when using all of it would violate another constraint,
for example when transmission lines out of a region are congested or when must-run
and minimum hydro output already cover demand.

Storage
~~~~~~~

.. math::

   \begin{aligned}
   e_{s,t} &= e_{s,t-1} + \eta^{ch}_s \, c_{s,t} - \frac{d_{s,t}}{\eta^{dis}_s}
       && \text{(1) State-of-charge balance} \\
   c_{s,t} &\le \frac{\overline{SoC}_s - e_{s,t-1}}{\eta^{ch}_s}
       && \text{(2) Charging headroom} \\
   d_{s,t} &\le \left( e_{s,t-1} - \underline{SoC}_s \right) \eta^{dis}_s
       && \text{(3) Available energy} \\
   \frac{c_{s,t}}{\overline{P}^{ch}_s} + \frac{d_{s,t}}{\overline{P}^{dis}_s} &\le 1
       && \text{(4) Joint charge/discharge limit} \\
   0 \le c_{s,t} \le \overline{P}^{ch}_s, \quad
   0 \le d_{s,t} &\le \overline{P}^{dis}_s, \quad
   \underline{SoC}_s \le e_{s,t} \le \overline{SoC}_s
       && \text{(5) Bounds}
   \end{aligned}

These hold for all :math:`s \in \mathcal{S}` and :math:`t \in \mathcal{T}`, with
:math:`e_{s,0} = SoC^{0}_s`, the state of charge at the end of the previous horizon.
A fresh run starts every unit at its minimum state of charge
:math:`\underline{SoC}_s`.

Storage units (batteries and pumped storage hydro) move energy in time. They charge
when power is cheap and discharge when it is expensive. The constraints work as
follows:

1. **State-of-charge balance:** The energy stored at the end of an hour is the energy
   at the end of the previous hour, plus the energy added by charging, minus the
   energy removed by discharging. The round-trip efficiency is
   :math:`\eta^{ch}_s \eta^{dis}_s`.
2. **Charging headroom:** A unit can't charge more than fits between the state of
   charge at the start of the hour and the maximum state of charge, after charging losses.
3. **Available energy:** A unit can't deliver more than the energy stored above its
   minimum state of charge at the start of the hour, after discharging losses.
4. **Joint charge/discharge limit:** Charging and discharging in the same hour share
   the unit's power capability. Charging at full power leaves no room for
   discharging, and vice versa. Together with the storage cycling cost in the objective function, 
   this keeps the model from charging and discharging at the same time.
5. **Bounds:** Charging and discharging power are limited by the unit's power
   ratings, and the state of charge stays within its limits.

The storage power enters the bus power balance at the unit's bus such that charging is extra
demand and discharging is extra supply.

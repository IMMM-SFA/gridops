API reference
=============

The names below are importable directly from the top-level package, for example
``gridops.Model``, ``gridops.GoSolver`` and ``gridops.generate_config``.

Model
-----

.. autoclass:: gridops.model.Model
   :members: run, retry

.. autodata:: gridops.model.HIGHS_RETRY_DEFAULTS
   :no-value:

Solvers
-------

.. autoclass:: gridops.solvers.GoSolver

   .. autoattribute:: SUPPORTED

Configuration
-------------

.. autoclass:: gridops.configuration.Config

.. autofunction:: gridops.configuration.generate_config

.. autofunction:: gridops.configuration.read_config_file

Utilities
---------

Restart files
~~~~~~~~~~~~~

.. autofunction:: gridops.utilities.get_restart_file

.. autofunction:: gridops.utilities.get_prior_restart_file_day

.. autofunction:: gridops.utilities.write_restart_file

.. autofunction:: gridops.utilities.clear_restart_files

Solver parameter files
~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: gridops.utilities.load_solver_parameters

.. autofunction:: gridops.utilities.write_solver_parameters

Western Interconnection
-----------------------

These lower-level functions are called by :meth:`gridops.model.Model.run`. They are
documented for users who want to inspect or extend the optimization model.

.. automodule:: gridops.west.launch
   :no-members:

.. autofunction:: gridops.west.launch.west_linear

.. autofunction:: gridops.west.launch.load_simulation_data

.. automodule:: gridops.west.linear
   :no-members:

.. autofunction:: gridops.west.linear.build_west_linear

Model constants
~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 35 20 45

   * - Constant
     - Value
     - Meaning
   * - ``gridops.west.linear.SLACK_PENALTY``
     - 2000.0 $/MWh
     - Penalty on unserved energy.
   * - ``gridops.west.linear.RENEWABLE_GEN_COST``
     - 0.01 $/MWh
     - Tie-breaking cost on hydro, solar, onshore wind, and offshore wind dispatch.
   * - ``gridops.west.linear.DUMMY_FLOW_PENALTY``
     - 0.01 $/MWh
     - Penalty on the absolute value of line flows.
   * - ``gridops.west.linear.STORAGE_COST``
     - 0.001 $/MWh
     - Cost on storage charge and discharge.
   * - ``gridops.west.linear.REFERENCE_BUS``
     - ``"bus_100011"``
     - Bus whose voltage angle is fixed to zero.
   * - ``gridops.west.linear.PU_BASE_MVA``
     - 100.0 MVA
     - Per-unit base for the DC power-flow equations.
   * - ``gridops.west.launch.SNAP_TOL``
     - 1e-6
     - Inputs with smaller magnitude are set to zero.
   * - ``gridops.west.launch.FUEL_TYPE_MAP``
     - ``dict``
     - Maps ``typ`` values to model sets (see :doc:`user_guide/inputs`).

Placeholders
------------

The following modules are reserved for future releases. Selecting them in
:class:`~gridops.model.Model` raises ``NotImplementedError``.

* ``gridops.west.mixed_integer``: Western Interconnection unit commitment (MILP).
* ``gridops.east``: U.S. Eastern Interconnection.
* ``gridops.ercot``: ERCOT (Texas) Interconnection.

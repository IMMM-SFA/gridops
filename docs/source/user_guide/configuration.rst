Configuration file
==================

A gridops run reads a YAML file that maps each input file to its path, each output
file to its destination, and gives the directory used for restart files. The
YAML keys correspond one-to-one with the fields of
:class:`~gridops.configuration.Config`. Every key is required, and unknown keys raise
an error.

Template
--------

The template below ships with the package as ``gridops/data/example_config_file.yml``:

.. literalinclude:: ../../../gridops/data/example_config_file.yml
   :language: yaml

Path resolution
---------------

Paths can be absolute or relative. Relative paths are resolved against the **current
working directory of the Python process**, not against the location of the YAML
file. Use absolute paths, or ``os.chdir`` to the folder the relative paths start
from.

gridops creates the restart directory if it doesn't exist. The **parent directories
of the input and output files must already exist.**

Keys
----

Input files
~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 32 10 58

   * - Key
     - Format
     - Contents (see :doc:`inputs` for full details)
   * - ``generator_parameters_file``
     - CSV
     - Generator parameters.
   * - ``generator_matrix_file``
     - CSV
     - Generator-to-bus incidence matrix (0/1).
   * - ``line_to_bus_file``
     - CSV
     - Line-to-bus incidence matrix (-1/0/1).
   * - ``line_parameters_file``
     - CSV
     - Line reactance (p.u.) and thermal limit (MW).
   * - ``daily_hydro_maximum_file``
     - CSV
     - Daily maximum hourly hydro output per bus (MW).
   * - ``daily_hydro_minimum_file``
     - CSV
     - Daily minimum hourly hydro output per bus (MW).
   * - ``daily_hydro_total_file``
     - CSV
     - Daily total hydro energy budget per bus (MWh).
   * - ``nodal_solar_file``
     - CSV
     - Hourly available solar generation per bus (MW).
   * - ``nodal_wind_file``
     - CSV
     - Hourly available onshore wind generation per bus (MW).
   * - ``nodal_offshore_wind_file``
     - CSV
     - Hourly available offshore wind generation per bus (MW).
   * - ``nodal_load_file``
     - CSV
     - Hourly demand per bus (MW).
   * - ``must_run_file``
     - CSV
     - Must-run (e.g., nuclear) capacity per bus (MW).
   * - ``fuel_prices_file``
     - CSV
     - Daily fuel price for thermal generators ($/MMBtu).
   * - ``storage_params_file``
     - CSV
     - Storage parameters.
   * - ``bus_to_storage_matrix_file``
     - CSV
     - Storage-to-bus incidence matrix (0/1).
   * - ``generator_outage_file``
     - NPY
     - Pickled ``dict`` mapping outage-group names to generator names.
   * - ``thermal_generators_file``
     - CSV
     - Thermal generator list.
   * - ``lost_capacity_file``
     - CSV
     - Hourly capacity lost to generator outages per outage group (MW).

Output files
~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 32 10 58

   * - Key
     - Format
     - Contents (see :doc:`outputs` for full details)
   * - ``mwh_file``
     - Parquet
     - Hourly generator dispatch.
   * - ``slack_file``
     - Parquet
     - Hourly unserved energy per bus.
   * - ``flow_file``
     - Parquet
     - Hourly transmission line flows.
   * - ``duals_file``
     - Parquet
     - Hourly locational marginal prices (LMPs) per bus.
   * - ``storage_soc_file``
     - Parquet
     - Hourly storage state of charge per storage unit.
   * - ``storage_discharge_file``
     - Parquet
     - Hourly storage discharge per storage unit.
   * - ``storage_charge_file``
     - Parquet
     - Hourly storage charge per storage unit.
   * - ``vlt_angle_file``
     - Parquet
     - Hourly voltage angles per bus.

Other settings
~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 32 10 58

   * - Key
     - Format
     - Contents
   * - ``restart_file_directory``
     - Directory
     - Where restart files (``model_restart_file_dayDDD_vVVV.pkl``) and
       ``solver_parameters.json`` are written and read.

Loading a configuration in Python
---------------------------------

:func:`~gridops.configuration.generate_config` parses a YAML file, or takes keyword
arguments when no file is given, and returns a validated
:class:`~gridops.configuration.Config`. It also logs every value.

.. code-block:: python

   from gridops import generate_config

   config = generate_config("my_config.yml")
   print(config.nodal_load_file)

When ``config_file`` is given, any keyword arguments are ignored.

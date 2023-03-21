# IAMMETER

------

[IAMMETER](https://www.iammeter.com/) provides both a bi-directional single-phase energy meter([WEM3080](https://www.iammeter.com/products/single-phase-meter)) and a bi-directional three-phase energy monitor ([WEM3080T](https://www.iammeter.com/products/three-phase-meter)). Both of them can be integrated into Home Assistant.

## Installation

------

### Manual Installation

1. Copy `ha_iammeter` folder into your custom_components folder in your hass configuration directory.
2. Restart Home Assistant.

### Installation with HACS (Home Assistant Community Store)

1. Ensure that HACS is installed.
2. In HACS / Integrations /explore&download repositories/iammeter, add the url the this repository.
3. Search for and install the `iammeter` integration.
4. Restart Home Assistant.

## Configuration

It is configurable through config flow, meaning it will popup a dialog after adding the integration.

1. Head to Settings --> Devices & Services--> ADD INTEGRATION
2. Add new and search for `iammeter`
3. Enter a name for your meter. It suggests "IamMeter" by default, but if you plan to read multiple make it a unique name.
4. Enter a IP to the IamMeter module. For example: "192.168.2.15" .
5. SUBMIT --> FINISH.

## Sensors

Sensors available in the library:

### SINGLE-PHASE ENERGY METER (WEM3080/WEM3162)

| name                 | Unit | Description                  |
| :------------------- | :--- | :--------------------------- |
| wem3080_voltage      | V    | Voltage.                     |
| wem3080_current      | A    | current.                     |
| wem3080_power        | W    | active power.                |
| wem3080_importenergy | kWh  | Energy consumption from grid |
| wem3080_exportgrid   | kWh  | Energy export to grid        |

### THREE-PHASE ENERGY METER (WEM3080T)

| name                    | Unit | Description           |
| :---------------------- | :--- | :-------------------- |
| wem3080t_voltage_a      | V    | A phase voltage       |
| wem3080t_current_a      | A    | A phase current       |
| wem3080t_power_a        | W    | A phase active power  |
| wem3080t_importenergy_a | kWh  | A phase import energy |
| wem3080t_exportgrid_a   | kWh  | A phase export energy |
| wem3080t_frequency_a    | Hz   | A phase frequency     |
| wem3080t_pf_a           |      | A phase power factor  |
|                         |      |                       |
| wem3080t_voltage_b      | V    | B phase voltage       |
| wem3080t_current_b      | A    | B phase current       |
| wem3080t_power_b        | W    | B phase active power  |
| wem3080t_importenergy_b | kWh  | B phase import energy |
| wem3080t_exportgrid_b   | kWh  | B phase export energy |
| wem3080t_frequency_b    | Hz   | B phase frequency     |
| wem3080t_pf_b           |      | B phase power factor  |
|                         |      |                       |
| wem3080t_voltage_c      | V    | C phase voltage       |
| wem3080t_current_c      | A    | C phase current       |
| wem3080t_power_c        | W    | C phase active power  |
| wem3080t_importenergy_c | kWh  | C phase import energy |
| wem3080t_exportgrid_c   | kWh  | C phase export energy |
| wem3080t_frequency_c    | Hz   | C phase frequency     |
| wem3080t_pf_c           |      | C phase power factor  |
|                         |      |                       |
| wem3080t_voltage_net      | V    | Net Metering Metod voltage |
| wem3080t_power_net        | W    | Net Metering Metod active power |
| wem3080t_importenergy_net | kWh  | Net Metering Metod import energy |
| wem3080t_exportgrid_net   | kWh  | Net Metering Metod export energy |
| wem3080t_frequency_net    | Hz   | Net Metering Metod frequency |
| wem3080t_pf_net           |      | Net Metering Metod power factor |
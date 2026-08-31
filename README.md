# IAMMETER HTTP for Home Assistant

Local-polling Home Assistant custom integration for IAMMETER energy meters.

## Supported meters

- WEM3080 and legacy WEM3162 single-phase payloads
- WEM3080T
- WEM3046T
- WEM3050T
- WEM3063T
- WEM2067 two-channel meter

WEM2067 exposes channels A and B only; no C-channel entities are created.

Optional `EA.Reactive` and Net Metering data are supported. If Reactive or Net
Metering data is not available in the device response, the corresponding
optional sensors are not created. If the data appears later, the sensors are
added automatically on the next update. Sensors already discovered remain
registered and become unavailable if their data later disappears.

## Installation

Install this repository as a custom integration with HACS, or copy
`custom_components/iammeter_http` into your Home Assistant configuration's
`custom_components` directory, then restart Home Assistant.

## Configuration

1. Go to **Settings > Devices & services > Add integration**.
2. Search for **IAMMETER HTTP**.
3. Enter a unique device name, hostname or IP address, HTTP port, and polling
   interval.
4. Submit the form after the connection test succeeds.

The default polling interval is 60 seconds. The allowed range is 1-3600
seconds.

For an existing entry, select **Reconfigure** to change its hostname/IP, HTTP
port, or polling interval. Home Assistant validates the new endpoint and
reloads the existing entry. The device name and entity unique IDs are retained.

The device page displays the detected meter model, firmware version, serial
number, and a link to the meter's local web interface.

## Sensors

### Single-phase meters (WEM3080/WEM3162)

| Sensor | Unit |
| :--- | :--- |
| Voltage | V |
| Current | A |
| Power | W |
| Import energy | kWh |
| Export energy | kWh |

When reactive data is present, Reactive power, Inductive reactive energy, and
Capacitive reactive energy sensors are added automatically.

### Multi-channel meters

WEM3080T, WEM3046T, WEM3050T, and WEM3063T expose the following sensors for
each A, B, and C phase. WEM2067 exposes the same sensors for A and B only.

| Sensor per phase | Unit |
| :--- | :--- |
| Voltage | V |
| Current | A |
| Power | W |
| Import energy | kWh |
| Export energy | kWh |
| Frequency | Hz |
| Power factor | — |

When reactive data is present, each physical phase also exposes Reactive
power, Inductive reactive energy, and Capacitive reactive energy. When Net
Metering data is present, Net voltage, Net power, Net import energy, Net export
energy, Net frequency, and Net power factor sensors are added automatically.

## Data layout

Each phase row uses:

`[voltage, current, active power, import energy, export energy, frequency, power factor]`

Each optional `EA.Reactive` row uses:

`[reactive power, inductive reactive energy, capacitive reactive energy]`

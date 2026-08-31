"""Constants and sensor descriptions for IAMMETER HTTP."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfReactiveEnergy,
    UnitOfReactivePower,
)

from .models import (
    MODEL_2067,
    MODEL_3046T,
    MODEL_3050T,
    MODEL_3063T,
    MODEL_3080,
    MODEL_3080T,
    MODEL_3162,
)

DOMAIN = "iammeter_http"

DEFAULT_IP = "192.168.2.15"
DEFAULT_PORT = 80
DEFAULT_NAME = "IAMMETER"
DEFAULT_TIMEOUT = 10
DEFAULT_UPDATE_INTERVAL = 60
MIN_UPDATE_INTERVAL = 1
MAX_UPDATE_INTERVAL = 3600


@dataclass(frozen=True, kw_only=True)
class IammeterSensorEntityDescription(SensorEntityDescription):
    """Describe an IAMMETER sensor entity."""


def _phase_descriptions(phase: str) -> tuple[IammeterSensorEntityDescription, ...]:
    """Build active measurement descriptions for one channel."""
    return (
        IammeterSensorEntityDescription(
            key=f"Voltage_{phase}",
            name=f"Voltage {phase}",
            native_unit_of_measurement=UnitOfElectricPotential.VOLT,
            device_class=SensorDeviceClass.VOLTAGE,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        IammeterSensorEntityDescription(
            key=f"Current_{phase}",
            name=f"Current {phase}",
            native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
            device_class=SensorDeviceClass.CURRENT,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        IammeterSensorEntityDescription(
            key=f"Power_{phase}",
            name=f"Power {phase}",
            native_unit_of_measurement=UnitOfPower.WATT,
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        IammeterSensorEntityDescription(
            key=f"ImportEnergy_{phase}",
            name=f"Import energy {phase}",
            native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
            device_class=SensorDeviceClass.ENERGY,
            state_class=SensorStateClass.TOTAL_INCREASING,
        ),
        IammeterSensorEntityDescription(
            key=f"ExportGrid_{phase}",
            name=f"Export energy {phase}",
            native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
            device_class=SensorDeviceClass.ENERGY,
            state_class=SensorStateClass.TOTAL_INCREASING,
        ),
        IammeterSensorEntityDescription(
            key=f"Frequency_{phase}",
            name=f"Frequency {phase}",
            native_unit_of_measurement=UnitOfFrequency.HERTZ,
            device_class=SensorDeviceClass.FREQUENCY,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        IammeterSensorEntityDescription(
            key=f"PF_{phase}",
            name=f"Power factor {phase}",
            device_class=SensorDeviceClass.POWER_FACTOR,
            state_class=SensorStateClass.MEASUREMENT,
        ),
    )


def _reactive_descriptions(
    phase: str,
) -> tuple[IammeterSensorEntityDescription, ...]:
    """Build optional reactive descriptions for one channel."""
    return (
        IammeterSensorEntityDescription(
            key=f"ReactivePower_{phase}",
            name=f"Reactive power {phase}",
            native_unit_of_measurement=UnitOfReactivePower.VOLT_AMPERE_REACTIVE,
            device_class=SensorDeviceClass.REACTIVE_POWER,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        IammeterSensorEntityDescription(
            key=f"InductiveReactiveEnergy_{phase}",
            name=f"Inductive reactive energy {phase}",
            native_unit_of_measurement=UnitOfReactiveEnergy.KILO_VOLT_AMPERE_REACTIVE_HOUR,
            device_class=SensorDeviceClass.REACTIVE_ENERGY,
            state_class=SensorStateClass.TOTAL_INCREASING,
        ),
        IammeterSensorEntityDescription(
            key=f"CapacitiveReactiveEnergy_{phase}",
            name=f"Capacitive reactive energy {phase}",
            native_unit_of_measurement=UnitOfReactiveEnergy.KILO_VOLT_AMPERE_REACTIVE_HOUR,
            device_class=SensorDeviceClass.REACTIVE_ENERGY,
            state_class=SensorStateClass.TOTAL_INCREASING,
        ),
    )


SENSOR_TYPES_3080 = (
    IammeterSensorEntityDescription(
        key="Voltage",
        name="Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    IammeterSensorEntityDescription(
        key="Current",
        name="Current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    IammeterSensorEntityDescription(
        key="Power",
        name="Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    IammeterSensorEntityDescription(
        key="ImportEnergy",
        name="Import energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    IammeterSensorEntityDescription(
        key="ExportGrid",
        name="Export energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    IammeterSensorEntityDescription(
        key="ReactivePower_A",
        name="Reactive power",
        native_unit_of_measurement=UnitOfReactivePower.VOLT_AMPERE_REACTIVE,
        device_class=SensorDeviceClass.REACTIVE_POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    IammeterSensorEntityDescription(
        key="InductiveReactiveEnergy_A",
        name="Inductive reactive energy",
        native_unit_of_measurement=UnitOfReactiveEnergy.KILO_VOLT_AMPERE_REACTIVE_HOUR,
        device_class=SensorDeviceClass.REACTIVE_ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    IammeterSensorEntityDescription(
        key="CapacitiveReactiveEnergy_A",
        name="Capacitive reactive energy",
        native_unit_of_measurement=UnitOfReactiveEnergy.KILO_VOLT_AMPERE_REACTIVE_HOUR,
        device_class=SensorDeviceClass.REACTIVE_ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
)

SENSOR_TYPES_NET = (
    IammeterSensorEntityDescription(
        key="Voltage_Net",
        name="Net voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    IammeterSensorEntityDescription(
        key="Power_Net",
        name="Net power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    IammeterSensorEntityDescription(
        key="ImportEnergy_Net",
        name="Net import energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    IammeterSensorEntityDescription(
        key="ExportGrid_Net",
        name="Net export energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    IammeterSensorEntityDescription(
        key="Frequency_Net",
        name="Net frequency",
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    IammeterSensorEntityDescription(
        key="PF_Net",
        name="Net power factor",
        device_class=SensorDeviceClass.POWER_FACTOR,
        state_class=SensorStateClass.MEASUREMENT,
    ),
)

SENSOR_TYPES_A = _phase_descriptions("A") + _reactive_descriptions("A")
SENSOR_TYPES_B = _phase_descriptions("B") + _reactive_descriptions("B")
SENSOR_TYPES_C = _phase_descriptions("C") + _reactive_descriptions("C")

SENSOR_TYPES_BY_MODEL = {
    MODEL_3080: SENSOR_TYPES_3080,
    MODEL_3162: SENSOR_TYPES_3080,
    MODEL_3080T: SENSOR_TYPES_A + SENSOR_TYPES_B + SENSOR_TYPES_C + SENSOR_TYPES_NET,
    MODEL_3046T: SENSOR_TYPES_A + SENSOR_TYPES_B + SENSOR_TYPES_C + SENSOR_TYPES_NET,
    MODEL_3050T: SENSOR_TYPES_A + SENSOR_TYPES_B + SENSOR_TYPES_C + SENSOR_TYPES_NET,
    MODEL_3063T: SENSOR_TYPES_A + SENSOR_TYPES_B + SENSOR_TYPES_C + SENSOR_TYPES_NET,
    MODEL_2067: SENSOR_TYPES_A + SENSOR_TYPES_B + SENSOR_TYPES_NET,
}

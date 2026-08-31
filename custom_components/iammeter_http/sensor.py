"""Sensor platform for IAMMETER HTTP."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import IammeterConfigEntry, IammeterData
from .const import (
    DOMAIN,
    SENSOR_TYPES_BY_MODEL,
    IammeterSensorEntityDescription,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: IammeterConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up IAMMETER HTTP sensors."""
    coordinator = entry.runtime_data
    descriptions = SENSOR_TYPES_BY_MODEL[coordinator.data.model]
    added_keys: set[str] = set()

    def _async_add_new_entities() -> None:
        """Add measurements when they first appear in a meter response."""
        new_descriptions = [
            description
            for description in descriptions
            if description.key in coordinator.data.measurement
            and description.key not in added_keys
        ]
        if not new_descriptions:
            return

        added_keys.update(description.key for description in new_descriptions)
        async_add_entities(
            IammeterSensor(coordinator, entry, description)
            for description in new_descriptions
        )

    _async_add_new_entities()
    entry.async_on_unload(coordinator.async_add_listener(_async_add_new_entities))


class IammeterSensor(CoordinatorEntity[IammeterData], SensorEntity):
    """Representation of an IAMMETER HTTP sensor."""

    _attr_has_entity_name = True
    entity_description: IammeterSensorEntityDescription

    def __init__(
        self,
        coordinator: IammeterData,
        entry: IammeterConfigEntry,
        description: IammeterSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"

        reading = coordinator.data
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            manufacturer="IAMMETER",
            name=entry.title,
            model=reading.model,
            sw_version=reading.firmware_version,
            serial_number=reading.serial_number,
            configuration_url=coordinator.api.configuration_url,
        )

    @property
    def available(self) -> bool:
        """Return whether this measurement is present in the latest payload."""
        return (
            super().available
            and self.entity_description.key in self.coordinator.data.measurement
        )

    @property
    def native_value(self) -> float | None:
        """Return the native sensor value."""
        return self.coordinator.data.measurement.get(self.entity_description.key)

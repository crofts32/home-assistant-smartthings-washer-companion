# SmartThings Washer Companion

Experimental Home Assistant custom integration that adds Samsung washer cycle
selection while keeping the official SmartThings integration installed.

It reuses the official integration's OAuth-authenticated runtime client. It does
not request or store a SmartThings token, Samsung password, Home Assistant token,
device serial number, or household identifier.

## Scope

- Discovers washers that expose `samsungce.washerCycle`.
- Reads the washer's live `supportedCycles` list.
- Adds a cycle selector to the existing SmartThings device.
- Refuses cycle changes unless Smart Control is enabled and the washer is stopped.
- Leaves unknown cycle codes visible instead of guessing their meaning.

The component deliberately does not replace SmartThings, start appliances,
manage security devices, or expose a generic SmartThings command service.

## Installation

Copy `custom_components/smartthings_washer_companion` into Home Assistant's
`custom_components` directory, restart Home Assistant, then add **SmartThings
Washer Companion** from **Settings → Devices & services**.

## Status and risk

This is experimental, independently developed software. It was produced with
AI-assisted coding ("vibecoded") and is not affiliated with Samsung,
SmartThings, Home Assistant, or the Open Home Foundation. Review the source and
test while standing near the appliance before relying on unattended operation.

Samsung cycle codes vary by reference table and model. The integration only
sends codes reported by the washer itself. Friendly names are applied only for
known tables; unknown values remain visible as raw codes.

## Licence

MIT

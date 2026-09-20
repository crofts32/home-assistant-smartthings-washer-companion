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
- Adds a constrained `schedule_wash` action that selects a supported cycle,
  configures Samsung Delay End, and asks the washer to start when needed.
- Leaves unknown cycle codes visible instead of guessing their meaning.

The component deliberately does not replace SmartThings, manage security
devices, or expose a generic SmartThings command service.

## Finish-by action

The washer must be stopped with Smart Control enabled. The requested cycle must
be one of the live options reported by the appliance, and the finish time must
be within Samsung's 24-hour Delay End window. Samsung accepts Delay End in
five-minute increments, so the integration rounds down to avoid finishing later
than requested.

```yaml
action: smartthings_washer_companion.schedule_wash
target:
  entity_id: select.washing_machine_cycle
data:
  cycle: Colours
  finish_at: "2026-09-21T06:55:00+01:00"
```

The action verifies the cycle and Delay End setting before sending Samsung's
washer-specific start command. It reports an error if SmartThings does not
confirm the requested state.

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

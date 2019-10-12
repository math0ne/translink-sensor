# Translink Sensor

This is home assistant custom component to pull bus times from TransLink Open API.  This is pretty limited right now, simply pulling in the next three times for a given stop and route.

There is a lovelace ui custom card available here: https://github.com/math0ne/translink-card

You can find stop id's here: https://tp.translink.ca/hiwire?.a=iLocationLookup

Register for an API key here: https://developer.translink.ca/Account/Register

### Installation

Copy this folder to `<config_dir>/custom_components/translink_sensor/`.

Add the following to your `configuration.yaml` file:

```yaml
# Example configuration.yaml entry
sensor:
  - platform: translink_sensor
    api_key: XXX
    stop_id: 58652
    route_number: 16
```
### Credits

This based on the work of:

* johnlarusic: https://github.com/johnlarusic/lebus
* amaximus: https://github.com/amaximus/bkk_stop
import asyncio
from datetime import timedelta
import logging
import urllib.request
import json

import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import ATTR_ATTRIBUTION, CONF_NAME
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity

import xml.etree.ElementTree as ET

REQUIREMENTS = [ ]

_LOGGER = logging.getLogger(__name__)

CONF_ATTRIBUTION = "Data provided by TransLink Open API"
CONF_STOPID = 'stop_id'
CONF_ROUTENUMBER = 'route_number'
CONF_APIKEY = 'api_key'

DEFAULT_NAME = 'Translink Next Bus'
DEFAULT_ICON = 'mdi:bus'

SCAN_INTERVAL = timedelta(seconds=240)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_STOPID): cv.string,
    vol.Required(CONF_ROUTENUMBER): cv.string,
    vol.Required(CONF_APIKEY): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
})

@asyncio.coroutine
def async_setup_platform(hass, config, async_add_devices, discovery_info=None):
    #_LOGGER.debug("start async setup platform")

    name = config.get(CONF_NAME)
    stopid = config.get(CONF_STOPID)
    routenumber = config.get(CONF_ROUTENUMBER)
    apikey = config.get(CONF_APIKEY)

    session = async_get_clientsession(hass)

    async_add_devices(
        [TranslinkPublicTransportSensor(name, stopid, routenumber, apikey)],update_before_add=True)

class TranslinkPublicTransportSensor(Entity):

    def __init__(self, name, stopid, routenumber, apikey):
        """Initialize the sensor."""
        self._name = name
        self._stopid = stopid
        self._routenumber = routenumber
        self._apikey = apikey
        self._state = None
        self._icon = DEFAULT_ICON

    @property
    def device_state_attributes(self):
        attr = {}
        translinkfile = "/tmp/tmpstopinfo_" + self._routenumber + "_" + self._stopid + ".xml"
        translinkdata = ET.parse(translinkfile).getroot()
        
        attr["route_number"] = self._routenumber
        attr["stop_id"] = self._stopid

        leavetimes = translinkdata.findall("./NextBus/Schedules/Schedule/ExpectedLeaveTime")
        countdowntimes = translinkdata.findall("./NextBus/Schedules/Schedule/ExpectedCountdown")

        if leavetimes:
            count=0
            while count < 3:
                if count == 0:
                    attr["next_bus_countdown"] = countdowntimes[count].text

                scheduletextsplit = leavetimes[count].text.split(" ")
                scheduletextsplit2 = scheduletextsplit[0].split(",")
                attr["buses_" + str(count + 1)] = scheduletextsplit2[0]
                count +=1

        return attr

    @asyncio.coroutine
    def async_update(self):
        translinkfile = "/tmp/tmpstopinfo_" + self._routenumber + "_" + self._stopid + ".xml"
        translinkurl="http://api.translink.ca/rttiapi/v1/stops/" + self._stopid + "/estimates?routeNo=" + self._routenumber + "&apikey=" + self._apikey + "&count=3"

        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)
        urllib.request.urlretrieve(translinkurl, translinkfile)
        translinkdata = ET.parse(translinkfile).getroot()

        self._state = 1
        return self._state  

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state
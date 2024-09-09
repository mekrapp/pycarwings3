#!/usr/bin/env python

from datetime import datetime, timedelta
import json
import logging
import sys
import pytz
import pytest
from pycarwings3.responses import (
    CarwingsLatestBatteryStatusResponse,
    CarwingsLatestClimateControlStatusResponse,
    NoDataError
)

pytest_plugins = ('pytest_asyncio',)

logging.basicConfig(stream=sys.stdout, level=logging.ERROR)


def test_get_latest_hvac_status_on():
    # Source: original pycarwings2 sources
    climateresponse = """
        {
            "status":200,
            "message":"success",
            "RemoteACRecords":{
                "OperationResult":"START_BATTERY",
                "OperationDateAndTime":"Feb 10, 2016 10:22 PM",
                "RemoteACOperation":"START",
                "ACStartStopDateAndTime":"2018/04/08 10:00",
                "CruisingRangeAcOn":"107712.0",
                "CruisingRangeAcOff":"109344.0",
                "ACStartStopURL":"",
                "PluginState":"NOT_CONNECTED",
                "ACDurationBatterySec":"900",
                "ACDurationPluggedSec":"7200"
            },
            "OperationDateAndTime":""
        }
"""
    response = json.loads(climateresponse)
    status = CarwingsLatestClimateControlStatusResponse(response)
    assert status.is_hvac_running
    assert status.cruising_range_ac_on_km == 107.712
    assert status.cruising_range_ac_off_km == 109.344
    assert status.ac_duration == timedelta(seconds=900)
    assert status.ac_start_stop_date_and_time == datetime(2018, 4, 8, 10, 0, 0, tzinfo=pytz.utc)
    assert status.is_plugged_in is False

def test_get_latest_hvac_status_off():
    # Source: From 24kWh Leaf (Climate is OFF)
    climateresponse = """
{
  "status":200,
  "RemoteACRecords":{
    "OperationResult":"START_BATTERY",
    "OperationDateAndTime":"11-Jan-2019 17:51",
    "RemoteACOperation":"STOP",
    "ACStartStopDateAndTime":"2019/01/11 16:52",
    "CruisingRangeAcOn":"74328.0",
    "CruisingRangeAcOff":"79544.0",
    "ACStartStopURL":"",
    "PluginState":"NOT_CONNECTED",
    "ACDurationBatterySec":"900",
    "ACDurationPluggedSec":"7200"}
}
"""
    response = json.loads(climateresponse)
    status = CarwingsLatestClimateControlStatusResponse(response)
    assert not status.is_hvac_running


def test_get_latest_hvac_status_error():
    # Source: original pycarwings2 sources
    climateresponse = """
        {
            "status":200,
            "RemoteACRecords": []
        }
"""
    # Assume climate control is off if we get back an empty response
    response = json.loads(climateresponse)
    status = CarwingsLatestClimateControlStatusResponse(response)
    assert not status.is_hvac_running


def test_get_latest_hvac_status_empty():
    # Source: 30kWh Leaf as at 13/01/2019
    climateresponse = """
{"status":200,"RemoteACRecords":[]}
"""
    # Assume climate control is off if we get back an empty response
    response = json.loads(climateresponse)
    status = CarwingsLatestClimateControlStatusResponse(response)
    assert not status.is_hvac_running


def test_get_latest_hvac_status_no_ranges_off():
    # Source: unknown leaf in Jan 2019
    # Missing CruisingRangeAcOn and CruisingRangeAcOff
    climateresponse = """
{
  "status": 200,
  "RemoteACRecords": {
    "OperationResult":"START",
    "OperationDateAndTime":"2019/01/24 09:43",
    "RemoteACOperation":"STOP",
    "ACStartStopDateAndTime":"2018/04/08 10:00",
    "ACStartStopURL":"",
    "PluginState":"NOT_CONNECTED",
    "ACDurationBatterySec":"900",
    "ACDurationPluggedSec ":"7200",
    "PreAC_unit":"C",
    "PreAC_temp":"22",
    "Inc_temp ":"12"
  }
}
"""
    # Climate control should be off
    response = json.loads(climateresponse)
    status = CarwingsLatestClimateControlStatusResponse(response)
    assert not status.is_hvac_running


def test_get_latest_hvac_status_no_ranges_on():
    # Source: unknown leaf in Jan 2019
    # Missing CruisingRangeAcOn and CruisingRangeAcOff
    climateresponse = """
{
  "status": 200,
  "RemoteACRecords": {
    "OperationResult":"START",
    "OperationDateAndTime":"2019/01/24 09:43",
    "RemoteACOperation":"START",
    "ACStartStopDateAndTime":"2019-jan-24 10:44",
    "ACStartStopURL":"",
    "PluginState":"NOT_CONNECTED",
    "ACDurationBatterySec":"900",
    "ACDurationPluggedSec ":"7200",
    "PreAC_unit":"C",
    "PreAC_temp":"22",
    "Inc_temp ":"12"
  }
}
"""
    # Assume climate control should be on
    response = json.loads(climateresponse)
    status = CarwingsLatestClimateControlStatusResponse(response)
    assert status.is_hvac_running


def test_get_latest_battery_status_24kWh_30percent_0degredation():
    # not connected to a charger
    batteryresponse = """
        {
            "status":200,
            "message":"success",
            "BatteryStatusRecords":{
                "OperationResult":"START",
                "OperationDateAndTime":"Feb  9, 2016 11:09 PM",
                "BatteryStatus":{
                    "BatteryChargingStatus":"NOT_CHARGING",
                    "BatteryCapacity":"12",
                    "BatteryRemainingAmount":"3",
                    "BatteryRemainingAmountWH":"",
                    "BatteryRemainingAmountkWH":""
                },
                "PluginState":"NOT_CONNECTED",
                "CruisingRangeAcOn":"39192.0",
                "CruisingRangeAcOff":"39744.0",
                "TimeRequiredToFull":{
                    "HourRequiredToFull":"18",
                    "MinutesRequiredToFull":"30"
                },
                "TimeRequiredToFull200":{
                    "HourRequiredToFull":"6",
                    "MinutesRequiredToFull":"0"
                },
                "TimeRequiredToFull200_6kW":{
                    "HourRequiredToFull":"4",
                    "MinutesRequiredToFull":"0"
                },
                "NotificationDateAndTime":"2016/02/10 04:10",
                "TargetDate":"2016/02/10 04:09"
            }
        }
"""
    response = json.loads(batteryresponse)
    status = CarwingsLatestBatteryStatusResponse(response)
    assert status.battery_percent == 100 * 3 / 12


def test_get_latest_battery_status_24kWh_50percent_1degredation():
    # Charging, but with 50% charged, with 11 bars max charge (1 bar lost)
    batteryresponse = """
{
  "status": 200,
  "BatteryStatusRecords": {
    "OperationResult": "START",
    "OperationDateAndTime": "26-Jan-2019 22:22",
    "BatteryStatus": {
      "BatteryChargingStatus": "NORMAL_CHARGING",
      "BatteryCapacity": "11",
      "BatteryRemainingAmount": "6",
      "BatteryRemainingAmountWH": "",
      "BatteryRemainingAmountkWH": ""
    },
    "PluginState": "CONNECTED",
    "CruisingRangeAcOn": "66024.0",
    "CruisingRangeAcOff": "69168.0",
    "TimeRequiredToFull200_6kW": {
      "HourRequiredToFull": "3",
      "MinutesRequiredToFull": "0"
    },
    "NotificationDateAndTime": "2019/01/26 21:22",
    "TargetDate": "2019/01/26 21:22"
  }
}
"""
    response = json.loads(batteryresponse)
    status = CarwingsLatestBatteryStatusResponse(response)
    assert status.battery_percent == 100 * 6 / 12


def test_get_latest_battery_status_24kWh_91percent_1degredation():
    # Not charging, but with 11 bars charged, 11 bars max charge (1 bar lost)
    batteryresponse = """
{
  "status": 200,
  "BatteryStatusRecords": {
    "OperationResult": "START",
    "OperationDateAndTime": "09-Jan-2019 20:45",
    "BatteryStatus": {
      "BatteryChargingStatus": "NOT_CHARGING",
      "BatteryCapacity": "11",
      "BatteryRemainingAmount": "11",
      "BatteryRemainingAmountWH": "",
      "BatteryRemainingAmountkWH": ""
    },
    "PluginState": "NOT_CONNECTED",
    "CruisingRangeAcOn": "97704.0",
    "CruisingRangeAcOff": "105984.0",
    "TimeRequiredToFull": {
      "HourRequiredToFull": "3",
      "MinutesRequiredToFull": "30"
    },
    "TimeRequiredToFull200": {
      "HourRequiredToFull": "2",
      "MinutesRequiredToFull": "30"
    },
    "TimeRequiredToFull200_6kW": {
      "HourRequiredToFull": "2",
      "MinutesRequiredToFull": "0"
    },
    "NotificationDateAndTime": "2019/01/09 19:45",
    "TargetDate": "2019/01/09 19:45"
  }
}
"""
    response = json.loads(batteryresponse)
    status = CarwingsLatestBatteryStatusResponse(response)
    assert status.battery_percent == 100 * 11 / 12


def test_get_latest_battery_status_24kWh_100percent_1degredation():
    # Not charging, but fully charged, 1 bar lost
    batteryresponse = """
{
  "status":200,
  "BatteryStatusRecords":{
    "OperationResult":"START",
    "OperationDateAndTime":"03-Feb-2019 23:50",
    "BatteryStatus":{
      "BatteryChargingStatus":"NOT_CHARGING",
      "BatteryCapacity":"11",
      "BatteryRemainingAmount":"12",
      "BatteryRemainingAmountWH":"",
      "BatteryRemainingAmountkWH":""
    },
    "PluginState":"NOT_CONNECTED",
    "CruisingRangeAcOn":"116112.0",
    "CruisingRangeAcOff":"131856.0",
    "TimeRequiredToFull":{
      "HourRequiredToFull":"0",
      "MinutesRequiredToFull":"40"
    },
    "TimeRequiredToFull200":{
      "HourRequiredToFull":"0",
      "MinutesRequiredToFull":"40"
    },
    "TimeRequiredToFull200_6kW":{
      "HourRequiredToFull":"0",
      "MinutesRequiredToFull":"40"
    },
    "NotificationDateAndTime":"2019/02/03 22:50",
    "TargetDate":"2019/02/03 22:50"
  }
}
"""
    response = json.loads(batteryresponse)
    status = CarwingsLatestBatteryStatusResponse(response)
    assert status.battery_percent == 100    # = 100 * 12 / 12


def test_get_latest_battery_status_30kWh_91percent_0degredation():
    # not connected to a charger - as at 21/01/2019 20:01 (for a 30kWh leaf)
    batteryresponse = """
        {
            "status":200,
            "BatteryStatusRecords": {
                "OperationResult":"START",
                "OperationDateAndTime":"21-Jan-2019 13:29",
                "BatteryStatus":{
                    "BatteryChargingStatus":"NOT_CHARGING",
                    "BatteryCapacity":"240",
                    "BatteryRemainingAmount":"220",
                    "BatteryRemainingAmountWH":"24480",
                    "BatteryRemainingAmountkWH":"",
                    "SOC":{
                        "Value":"91"
                    }
                },
                "PluginState":"NOT_CONNECTED",
                "CruisingRangeAcOn":"146000",
                "CruisingRangeAcOff":"168000",
                "TimeRequiredToFull":{
                    "HourRequiredToFull":"4",
                    "MinutesRequiredToFull":"30"
                },
                "TimeRequiredToFull200":{
                    "HourRequiredToFull":"3"
                    ,"MinutesRequiredToFull":"0"
                },
                "TimeRequiredToFull200_6kW":{
                    "HourRequiredToFull":"1",
                    "MinutesRequiredToFull":"30"
                },
                "NotificationDateAndTime":"2019/01/21 13:29",
                "TargetDate":"2019/01/21 13:29"
            }
        }
"""
    response = json.loads(batteryresponse)
    status = CarwingsLatestBatteryStatusResponse(response)
    assert status.battery_percent == 91

def test_get_latest_battery_status_with_empty_status():
    batteryresponse = """
        {
            "status":200,
            "BatteryStatusRecords": {
                "OperationResult":"START",
                "OperationDateAndTime":"21-Jan-2019 13:29",
                "BatteryStatus": [],
                "PluginState":"NOT_CONNECTED",
                "CruisingRangeAcOn":"146000",
                "CruisingRangeAcOff":"168000",
                "TimeRequiredToFull":{
                    "HourRequiredToFull":"4",
                    "MinutesRequiredToFull":"30"
                },
                "TimeRequiredToFull200":{
                    "HourRequiredToFull":"3"
                    ,"MinutesRequiredToFull":"0"
                },
                "TimeRequiredToFull200_6kW":{
                    "HourRequiredToFull":"1",
                    "MinutesRequiredToFull":"30"
                },
                "NotificationDateAndTime":"2019/01/21 13:29",
                "TargetDate":"2019/01/21 13:29"
            }
        }
"""
    response = json.loads(batteryresponse)
    with pytest.raises(NoDataError):
      CarwingsLatestBatteryStatusResponse(response)
      pytest.fail('Should fail with ValueError')
  
def test_get_latest_battery_status_with_empty_status_records():
    batteryresponse = """
        {
            "status":200,
            "BatteryStatusRecords": []
        }
"""
    response = json.loads(batteryresponse)
    with pytest.raises(NoDataError):
      CarwingsLatestBatteryStatusResponse(response)
      pytest.fail('Should fail with NoDataError')
  
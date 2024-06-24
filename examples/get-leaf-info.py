#!/usr/bin/env python

import pycarwings3
from configparser import ConfigParser
import logging
import sys
import asyncio

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

parser = ConfigParser()
candidates = ['config.ini', 'my_config.ini']
found = parser.read(candidates)

username = parser.get('get-leaf-info', 'username')
password = parser.get('get-leaf-info', 'password')
region = parser.get('get-leaf-info', 'region')
base_url = parser.get('get-leaf-info', 'base_url')

sleepsecs = 30     # Time to wait before polling Nissan servers for update


async def update_battery_status(leaf: pycarwings3.Leaf, wait_time=1):
    key = await leaf.request_update()
    status = await leaf.get_status_from_update(key)
    # Currently the nissan servers eventually return status 200 from get_status_from_update(), previously
    # they did not, and it was necessary to check the date returned within get_latest_battery_status().
    while status is None:
        print("Waiting {0} seconds".format(sleepsecs))
        await asyncio.sleep(wait_time)
        status = await leaf.get_status_from_update(key)
    return status


def print_info(info):
    print("  date %s" % info.answer["BatteryStatusRecords"]["OperationDateAndTime"])
    print("  date %s" % info.answer["BatteryStatusRecords"]["NotificationDateAndTime"])
    print("  battery_capacity2 %s" % info.answer["BatteryStatusRecords"]["BatteryStatus"]["BatteryCapacity"])
    print("  battery_capacity %s" % info.battery_capacity)
    print("  charging_status %s" % info.charging_status)
    print("  battery_capacity %s" % info.battery_capacity)
    print("  battery_remaining_amount %s" % info.battery_remaining_amount)
    print("  charging_status %s" % info.charging_status)
    print("  is_charging %s" % info.is_charging)
    print("  is_quick_charging %s" % info.is_quick_charging)
    print("  plugin_state %s" % info.plugin_state)
    print("  is_connected %s" % info.is_connected)
    print("  is_connected_to_quick_charger %s" % info.is_connected_to_quick_charger)
    print("  time_to_full_trickle %s" % info.time_to_full_trickle)
    print("  time_to_full_l2 %s" % info.time_to_full_l2)
    print("  time_to_full_l2_6kw %s" % info.time_to_full_l2_6kw)
    print("  battery_percent %s" % info.battery_percent)
    print("  state_of_charge %s" % info.state_of_charge)


# Main program
async def main():
    logging.debug("login = %s, password = %s, region = %s" % (username, password, region))

    print("Prepare Session")
    async with pycarwings3.Session(username, password, region, base_url=base_url) as s:
        try:
            print("Login...")
            leaf = await s.get_leaf()

            # Give the nissan servers a bit of a delay so that we don't get stale data
            await asyncio.sleep(1)

            print("get_latest_battery_status from servers")
            leaf_info = await leaf.get_latest_battery_status()
            start_date = leaf_info.answer["BatteryStatusRecords"]["OperationDateAndTime"]
            print("start_date=", start_date)
            print_info(leaf_info)

            # Give the nissan servers a bit of a delay so that we don't get stale data
            await asyncio.sleep(1)

            print("request an update from the car itself")

            await update_battery_status(leaf, sleepsecs)

            latest_leaf_info = await leaf.get_latest_battery_status()
            latest_date = latest_leaf_info.answer["BatteryStatusRecords"]["OperationDateAndTime"]
            print("latest_date=", latest_date)
            print_info(latest_leaf_info)

        except pycarwings3.CarwingsError as e:
            raise e

asyncio.run(main())

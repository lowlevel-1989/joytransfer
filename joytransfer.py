#!/usr/bin/env python3

import os
import time
import argparse
import asyncio
import logging

from multiprocessing import Process
from multiprocessing import Queue

from joycontrol import utils
from joycontrol.controller import Controller
from joycontrol.memory import FlashMemory
from patch_joycontrol.protocol import controller_protocol_factory
from patch_joycontrol.server import create_hid_server


async def _main(args, c, q, reconnect_bt_addr=None):

    # Get controller name to emulate from arguments
    controller = Controller.PRO_CONTROLLER

    # prepare the the emulated controller
    factory = controller_protocol_factory(controller,
                            reconnect = reconnect_bt_addr)

    ctl_psm, itr_psm = 17, 19

    print('', end='\n' if c else ' ')
    print('  Joy Transfer  v0.1')
    print('INFO: Waiting for Switch to connect...', end='\n' if c else ' ')

    if c < 1:
        print('Please open the "Change Grip/Order" menu')

    transport, protocol, ns_addr = await create_hid_server(factory,
                                                  reconnect_bt_addr=reconnect_bt_addr,
                                                  ctl_psm=ctl_psm,
                                                  itr_psm=itr_psm,
                                                  unpair = not reconnect_bt_addr)
    controller_state = protocol.get_controller_state()

    # this is needed
    await controller_state.connect()

    if not reconnect_bt_addr:
        reconnect_bt_addr = ns_addr
        q.put(ns_addr)

    # wait back home in nintendo switch
    if c < 1:
        print('INFO: NINTENDO SWITCH', reconnect_bt_addr)
        if args.auto:
            controller_state.button_state.set_button('a', pushed=True)
            await controller_state.send()
        else:
            print('INFO: Press the button A or B or HOME')
        print()

        while 1:
            await asyncio.sleep(0.2)

    q.put('unlock') # unlock console
    print('hi :3')

    while 1:
        cmd = q.get() # wait command

        await test_button(controller_state, cmd)

'''
NINTENDO SWITCH
    - version 12.1.0
    - version 13.0.0
'''
async def test_button(ctrl, btn):
        available_buttons = ctrl.button_state.get_available_buttons()

        if btn == 'wake':
            # wake up control
            ctrl.button_state.clear()
            await ctrl.send()
            await asyncio.sleep(0.050) # stable minimum 0.050

        if btn not in available_buttons:
            return 1

        ctrl.button_state.set_button(btn, pushed=True)
        await ctrl.send()

        await asyncio.sleep(0.050) # stable minimum 0.050 press
        ctrl.button_state.set_button(btn, pushed=False)
        await ctrl.send()
        await asyncio.sleep(0.020) # stable minimum 0.020 release

        return 0

def handle_exception(loop, context):
    tasks = [t for t in asyncio.all_tasks() if t is not
                         asyncio.current_task()]
    for task in tasks:
        task.cancel()

count = 0

def test(args, c, q, b):
    try:
        loop.run_until_complete(
            _main(args, c, q, b)
        )
    except:
        pass

if __name__ == '__main__':

    # check if root
    if not os.geteuid() == 0:
        raise PermissionError('Script must be run as root!')

    parser = argparse.ArgumentParser()
    parser.add_argument('--auto', dest='auto', action='store_true')
    parser.add_argument('-r', '--reconnect_bt_addr', type=str, default=None,
                        help='The Switch console Bluetooth address (or "auto" for automatic detection), for reconnecting as an already paired controller.')
    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    loop.set_exception_handler(handle_exception)

    queue = Queue()

    cmd = None

    ns_addr = args.reconnect_bt_addr
    if ns_addr:
        count = 1

    for _ in range(2 - count):
        p = Process(target=test, args=(args, count, queue, ns_addr))
        p.start()

        if count < 1:
            ns_addr = queue.get() # wait nintendo switch address
            p.join()
        else:
            queue.get() # lock console

        while p.is_alive():
            cmd = input('cmd >> ')
            if cmd in ['exit', 'quit', 'q', 'bye', 'shutdown']:
                p.kill()
                break

            queue.put(cmd)
            time.sleep(0.2) # not needed

        # wait reconnection
        time.sleep(2) # important 2 or more
        count += 1

    print("bye")

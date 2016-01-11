import future_snap_connect
from snapconnect import snap

from tornado.gen import coroutine

import tornado
import asyncore
import apy

import logging
logging.basicConfig(level=logging.INFO)

#Modify these values for your configuration.
serial_type = snap.SERIAL_TYPE_SNAPSTICK100
serial_port = 0
node_addr = '5de663'


#Snap Connect Futures (SCF) setup.  Check the SCF Quick Start guide for an in-depth explanation of the setup.
scheduler = apy.ioloop_scheduler.IOLoopScheduler.instance()

sc = snap.Snap(scheduler=scheduler, funcs={})
#Notice that you don't have to pass any callback methods into our SNAP instances.
#These will all be automatically handled by Snap Connect Futures.
scf = future_snap_connect.FutureSnapConnect(sc)

tornado.ioloop.PeriodicCallback(asyncore.poll, 5).start()
tornado.ioloop.PeriodicCallback(sc.poll_internals, 5).start()

@coroutine
def setup_serial():
    logging.info("Connecting to serial...")
    yield scf.open_serial(serial_type, serial_port)

@coroutine
def cause_temporary_outage(time):
    #RPC will send the RPC message without any follow-ups.
    logging.info("Simulating an outage by turning off the radio for {} seconds.".format(time))
    yield scf.rpc(node_addr, 'simulate_outage', time)

@coroutine
def simple_callback_rpc():
    #Most Basic example possible. Futures will automatically add the callback handler for you.
    #After the Future is resolved (success or failure) the callback handler will be removed.
    response = yield scf.callback_rpc(node_addr, "generic_response")
    logging.info("Responses: {}".format(response))

@coroutine
def expect_special_callback():
    #If you need to expect a specific return, you can specify a callback_name. (vmStat and tellVmStat, for example.)
    #The SNAPpy script will send a mcastRpc with 'the_wrong_callback' the first 2 times
    #The 3rd retry, it will send a mcastRpc with 'special_callback_name'.
    #Futures will only resolve when the proper callback is received.
    yield scf.rpc(node_addr, 'reset_counter')
    response = yield scf.callback_rpc(node_addr, "explicit_response", callback_name="explicit_callback")
    logging.info("Responses: {}".format(response))

@coroutine
def retries_and_timeouts():
    #Callback_rpc will default to timeout=2 retries=3
    yield cause_temporary_outage(7)
    first_delayed_response = yield scf.callback_rpc(node_addr, "generic_response")
    logging.info("Responses: {}".format(first_delayed_response))
    #Retries and Timeouts can be set manually as well.
    yield cause_temporary_outage(5)
    second_delayed_response = yield scf.callback_rpc(node_addr, "generic_response", retries=1, timeout=1)
    logging.info("Responses: {}".format(second_delayed_response))

@coroutine
def dropped_response():
    #If no response is returned before retries are exhausted, the Future resolves and returns 'None'.
    yield cause_temporary_outage(5)
    response = yield scf.callback_rpc(node_addr, "generic_response", retries=0, timeout=1)
    if not response:
        logging.info("'{}' is yielded after retries and timeouts are exhausted.".format(response))


@coroutine
def main():
    yield setup_serial()
    yield simple_callback_rpc()
    yield expect_special_callback()
    yield retries_and_timeouts()
    yield dropped_response()

    my_loop.stop()

if __name__ == "__main__":

    main()
    my_loop = tornado.ioloop.IOLoop.instance()
    my_loop.start()


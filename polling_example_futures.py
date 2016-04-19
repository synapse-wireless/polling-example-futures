from snapconnect_futures import SnapConnectFutures
from snapconnect import snap

from tornado.gen import coroutine
import tornado

import logging
logging.basicConfig(level=logging.INFO)

# Modify these values for your configuration.
serial_type = snap.SERIAL_TYPE_SNAPSTICK100
serial_port = 0
# Replace node_addr with a specific MAC address.  If you leave it as None, the example will use your bridge node.
node_addr = None

# Snap Connect Futures (SCF) setup.  Check the SCF Quick Start guide for an in-depth explanation of the setup.
# Notice that you don't have to pass any callback methods into our SNAP instances.
sc = snap.Snap(funcs={})

# These will all be automatically handled by Snap Connect Futures.
scf = SnapConnectFutures(sc)

tornado.ioloop.PeriodicCallback(sc.poll, 5).start()

@coroutine
def setup_serial():
    global node_addr
    logging.info("Connecting to serial...")
    # The open_serial future returns the bridge node's MAC Address.
    bridge_address = yield scf.open_serial(serial_type, serial_port)
    if bridge_address is None:
        logging.info("Unable to connect to bridge node")
    else:
        logging.info("Connected to bridge with MAC: {}".format(bridge_address))
        if node_addr is None:
            node_addr = bridge_address

@coroutine
def cause_temporary_outage(time):
    # RPC will send the RPC message without any follow-ups.
    logging.info("Simulating an outage by turning off the radio for {} seconds.".format(time))
    yield scf.rpc(node_addr, 'simulate_outage', time)

@coroutine
def simple_callback_rpc():
    # Most Basic example possible. Futures will automatically add the callback handler for you.
    # After the Future is resolved (success or failure) the callback handler will be removed.
    response = yield scf.callback_rpc(node_addr, "simple_call")
    # Callback futures are returned as a tuple on success, or None on failure.
    if response is None:
        logging.info('Callback not received.')
    else:
        logging.info("Responses: {}".format(response[0]))

@coroutine
def expect_special_callback():
    '''
    If you need to expect a specific return, you can specify a callback_name. (vmStat and tellVmStat, for example.)
    The SNAPpy script will send a mcastRpc with 'the_wrong_callback' the first 2 times
    The 3rd retry, it will send a mcastRpc with 'explicit_callback'.
    Futures will only resolve when the proper callback is received.
    '''
    # This RPC just resets a counter on the SNAP Node.
    yield scf.rpc(node_addr, 'reset_counter')
    response = yield scf.callback_rpc(node_addr, "explicit_call", callback_name="explicit_response")
    if response is None:
        logging.info('Callback not received.')
    else:
        logging.info("Responses: {}".format(response[0]))

@coroutine
def retries_and_timeouts():
    # Callback_rpc will default to timeout=2 retries=3
    yield cause_temporary_outage(7)
    first_delayed_response = yield scf.callback_rpc(node_addr, "delay_call_one")
    if first_delayed_response is None:
        logging.info('First delayed callback not received.')
    else:
        logging.info("Responses: {}".format(first_delayed_response[0]))
    # Retries and Timeouts can be set manually as well.
    yield cause_temporary_outage(5)
    second_delayed_response = yield scf.callback_rpc(node_addr, "delay_call_two", retries=1, timeout=1)
    if second_delayed_response is None:
        logging.info('Second delayed callback not received.')
    else:
        logging.info("Responses: {}".format(second_delayed_response[0]))

@coroutine
def dropped_response():
    # If no response is returned before retries are exhausted, the Future resolves and returns 'None'.
    yield cause_temporary_outage(5)
    response = yield scf.callback_rpc(node_addr, "dropped_call", retries=0, timeout=1)
    if response is None:
        logging.info("'{}' is yielded after retries and timeouts are exhausted.".format(response))
    else:
        logging.info("Honestly, we expected this to fail...")

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
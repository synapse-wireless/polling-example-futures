import logging
from snapconnect import snap

Log = logging.getLogger(__name__)

TEST_ADDR = '\x03\xC1\x61'

call =  ['setup_serial', 'simple_callback_rpc', 'expect_special_callback','retries_and_timeouts', 'dropped_response']


class SNAPConnectPoller(object):

    def __init__(self, serial_type, serial_port):
        self.responseFunc = {
                            'simple_callback' : self.simple_callback,
                            'special_callback' : self.special_callback,
                            'custom_retry_timeout_callback' : self.custom_retry_timeout_callback,
                            'dropped_callback' : self.dropped_callback,
                            }

        self.serial_type = serial_type
        self.serial_port = serial_port
        self.response = None
        self.resp_flag = False
        self.attempt = 0
        self.active_call = None
        self.queue = []

        self.sc = snap.Snap(funcs = self.responseFunc)
        self.snap.open_serial(serial_type, serial_port)

    def run(self):
        self.next_call()

    def next_call(self):
        if len(self.queue) == 0:
            print 'All scheduled call completed'
            self.snap.close_serial(self.serial_type, self.serial_port)
            exit()
        else:
            self.resp_flag = False
            self.active = self.queue.pop(0)
            self.active_call = self.active[0]
            self.active_callback = self.active[1]
            self.timeout = self.active[2]
            self.retries = self.active[3]
            self.attempt = 0
            self.sc.scheduler.schedule(self.timeout, self.handle_timeout)
            self.active_call()

    def callback_rpc(self, rpc_method, callback, retries=2, timeout=3):
        self.queue.append((rpc_method, callback, retries, timeout))

    def handle_timeout(self):
        if self.attempt > self.retries:


    def check_active(self):
        #check if callback is the active callback
        #if so, trip response flag
        #disable timer

# -----------------------------------------------------------------------------
#   Calls
# -----------------------------------------------------------------------------

    def sync(self):
        '''RCB does not respond to this call.  This tells the RCB to gather
        data from the SCB in preparation for a getData call.'''
        Log.info('Sending sync.')
        self.snap.rpc(TEST_ADDR, 'sync', self.seq, True)
        self.seq += 1
        #need to wait ~6 seconds before sending rpc after a sync.
        self.snap.scheduler.schedule(7, self.next_call)

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
    def cause_temporary_outage(self, time):
        # RPC will send the RPC message without any follow-ups.
        logging.info("Simulating an outage by turning off the radio for {} seconds.".format(time))
        yield scf.rpc(node_addr, 'simulate_outage', time)

    @coroutine
    def simple_callback_rpc(self):
        # Most Basic example possible. Futures will automatically add the callback handler for you.
        # After the Future is resolved (success or failure) the callback handler will be removed.
        response = yield scf.callback_rpc(node_addr, "generic_response")
        # Callback futures are returned as a tuple on success, or None on failure.
        if response is None:
            logging.info('Callback not received.')
        else:
            logging.info("Responses: {}".format(response[0]))

    @coroutine
    def expect_special_callback(self):
        '''
        If you need to expect a specific return, you can specify a callback_name. (vmStat and tellVmStat, for example.)
        The SNAPpy script will send a mcastRpc with 'the_wrong_callback' the first 2 times
        The 3rd retry, it will send a mcastRpc with 'explicit_callback'.
        Futures will only resolve when the proper callback is received.
        '''
        # This RPC just resets a counter on the SNAP Node.
        yield scf.rpc(node_addr, 'reset_counter')
        response = yield scf.callback_rpc(node_addr, "explicit_response", callback_name="explicit_callback")
        if response is None:
            logging.info('Callback not received.')
        else:
            logging.info("Responses: {}".format(response[0]))

    @coroutine
    def retries_and_timeouts_one(self):
        # Callback_rpc will default to timeout=2 retries=3
        yield cause_temporary_outage(7)
        first_delayed_response = yield scf.callback_rpc(node_addr, "generic_response")
        if first_delayed_response is None:
            logging.info('First delayed callback not received.')
        else:
            logging.info("Responses: {}".format(first_delayed_response[0]))

    def retries_and_timeouts_two(self):
        # Retries and Timeouts can be set manually as well.
        yield cause_temporary_outage(5)
        second_delayed_response = yield scf.callback_rpc(node_addr, "generic_response", retries=1, timeout=1)
        if second_delayed_response is None:
            logging.info('Second delayed callback not received.')
        else:
            logging.info("Responses: {}".format(second_delayed_response[0]))

    @coroutine
    def dropped_response():
        # If no response is returned before retries are exhausted, the Future resolves and returns 'None'.
        yield cause_temporary_outage(5)
        response = yield scf.callback_rpc(node_addr, "generic_response", retries=0, timeout=1)




# -----------------------------------------------------------------------------
#  Responses
# -----------------------------------------------------------------------------

    def simple_callback(self):
        pass

    def explicit_callback(self):
        pass

    def the_wrong_callback(self):
        pass

    def custom_retry_timeout_callback(self):
        pass

    def dropped_callback(self):
        if response is None:
            logging.info("'{}' is yielded after retries and timeouts are exhausted.".format(response))
        else:
            logging.info("Honestly, we expected this to fail...")

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    test = RCBv1_Tester() # Instantiate a client instance
    test.main(v37_Testing) # Start first test
    test.snap.loop()
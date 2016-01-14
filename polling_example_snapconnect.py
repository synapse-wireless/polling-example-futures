import logging
from snapconnect import snap

node_addr = '\x5D\xE6\x63'
serial_type = snap.SERIAL_TYPE_SNAPSTICK100
serial_port = 0

class SNAPConnectDispatcher(object):
    '''
    A simple dispatcher that generates a queue of RPCs to be sent while retries and timeouts.  This is meant to help
    show a realistic side-by-side comparison of the value of utilizing SNAP Connect Futures.  This script has the same
    functionality as the Futures implementation but is much harder to troubleshoot and much more prone to typos and bugs
    since there are many situations where you need to cross reference the same variable in 4 or 5 separate places.
    '''

    def __init__(self, node_addr, serial_type, serial_port):
        '''
        :param node_addr: 6-byte hex string that is the target of the rpc calls.
        :param serial_type: Bridge type. See Snap Reference Manual for more info.
        :param serial_port: COM Port. 0 = COM 1, 1 = COM 2, dev/tty1 can be used for linux system.
        :return:
        '''

        logging.info('Initializing SNAP Connect instance.')

        # You have to manually register your callbacks using traditional SNAP Connect methods.
        # It's possible to hide this behind-the-scenes and register them on the fly similar to how SNAP Connect Futures
        # handles it, but it would be more code than just registering the callbacks in this scenario.
        self.func = {
                    'simple_response' : self.simple_response,
                    'explicit_response' : self.explicit_response,
                    'the_wrong_response' : self.the_wrong_response,
                    'delay_response_one' : self.delay_response_one,
                    'delay_response_two' : self.delay_response_two,
                    'dropped_response' : self.dropped_response
                    }

        self.serial_type = serial_type
        self.serial_port = serial_port
        self.response = None
        self.timeout_event = None
        self.attempt = 0
        self.active_rpc = None
        self.queue = []

        # Make your SNAP Instance.
        self.sc = snap.Snap(funcs = self.func)
        self.sc.open_serial(serial_type, serial_port)

    def call(self):
        '''
        Pops, initializes, and calls the next rpc in the queue.  Timeout timer is started here, as well.
        '''
        if len(self.queue) == 0:
            logging.info('All scheduled calls completed')
            self.sc.close_serial(self.serial_type, self.serial_port)
            exit()
        else:
            if self.timeout_event:
                self.sc.scheduler.unschedule(self.timeout_event)

            # Pop the first rpc off the queue and unpack any data stored with it
            self.active = self.queue.pop(0)
            self.active_rpc = self.active[0]
            self.active_callback = self.active[1]
            self.timeout = self.active[2]
            self.retries = self.active[3]
            self.delay = self.active[4]

            self.attempt = 0
            self.timeout_event = self.sc.scheduler.schedule(self.timeout, self.handle_timeout)

            # For this example, cause_temporary_outage is somewhat hard to call.  We could either add a handler here or
            # use the queue_callback_rpc function to queue up the calls each time like we did with the one
            # reset_explicit_counter call.
            if self.delay:
                self.cause_temporary_outage(self.delay)

            # Call the active_rpc method to kick of the rest of the state machine.
            self.active_rpc()

    def queue_callback_rpc(self, rpc_method, callback, retries=2, timeout=3, delay=None):
        '''
        An attempt at creating a method of queueing and storing data relevant to rpc calls in a reasonable fashion.
        :param rpc_method: Direct reference to the method that needs to be queued
        :param callback: str used to verify if the callback should be acted on.
        :param retries: num of retries before failing the current rpc.
        :param timeout: num of seconds to wait before retries.
        :param delay: num of seconds the node needs to simulate an outage for.
        '''
        self.queue.append((rpc_method, callback, retries, timeout, delay))

    def handle_timeout(self):
        '''
        Checks the num of attempts against the num of retries and either fails or re-calls the active rpc.
        '''
        if self.attempt > self.retries:
            logging.info("No response received from SNAP Node.")
            self.call()
        else:
            self.attempt += 1
            #reset the timeout counter and call the active_rpc again.
            self.timeout_event = self.sc.scheduler.schedule(self.timeout, self.handle_timeout)
            self.active_rpc()

    def check_if_active(self, active_callback):
        '''
        Check to see if the active callback is the callback we're current waiting and ignores it if not.
        :param active_callback: str that correlates to the 'callback' str passed into queue_callback_rpc.
        :return:
        '''
        if self.active_callback != active_callback:
            logging.info('Ignoring callback: {}'.format(active_callback))
            return False
        else:
            #unchedule the timeout counter if we got the callback we were waiting on.
            self.sc.scheduler.unschedule(self.timeout_event)
            return True

# -----------------------------------------------------------------------------
#   Calls
# -----------------------------------------------------------------------------

    # It's somewhat a matter of choice on whether you want to keep your call and responses separated.  If you only have
    # 1 to 1 relationships, you can reorganize the code to be easier to follow, but things get complicated and harder
    # to read when you have some rpcs with no callbacks and some rpcs that may have multiple callbacks it needs to
    # handle or state machines it needs to interface with.
    def cause_temporary_outage(self, time):
        logging.info("Simulating an outage by turning off the radio for {} seconds.".format(time))
        self.sc.rpc(node_addr, 'simulate_outage', time)

    def reset_explicit_counter(self):
        logging.info("Resetting counter for explicit callback example")
        self.sc.rpc(node_addr, 'reset_counter')
        self.call()

    def simple_callback(self):
        logging.info("Sending RPC for simple_callback")
        self.sc.rpc(node_addr, 'callback', 'simple_response', 'simple_call')

    def expect_special_callback(self):
        logging.info("Sending RPC for expect_special_callback")
        self.sc.rpc(node_addr, "explicit_call")

    def retries_and_timeouts_one(self):
        logging.info("Sending RPC for retries_and_timeouts_one")
        self.sc.rpc(node_addr, "callback", "delay_response_one", "delay_call_one")

    def retries_and_timeouts_two(self):
        logging.info("Sending RPC for retries_and_timeouts_two")
        self.sc.rpc(node_addr, "callback", "delay_response_two", "delay_call_two")

    def dropped_call(self):
        logging.info("Sending RPC for dropped_call")
        self.sc.rpc(node_addr, "callback", "dropped_response", "dropped_call")

# -----------------------------------------------------------------------------
#  Responses
# -----------------------------------------------------------------------------

    def simple_response(self, response):
        if self.check_if_active("simple_response"):
            logging.info("Simple Response: {}".format(response))
            self.call()

    def explicit_response(self, response):
        if self.check_if_active("explicit_response"):
            logging.info("Explicit Response: {}".format(response))
            self.call()

    def the_wrong_response(self, response):
        if self.check_if_active("the_wrong_response"):
            logging.info("Wrong Response: {}".format(response))
            self.call()

    def delay_response_one(self, response):
        if self.check_if_active("delay_response_one"):
            logging.info("Delay One Response: {}".format(response))
            self.call()

    def delay_response_two(self, response):
        if self.check_if_active("delay_response_two"):
            logging.info("Delay Two Response: {}".format(response))
            self.call()

    def dropped_response(self, response):
        if self.check_if_active("dropped_response"):
            logging.info("Honestly, we expected this to fail... {}".format(response))
            self.call()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    # Generate a dispatcher and queue up the necc. rpc calls.
    dispatch = SNAPConnectDispatcher(node_addr, serial_type, serial_port)
    dispatch.queue_callback_rpc(dispatch.simple_callback, 'simple_response')
    dispatch.queue_callback_rpc(dispatch.reset_explicit_counter, None, 0, 0)
    dispatch.queue_callback_rpc(dispatch.expect_special_callback, 'explicit_response')
    dispatch.queue_callback_rpc(dispatch.retries_and_timeouts_one, 'delay_response_one', delay=5)
    dispatch.queue_callback_rpc(dispatch.retries_and_timeouts_two, 'delay_response_two', 2, 2, 4)
    dispatch.queue_callback_rpc(dispatch.dropped_call, 'dropped_response', 0, 0, )
    # Kick off the dispatcher
    dispatch.call()
    # Turn over control of the processes to the SNAP IO Loop.
    dispatch.sc.loop()
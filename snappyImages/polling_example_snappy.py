def simulate_outage(time):
    rx(False)
    sleep(time)
    rx(True)

def simple_call():
    return "Callback Returned!"

resp = 0

def explicit_call():
    global resp
    if resp == 2:
        mcastRpc(1, 2, 'explicit_response', 'Mcast sent from explicit.')
    else:
        resp += 1
        mcastRpc(1, 2, 'the_wrong_response', 'Mcast sent from wrong.')

def delayed_call():
    return "I should have been delayed."

def reset_counter():
    global resp
    resp = 0

def delay_call_one():
    return "There are built in retries and timeouts!"

def delay_call_two():
    return "Retries and timeouts can be set manually, too!"

def dropped_call():
    return "You should never see this."


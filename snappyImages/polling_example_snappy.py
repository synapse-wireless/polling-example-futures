resp = 0

def generic_response():
    return "Callback Returned!"

def simulate_outage(time):
    rx(False)
    sleep(time)
    rx(True)

def reset_counter():
    global resp
    resp = 0

def explicit_response():
    global resp
    if resp == 2:
        mcastRpc(1, 2, 'explicit_callback', 'Explicit')
    else:
        resp += 1
        mcastRpc(1, 2, 'the_wrong_callback', 'Wrong')


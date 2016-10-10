[![](https://cloud.githubusercontent.com/assets/1317406/12406044/32cd9916-be0f-11e5-9b18-1547f284f878.png)](http://www.synapse-wireless.com/)

# Polling Example Futures - Basic node-polling using SNAPconnect Futures

`Polling Example Futures` is a fairly straight-forward example project 
that highlights some of the value-adding features built into SNAPconnect
Futures.

The project includes a SNAPpy script with very basic functionality. The 
script has several functions that simply return values, but also 
includes a `simulate_outage(time)` function that allows you to simulate
breaks in connectivity with the node by putting the node to sleep with
the radio turned off.

## Background

Many SNAPconnect applications tend to follow a standard format:

1.  A SNAP Node has some kind of valuable data that needs to be collected.

1.  Create a method on the node to collect and return polled data.

1.  Send callback RPC to the node and wait for a response.

1.  The node's callback response triggers the SNAPconnect method, which
    kicks off subsequent events.

1.  Repeat ad infinitum.

There are two significant challenges with this:

-   The first is that maximizing throughput is difficult, since having 
    your host send messages out to poll your nodes as quickly as it can 
    doesn't leave any bandwidth available for receiving replies from the 
    nodes it is polling. Queueing RPC calls to query nodes as quickly as the 
    host can generate them gets the messages queued for output (until you 
    run out of buffers), but doesn't send the messages efficiently. 
    Triggering the sending of RPC calls from the RPC_SENT hook improves the 
    system efficiency, but still leaves no bandwidth for the host to receive 
    replies from the nodes it is polling.

-   The second is that managing the sending and receiving of messages 
    typically requires setting up event-driven state machines, which can 
    make your code complex, difficult to understand, and even harder to
    maintain. By the time you add in other mechanisms, such as retries or 
    timeouts, or recovery from dropped packets, even relatively simple
    applications can grow unwieldy very quickly.

The Futures package for SNAPconnect solves these problems by simulating
a synchronous environment when you can simply wait for data to be 
returned. SNAPconnect Futures also has built-in retry/timeout
mechanisms to help provide more reliable communications with less
overhead. This lends itself to creating much more straight-forward code 
which, in turn, means faster development and easier bug-fixes in the 
future.

## How SNAPconnect Futures Helps

The main code has an example of connecting to a bridge node, five 
examples of using the new callback_rpc feature in SNAPconnect Futures,
and examples of handling callbacks, all with plenty of comments 
throughout.

While not terribly exciting code, a simple 6 line callback example 
implemented using SNAPconnect Futures provides a drastic improvement
over the traditional method:

 * make a callback method and register it on the SNAP instances 
function list, 
 * define a state machine to handle the retry mechanism, 
 * implement a timer mechanism to handle timeouts, 
 * define a method to send the rpc. 

This example includes two files, `polling_example_futures.py` and 
`polling_example_snapconnect.py`, providing parallel examples of the 
code required to poll a node using SNAPconnect Futures, and having to
implement the infrastructure to support callbacks, state machines, and 
timeouts. While it is entirely possible to reproduce the exact same 
functionality using only SNAPconnect, using SNAPconnect Futures
creates a much more streamlined codebase.

## Installation

First, download the example, either by cloning the repository with Git, 
or by downloading and unzipping the zip archive. Then, using pip, 
install the required Python packages for the example, which include 
SNAPconnect Futures:

```bash
pip install -r requirements.txt
```

## Running This Example

Connect to a SNAP-powered network and load `snappyImages/polling_example_snappy.py` 
to a node (your bridge or another node) using Portal. Disconnect Portal, 
so that your SNAPconnect application can use the bridge node. Change
the parameters at the top of the `polling_example_futures.py` script 
based on the type and serial port of the bridge node:

```python
# Modify these values for your configuration.
serial_type = snap.SERIAL_TYPE_SNAPSTICK100
serial_port = 0
# Replace node_addr with a specific MAC address.
# If you leave it as None, the example will use your bridge node.
node_addr = None
```

Then, run the example:

```bash
python polling_example_futures.py 
```

This will run and print out some relevant log data to the console.

## License

Copyright © 2016 [Synapse Wireless](http://www.synapse-wireless.com/), 
licensed under the [Apache License v2.0](LICENSE.md).

<!-- meta-tags: vvv-snapconnect, vvv-python, vvv-example -->

[![](https://cloud.githubusercontent.com/assets/1317406/12406044/32cd9916-be0f-11e5-9b18-1547f284f878.png)](http://www.synapse-wireless.com/)

# Polling Example Futures - Basic node-polling using SNAPconnect Futures

`Polling Example Futures` is a fairly straight-forward example that highlights 
some of the value-adding features built into SNAPconnect Futures.

Included is a SNAPpy script with very basic functionality. The script uses very standard SNAPpy practices,
with the exception of simulating dropped or delayed packets by turning off the Node's radio 
and having it sleep temporarily.

## Background

Many SNAPconnect applications tend to follow a standard format:

1. A SNAP Node has some kind of valuable data that needs to be collected. 
1. Create a callback method to handle collected/polled data from a node.
1. Send callback rpc to the node and wait for a response.
1. Response triggers the callback method which kicks off subsequent events.
1. Repeat ad infinitum.

Problem: It can be confusing as to what is actually happening, especially if you 
are viewing source code that you didn't write.  Traditional implementations are
very reliant on state-machines since everything has to be event-driven, as well.
In most cases, as soon as you get past the simplest applications, the complexity 
of your applications will begin to expand drastically.  Once you add in other
mechanisms such as retries/timeouts and dropped package handling, it's easy to 
see how even relatively simple applications can become more complex over time.

Solution: Use Futures to simulate a synchronous environment where you can 
simply wait for data to be returned.  SNAPconnect Futures also has built-in 
retry/timeout mechanisms to help provide more reliable communications with less 
overhead. This lends itself to creating much more straight-forward code which, 
in turn, means faster iteration and easier bug-fixes in the future.

Many SNAPconnect applications are built to gather data from the remote nodes as quickly
as possible.

Here are some approaches that **don't** work well.

#### Blindly enqueueing RPC calls

Since the packets have to be transferred "out" via either a serial or TCP/IP link,
blindly enqueueing lots of RPC calls just queues them up INSIDE your PC.

#### Queueing RPC calls based on HOOK_RPC_SENT, but with no regard for incoming replies

If you are sending COMMANDS (no return RPC call), triggering their transmission off
of the HOOK_RPC_SENT event is sufficient. However, if those outbound RPC calls are
going to result in INCOMING RPC calls, you need to give the remote nodes a chance to 
"get a word in edgewise".

## Running This Example

The main code has an example of connecting to a bridge node, 5 examples of
using SNAPconnect Futures new callback_rpc, and handling callbacks with plenty
of comments throughout.  While not terribly exciting, a simple 6 line callback 
example implemented using SNAPconnect Futures provides a drastic improvement 
over the traditional method which would have required a callback method to be 
made and registered on the SNAP instances function list, a state machine 
created to handle the retry mechanism, a separate timer mechanism implemented 
to handle timeouts, and finally, a method to send the rpc.  Included in this
example is `polling_example_snapconnect.py`, which is a SNAPconnect
implementation of the same functionality provided by `polling_example_futures.py`.
While it is entirely possible to create the exact same application using only
SNAPconnect, utilizing SNAPconnect Futures can create a much more stream-lined
codebase.

To run the example, simply connect a SNAP Bridge and, using Portal, load 
`polling_example_snappy.py` to the node. Assuming the bridge is connected 
on COM Port 1 (modify the config parameters at the top of the example, if needed)
and SNAPconnect Futures is properly installed, you can run:

```bash
python polling_example_futures.py 
```

This will run the examples and print out the relevant log data from the SNAP 
Communications to the console.

## License

Copyright © 2016 [Synapse Wireless](http://www.synapse-wireless.com/), licensed under the [Apache License v2.0](LICENSE.md).

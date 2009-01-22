#from orbited import json
#from moksha.hub import MokshaHub

## @@ This is currently leaking socket descriptors...

#def send_message(topic, message):
#    """ Send a `message` to a specific `topic` """
#
#    # Right now we're instantiating a new connection & channel each message..
#    # we could potentially do this in the DataStreamer...
#    # each could have their own Connection...
#    # or, the MokshaHub could instantiate all DataStreamers with their
#    # own channel?
#    hub = MokshaHub()
#
#    # Automatically encode non-strings to JSON
#    if not isinstance(message, basestring):
#        message = json.encode(message)
#
#    hub.send_message(message, routing_key=topic)
#
#    hub.stop()
#    del(hub)

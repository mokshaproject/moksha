The Moksha Command-Line Client
==============================

The moksha command-line tool can be used to perform various tasks, such as
starting up the entire Moksha stack for quick development/deployment, listing
installed componets, and sending messages to the broker.  It is a fairly new
piece of Moksha, and will grow more features in the future.

.. code-block:: bash

   $ moksha --help
   Usage: moksha [command]

    The Moksha Command-line Interface

   Options:
     -h, --help  show this help message and exit
     --start     Start Moksha
     --list      List all installed Moksha components
     --send      Send a message to a given topic. Usage: send <topic> <message>


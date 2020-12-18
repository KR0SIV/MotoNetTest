# MotoNetTest
Simple GUI/Py Application to Test UDP Traversal on a Network - Specifically for Motorola Repeater Installations

This application is both the client and the server, everything is configurable and messages such as ping/packet count are sent over the configured master UDP port with a "SYSMSG" header so that the applications can communicate using the same channel a repeater would.

The goal is to prevent an IT department from saying "I can ping it, everything should work" and walking away. If you know anything about IT/Networking you know that Ping while useful does NOT show the whole picture. This tool is intended to help you test that UDP can traverse the network on the required ports and if it cannot that you'll have more information to provide the IT department so they can fix their routing issues.

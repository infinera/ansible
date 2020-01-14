# Changing Default Password

This document provides sequence of operations required to change the password and the access privileges of a user.

## TL1 Interface

Transaction Language 1 (TL1) is an industry-recognized common language protocol for communicating with network elements. The TL1 Interface uses the common language protocol to eliminate the need for vendor-specific interfaces.
In order to launch the TL1 interface connection to the Network Element must be established

### Connecting to a Target Network Element

In-order to connect the TL1 interface a TL1 session needs to be launched.

This can be done by running the following in the shell command prompt

```shell
> telnet 10.220.165.84 9090
```

Here the the `telnet` command is used along with the `ipaddress` of the Network Element and the TL1 Interface `port` which is `9090`.

The following prompt will be displayed indicating a successful launch of a TL1 session.

```shell
Trying 10.220.165.84...
Connected to 10.220.165.84.
Escape character is '^]'.

TL1>>

Copyright (c) 2003-2013 Infinera Corporation. All rights reserved.

Legal Notice:

This product contains copyright material licensed from AdventNet, Inc. http://www.adventnet.com. All rights to such copyright material rest with AdventNet.

Copyright (c) 199x-20xx Metaswitch Networks.

The following software is licensed under the terms of the GNU Lesser General Public License version 2.1: (1) javax jnlp (2) Glazed Lists (3) netx jnlp (4) RSTP library - Rapid Spanning Tree (802.1t, 802.1w). Copyright (C) 2001-2003 Optical Access.  Author: Alex Rozin (5) ftplib.c - callable ftp access routines.  Copyright (C) 1996, 1997, 1998 Thomas Pfau, pfau@cnj.digex.net, 73 Catherine Street, South Bound Brook, NJ, 08880. (6) Avahi service discovery suite - DNS Service Discovery (DNS-SD RFC 6763) over Multicast DNS (mDNS RFC 6762). Copyright 2004-2015 by the Avahi developers. (7) libsocket.so.2 (8) curl (9) RapidJson, licensed under the MIT License. You may obtain a copy of the GNU Lesser General Public License version 2.1 at: http://www.gnu.org/licenses/lgpl.html.

TL1>>
```

The session can be closed using `ctrl + ]` keys.

### Logging Into the TL1 Interface

Use the ACT-USER command to login - ACT-USER:[<TID>]:<UID>:<CTAG>::<PID>;

* TID - Target Network Element Identifier --- The name of the Network Element. For. E.g., XTC286
* UID - Username Identifier --- The Username
* CTAG - Input, Response Correlation Tag --- Can be taken as ctag as shown below
* PID - Password Identifier --- The password for the username

Example Input/Response

```shell
ACT-USER::username:ctag::*********;
   node3 09-02-16 08:53:13
M  ea COMPLD
   "username:2016-02-15,10-56-41,0"
;
```

> The COMPLD string indicates that the command has been executed successfully

### Changing the Default Password

Use the ED-USER-SECU command to edit the password and access privileges.

ED-USER-SECU:[<TID>]:<UID>:<CTAG>::,[<newpid>],,[<uap>];

* TID - Target Network Element Identifier --- The name of the Network Element. For. E.g., XTC286
* UID - Username Identifier --- The Username
* CTAG - Input, Response Correlation Tag --- Can be taken as ctag as shown below
* newpid - New Password Identifier --- The new password for the user
* uap - User access privilege --- The access privilege of the user(See below)

```shell
TL1>>ed-user-secu::username:ctag::,**********,,RA;


   XTC287 20-01-10 09:50:12
M  asd COMPLD
;
```

#### User Access Privileges

Multiple access privileges are defined to restrict user access to resources. Each access privilege allows a
specific set of actions to be performed. Assign one or more access privileges to each user account. The
levels of access privileges are:

* Monitoring Access (MA)—allows user to monitor the network element, but not to modify anything on the network element (read-only privilege). The Monitoring Access is provided to all users by default.
* Security Administrator (SA)—allows the user to perform network element security management and administration related tasks.
* Network Administrator (NA)—allows the user to monitor the network element, manage equipment, turn-up network element, provision services, administer various network-related functions such as Auto-discovery and topology.
* Network Engineer (NE)—allows the user to monitor the network element and manage equipment.
* Provisioning (PR)—allows the user to monitor the network element, configure facility endpoints and provision services.
* Test and Turn-up (TT)—allows the user to monitor, turn-up and troubleshoot the network element and fix network problems.
* Restricted Access (RA)—allows the user to disable Automatic Laser Shutdown (ALS) operation. A user may not disable the ALS feature unless the user’s account is configured with “Restricted Access” privileges.

### Logging Out of the TL1 Interface

Use the CANC-USER command to logout - CANC-USER:[<TID>]:<UID>:<CTAG>;

* TID - Target Network Element Identifier --- The name of the Network Element. For. E.g., XTC286
* UID - Username Identifier --- The Username
* CTAG - Input, Response Correlation Tag --- Can be taken as ctag as shown below

Example Input/Response

```shell
TL1>>CANC-USER::username:ctag;


   XTC287 20-01-10 10:58:02
M  ads COMPLD
;
```

memery
======

The third incarnation of the infamous ircbot. Not with less ugly pos code!

Written in Python 3, not compatible with Python 2.


Usage
-----

memery is very dynamic and almost everything can be done without losing the IRC
connection. For administration there are several commands available.

### Administrator commands

The administrator commands can only be executed by someone who matches any
regex in the adminlist configuration file (further details in the section
about config files.)

All administrator commands share the same syntax:

* `bot-nick: <administrator command>`, or
* `bot-nick, <administrator command>`.

The different administrator commands are as follows.

* `help`: Shows a list of administrator commands.
* `stfu`: Toggles memery's *quiet* state. When memery is quiet, she will idle
and only listen to administrator commands -- no other commands or plugins. The
current state of quietness is indicated by whether memery is marked as away.
* `update config`: Re-reads the config. If the config is changed, the changes
will be applied live. This is currently the preferred way to join/part channels,
change nickname, change servers etc. Updating the config will try to apply the
config as if memery was freshly started, but will not perform anything related
to parts that aren't changed. (E.g. if the server or port isn't changed, memery
will not drop the current connection either. If it is, she will reconnect to
the new server.)
* `reload`: Reloads large parts of memery without dropping the IRC connection.
Useful for updating memery to the current versions of `interpretor.py`,
`ircparser.py` and `common.py`.
* `restart`: Reboots almost all of memery. Needs to be done to update memery to
the current version of `irc.py`, otherwise probably unneeded.
* `reconnect`: Simply reconnects to the current IRC server. There is, as far as
I can see, no reason to invoke this command manually at all.
* `quit`: Terminates memery completely. Should very rarely be needed unless a
permanent termination is desired.


Config files
------------

memery uses three configuration files.

* `config`. This configuration file is required for memery to run.
* `adminlist`. This configuration file is required for memery to run.
* `userblacklist`. This is entirely optional and hopefully not needed at all.

### config

This is the base configuration file which memery needs to run; memery will
refuse to start without this file. The file is written in JSON and an example
is provided in the repo. Rename `config.example` to just `config` and edit the
values however you wish to get started quickly.

The values in `config` are as explained:

* `irc/nick`: The nick memery will use on the network. If the nick is occupied,
memery will generate a hopefully free new one based on this.
* `irc/channels`: A list of channels memery will join.
* `irc/server`: The server memery will connect to.
* `irc/port`: The port memery will connect to.
* `irc/ssl`: Whether or not memery should connect using SSL.
* `irc/reconnect_delay`: Whenever memery fails connecting to a server, she will
retry over and over. How often she retries is specified by this setting,
in seconds.
* `irc/grace_period`: When memery stops receiving messages from the server for
the number of seconds specified by this setting, she will attempt to contact
the server herself. If she fails to receive anything for an extended period
of time, she will attempt to reconnect to the server.
* `behaviour/command_prefix`: Most commands are executed with something like `!ping`
or `.ping` or `@ping` or perhaps even `command: ping`. This setting dictates
the leading character sequence that will identify a command.
* `plugins/blacklist`: The *plugins* in this list will not be executed by
anyone. Useful when a plugin is considered unnecessary or its usage collides with
another bot.


### adminlist

This file contains regexes of everyone that should be able to reload, kill,
or otherwise violently violate memery at their will. The regexes are standard
python regular expressions, run on the whole name including hostname.
(Eg. name!~nick@host.name.net)

Any empty lines or lines starting with # will be considered whitespace and
ignored.

This file is not cached and changes you make to it will be apparent
immediately.


### userblacklist

Identical to the adminlist file, except the users here will not be able to
interact with memery in any way whatsoever (unless they for some odd reason
would be on the adminlist – that overrides this file).

This file is not cached and changes you make to it will be apparent
immediately.



Licensing
---------

All python code (except plugins, see separate copyright notice in the plugin 
directory) is licensed under the following three-clause BSD license and 
copyrighted to their respective authors:

    Copyright (c) 2012, nycz, kqr
    All rights reserved.

    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions are met:
        * Redistributions of source code must retain the above copyright
          notice, this list of conditions and the following disclaimer.
        * Redistributions in binary form must reproduce the above copyright
          notice, this list of conditions and the following disclaimer in the
          documentation and/or other materials provided with the distribution.
        * The names of the authors must not be used to endorse or promote
          products derived from this software without specific prior written
          permission.

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
    ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
    WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
    DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDERS BE LIABLE FOR ANY
    DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
    (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
    LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
    ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
    (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
    SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


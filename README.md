memery
======

The third incarnation of the infamous ircbot. Not with less ugly pos code!

Written in Python 3, not compatible with Python 2.


Config files
------------

memery uses three configuration files.

* `config`. This is the only configuration file required to run.
* `adminlist`. This is recommended, but not required.
* `userblacklist`. This is entirely optional and hopefully not needed at all.

### config

This is the base configuration file which memery needs to run; memery will
refuse to start without this file. The file is written in JSON and an example
is provided in the repo. Rename `config.example` to just `config` and edit the
values however you wish to get started quickly.

The values in `config` are as explained:

* `nick`: The nick memery will use on the network. Please pick a nick that is
unused. memery will not be able to connect with an occupied nick.
* `channels`: A list of channels memery will join.
* `server`: The server memery will connect to.
* `port`: The port memery will connect to.
* `ssl`: Whether or not memery should connect using SSL.
* `reconnect_delay`: Whenever memery fails connecting to a server, she will
retry over and over. How often she retries is specified by this setting,
in seconds.
* `grace_period`: When memery stops receiving messages from the server for
the number of seconds specified by this setting, she will attempt to contact
the server herself. If she fails to receive anything for an extended period
of time, she will attempt to reconnect to the server.
* `command_prefix`: Most commands are executed with something like `!ping`
or `.ping` or `@ping` or perhaps even `command: ping`. This setting dictates
the leading character sequence that will identify a command.

At the moment, it is unfortunately not possible to reload `config` during
execution. This will probably only be a problem if you wish to change the nick
or command prefix during execution.


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


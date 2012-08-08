memery
======

The third incarnation of the infamous ircbot. Not with less ugly pos code!

Written in Python 3, not compatible with Python 2.


Config files
------------

No config files are in the repo, they have to be created locally. If they do
not exist when memery needs them, empty ones will be created.
(This does not apply to config, memery will crash without it)

All of them will ignore empty lines and lines starting with #.

### config

This file is read only on startup and should contain memery's nick, channel(s),
server and port.
Example:

    nick:memery
    channels:#channel
    server:serv.errr.net
    port:1234

Note the 's' in channelS! It should be there even if only one channels it to be
joined.


### adminlist

This file contains regexes of everyone that should be able to reload, kill,
or otherwise violently violate memery at their will. The regexes are standard
python regular expressions, run on the whole name including hostname.
(Eg. name!~nick@host.name.net)

This file is not cached and changes you make to it will be apparent
immediately.


### userblacklist

Identical to the adminlist file, except the users here will not be able to
interact with memery in any way whatsoever (unless they for some odd reason
would be on the adminlist – that overrides this file).

This file is not cached and changes you make to it will be apparent
immediately.


### o-blacklist

This file should not be edited manually! In fact, if you're lucky you'll never
need it at all! It contains all crappy .o commands that timeout or return
HTTP errors of some sort. Memery will not run any of them.

Each command is on their own line.

This file is not cached and changes you make to it will be apparent
immediately.



Licensing
---------

All python code (except plugins, see separate copyright notice in the plugin 
directory) is licensed under the following three-clause BSD license and 
copyrighted to their respective authors:

    Copyright (c) 2012, nycz
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


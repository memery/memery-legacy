memery-plugins
==============

Plugins for memery!


Structure
---------

Plugins must consist of at least two functions: help() and run().

* help() has no parameters. Help must return a dictionary with the following
    elements: authors, years, version, description and argument.

    * authors must be a list of strings, each string being the name of
        one author of the plugin.
    * years must be a list of strings, each string being a copyright year.
    * version must be a single string with an indication of the version
        of a plugin.
    * description must be a single string which contains a short
        description of what the purpose of the plugin is.
    * argument must be a single string which outlines the expected format
        of the argument to the plugin.

    Example dictionary:

        {'authors':     ['John H. Doe', 'Nick White'],
         'years':       ['2009', '2010', '2011'],
         'version':     '3.4',
         'description': 'Executes a Python expression.',
         'argument':    '<valid python expression>'}
        
* run() has two parameters. The first parameter is the nick of the user who
    executed the command. The second parameter is the argument to the command.
    Both arguments are strings and may be dealt with as the author pleases.
    The function must return a string, the first line of which will be output
    in the channel the command was requested.


Licensing
---------

All plugins are licensed under the following three-clause BSD license
and copyrighted to their respective authors:

    Copyright (c) plugin years, plugin authors
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


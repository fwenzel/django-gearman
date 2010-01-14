django-gearman
==============

*django-gearman* is a convenience wrapper for the [Gearman][Gearman]
[Python Bindings][python-gearman].

With django-gearman, you can code jobs as well as clients in a Django project
with minimal overhead in your application. Server connections etc. all take
place in django-gearman and don't unnecessarily clog your application code.

[Gearman]: http://gearman.org
[python-gearman]: http://github.com/samuel/python-gearman

Usage
-----
Copy/link/weld this app into your django project and add it to the
`INSTALLED_APPS` section of `settings.py`.

Specify the following settings in your local settings.py file:

    # One or more gearman servers
    GEARMAN_SERVERS = ['127.0.0.1']

    # gearman job name pattern. Namespacing etc goes here. This is the pattern
    # jour jobs will register as with the server, and that you'll need to use
    # when calling them from a non-django-gearman client.
    # replacement patterns are:
    # %(app)s : django app name the job is filed under
    # %(job)s : job name
    GEARMAN_JOB_NAME = '%(app)s_%(job)s'

Licensing
---------
This software is licensed under the [Mozilla Tri-License][MPL]:

    ***** BEGIN LICENSE BLOCK *****
    Version: MPL 1.1/GPL 2.0/LGPL 2.1

    The contents of this file are subject to the Mozilla Public License Version
    1.1 (the "License"); you may not use this file except in compliance with
    the License. You may obtain a copy of the License at
    http://www.mozilla.org/MPL/

    Software distributed under the License is distributed on an "AS IS" basis,
    WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
    for the specific language governing rights and limitations under the
    License.

    The Original Code is django-gearman.

    The Initial Developer of the Original Code is Mozilla.
    Portions created by the Initial Developer are Copyright (C) 2010
    the Initial Developer. All Rights Reserved.

    Contributor(s):
      Frederic Wenzel <fwenzel@mozilla.com>

    Alternatively, the contents of this file may be used under the terms of
    either the GNU General Public License Version 2 or later (the "GPL"), or
    the GNU Lesser General Public License Version 2.1 or later (the "LGPL"),
    in which case the provisions of the GPL or the LGPL are applicable instead
    of those above. If you wish to allow use of your version of this file only
    under the terms of either the GPL or the LGPL, and not to allow others to
    use your version of this file under the terms of the MPL, indicate your
    decision by deleting the provisions above and replace them with the notice
    and other provisions required by the GPL or the LGPL. If you do not delete
    the provisions above, a recipient may use your version of this file under
    the terms of any one of the MPL, the GPL or the LGPL.

    ***** END LICENSE BLOCK *****

[MPL]: http://www.mozilla.org/MPL/
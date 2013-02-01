django-gearman
==============

*django-gearman* is a convenience wrapper for the [Gearman][Gearman]
[Python Bindings][python-gearman].

With django-gearman, you can code jobs as well as clients in a Django project
with minimal overhead in your application. Server connections etc. all take
place in django-gearman and don't unnecessarily clog your application code.

[Gearman]: http://gearman.org
[python-gearman]: http://github.com/samuel/python-gearman

Installation
------------
It's the same for both the client and worker instances of your django project:

    pip install -e git://github.com/fwenzel/django-gearman.git#egg=django-gearman

Add ``django_gearman`` to the `INSTALLED_APPS` section of `settings.py`.

Specify the following setting in your local settings.py file:

    # One or more gearman servers
    GEARMAN_SERVERS = ['127.0.0.1']

Workers
-------
### Registering jobs
Create a file `gearman_jobs.py` in any of your django apps, and define as many
jobs as functions as you like. The jobs must accept a single argument as
passed by the caller and must return the result of the operation, if
applicable. (Note: It must accept an argument, even if you don't use it).

Mark each of these functions as gearman jobs by decorating them with
`django_gearman.decorators.gearman_job`.

For an example, look at the `gearman_example` app's `gearman_jobs.py` file.

### Job naming
The tasks are given a default name of their import path, with the phrase
'gearman_jobs' stripped out of them, for readability reasons. You can override
the task name by specifying `name` parameter of the decorator. Here's how:

    @gearman_job(name='my-task-name')
    def my_task_function(foo):
        pass

### Gearman-internal job naming: ``GEARMAN_JOB_NAME``
The setting ``GEARMAN_JOB_NAME`` is a function which takes the original task
name as an argument and returns the gearman-internal version of that task
name. This allows you to map easily usable names in your application to more
complex, unique ones inside gearman.

The default behavior of this method is as follows:

    new_task_name = '%s.%s' % (crc32(getcwd()), task_name)

This way several instances of the same application can be run on the same
server. You may want to change it if you have several, independent instances
of the same application run against a shared gearman server.

If you would like to change this behavior, simply define the
``GEARMAN_JOB_NAME`` function in the ``settings.py``:

    GEARMAN_JOB_NAME = lambda name: name

which would leave the internal task name unchanged.

### Task parameters
The gearman docs specify that the job function can accept only one parameter
(usually refered to as the ``data`` parameter). Additionally, that parameter
may only be a string. Sometimes that may not be enough. What if you would like
to pass an array or a dict? You would need to serialize and deserialize them.
Fortunately, django-gearman can take care of this, so that you can spend
all of your time on coding the actual task.

    @gearman_job(name='my-task-name')
    def my_task_function(foo):
        pass

    client.submit_job('my-task-name', {'foo': 'becomes', 'this': 'dict'})
    client.submit_job('my-task-name', Decimal(1.0))

### Tasks with more than one parameter

You can pass as many arguments as you want, of whatever (serializable) type
you like. Here's an example job definition:

    @gearman_job(name='my-task-name')
    def my_task_function(one, two, three):
        pass

You can execute this function in two different ways:

    client.submit_job('my-task-name', one=1, two=2, three=3)
    client.submit_job('my-task-name', args=[1, 2, 3])

Unfortunately, executing it like this:

    client.submit_job('my-task-name', 1, 2, 3)

would produce the error, because ``submit_job`` from Gearman's Python bindings
contains __a lot__ of arguments and it's much easier to specify them via
keyword names or a special ``args`` keyword than to type something like seven
``None``s instead:

    client.submit_job('my-task-name', None, None, None, None, None, None, None, 1, 2, 3)

The only limitation that you have are gearman reserved keyword parameters. As of
Gearman 2.0.2 these are:

    * data
    * unique
    * priority
    * background
    * wait_until_complete
    * max_retries
    * poll_timeout

So, if you want your job definition to have, for example, ``unique`` or
``background`` keyword parameters, you need to execute the job in a special,
more verbose way. Here's an example of such a job and its execution.

    @gearman_job(name='my-task-name')
    def my_task_function(background, unique):
        pass

    client.submit_job('my-task-name', kwargs={"background": True, "unique": False})
    client.submit_job('my-task-name', args=[True, False])

Finally:

    client.submit_job('my-task-name', background=True, unique=True, kwargs={"background": False, "unique": False})

Don't panic, your task is safe! That's because you're using ``kwargs``
directly. Therefore, Gearman's bindings would receive ``True`` for
``submit_job`` function, while your task would receive ``False``.

Always remember to double-check your parameter names with the reserved words
list.

### Starting a worker
To start a worker, run `python manage.py gearman_worker`. It will start
serving all registered jobs.

To spawn more than one worker (if, e.g., most of your jobs are I/O bound),
use the `-w` option:

    python manage.py gearman_worker -w 5

will start five workers.

Since the process will keep running while waiting for and executing jobs,
you probably want to run this in a _screen_ session or similar.

### Task queues
Queues are a virtual abstraction layer built on top of gearman tasks. An
easy way to describe it is the following example: Imagine you have a task
for fetching e-mails from the server, another task for sending the emails
and one more task for sending SMS via an SMS gateway. A problem you may
encounter is that the email fetching tasks may effectively "block" the worker
(there could be so many of them, it could be so time-consuming, that no other
task would be able to pass through). Of course, one solution would be to add
more workers (via the ``-w`` parameter), but that would only temporarily
solve the problem. This is where queues come in.

The first thing to do is to pass a queue name into the job description, like
this:

    @gearman_job(queue="my-queue-name")
    def some_job(some_arg):
        pass

You may then proceed to starting the worker that is bound to the specific
queue:

    python manage.py gearman_worker -w 5 -q my-queue-name

Be aware of the fact that when you don't specify the queue name, the worker
will take care of all tasks.

Clients
-------
To make your workers work, you need a client app passing data to them. Create
and instance of the `django_gearman.GearmanClient` class and execute a
`django_gearman.Task` with it:

    from django_gearman import GearmanClient, Task
    client = GearmanClient()
    res = client.do_task(Task("gearman_example.reverse", sentence))
    print "Result: '%s'" % res

The notation for the task name is `appname.jobname`, no matter what pattern
you have defined in `GEARMAN_JOB_NAME`.

Dispatching a background event without waiting for the result is easy as well:

    client.dispatch_background_task('gearman_example.background_counting', None)

For a live example look at the `gearman_example` app, in the
`management/commands/gearman_example_client.py` file.

Example App
-----------
For a full, working, example application, add `gearman_example` to your
`INSTALLED_APPS`, then run a worker in one shell:

    python manage.py gearman_worker -w 4

and execute the example app in another:

    python manage.py gearman_example_client

You can see the client sending data and the worker(s) working on it.

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

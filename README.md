![Logo](https://raw.githubusercontent.com/sawyersteven/CherrypyScheduler/master/img/Logo_wide.png)

# CherrypyScheduler
CherrypyScheduler creates a simple interface for creating repeating events on a [Cherrypy](https://github.com/cherrypy/cherrypy) webserver.

### Installation
CherrypyScheduler has been tested on Python 3.4.0 and is not guaranteed to run at all on lower versions.

Install via pip with `pip install CherrypyScheduler`


### Usage
CherrypyScheduler operates as a SimplePlugin in Cherrypy and is easy to integrate.

    import cherrypy
    from cherrypyscheduler import SchedulerPlugin
    
    import datetime
    
    
    class ServerRoot(object):
    
        tasks_completed = 0
    
        @cherrypy.expose
        def index(self):
            return 'Hello World!'
    
    
    SchedulerPlugin(cherrypy.engine).subscribe()

    cherrypy.quickstart(ServerRoot(), '/')

    
At this point the scheduler plugin is running and listening for signals, but doesn't have any tasks to run. Let's give it a job and a way to see what is happening:
    
    import cherrypy
    from cherrypyscheduler import SchedulerPlugin
    
    
    class ServerRoot(object):
    
        tasks_completed = 0
    
        @cherrypy.expose
        def index(self):
            return 'We\'ve executed {} tasks!'.format(self.tasks_completed)
    
    
    def my_scheduled_task():
        ServerRoot.tasks_completed += 1
    
    
    SchedulerPlugin(cherrypy.engine).subscribe()
    
    SchedulerPlugin.ScheduledTask(0, 0, 30, my_scheduled_task)
    
    cherrypy.quickstart(ServerRoot(), '/')

    
This tells the plugin to run `my_scheduled_task`. The start time is `0:00` (midnight) and the task will be called every `30` seconds. The scheduler will call `my_scheduled_task` at the next possible 30 second interval from midnight.

Open `localhost:8080` in your browser and you'll see the counter increase every 30 seconds.

Many more methods are available for interacting with the scheduler and scheduled tasks. See the wiki ## TODO LINK ## for more information.

### How it Works

Tasks are called using a threading.Timer, so the main loop of the Cherrypy server is completely unaffected. Perhaps the largest side-effect of this is that exceptions will cause only the Timer thread to fail, so it is suggested to take advantage of good logging practices to catch anything that might not be working as expected. Timers will restart whether or not the task raises an exception. This allows tasks that rely on external input to fail without preventing future tasks from starting.


### Testing

Tests may be run with `python3 tests/test.py`. Due to the nature of a scheduler, tests make take several minutes to complete as we wait for the scheduler to call the task function. Tests require Cherrypy and Cheroot.

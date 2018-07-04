import os
import sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.getcwd(), '../'))

import unittest                                 # noqa
import cherrypy                                 # noqa
import threading                                # noqa
import time                                     # noqa
from datetime import datetime, timedelta        # noqa
from cherrypyscheduler import SchedulerPlugin   # noqa


class TestScheduler(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.setup_done = False
        cls.task_name = 'Increase Counter'
        cls.task_counter = 0
        cls.now = datetime.now().replace(microsecond=0)
        cls.task_instance = None

    def task(self):
        ''' Task to apply to scheduler
        Increases task_counter by one for every call
        Sets TestScheduler._test_last_execution as datetime obj so we have
            a reference for the actual time in ms later on
        '''
        TestScheduler._test_last_execution = datetime.now()
        TestScheduler.task_counter += 1

    def test_00_create_task(self):
        ''' Tests creation of a simple task and that is is properly
            placed in SchedulerPlugin.task_list

            Set to execute once every 30 seconds
        '''
        TestScheduler.task_instance = SchedulerPlugin.ScheduledTask(self.now.hour, self.now.minute + 1, 30, self.task, auto_start=False, name=self.task_name)
        self.assertIsInstance(SchedulerPlugin.task_list[self.task_name], SchedulerPlugin._SchedulerPlugin__ScheduledTask)

    def test_01_next_execution(self):
        ''' Tests that task.next_execution is set correctly
            for created but not started task, and started task
        '''
        self.assertIsNone(self.task_instance.next_execution)
        self.task_instance.start()
        self.assertEqual(self.task_instance.next_execution, self.now + timedelta(seconds=30))

    def test_02_task_call(self):
        ''' Tests that task is called (30s) '''
        start_count = self.task_counter
        time.sleep(32)
        self.assertEqual(start_count + 1, self.task_counter)

    def test_03_record_json(self):
        ''' Tests that the persistence record is written correctly
            By default this tests both read and write methods of _Record
        '''
        le = SchedulerPlugin.record_handler.read()[self.task_name]['last_execution']
        self.assertEqual(le, self.task_instance.last_execution)

    def test_04_stop(self):
        ''' Tests that the task can be stopped and Thread timer is cancelled (30s)
            Since Timer objects have no properties that indicate remaining time or
            status we will check the task_counter, wait for a timer iteration, and
            make sure it hasn't changed.
        '''
        start_count = self.task_counter
        self.task_instance.stop()
        time.sleep(32)
        self.assertEqual(start_count, self.task_counter)

    def test_05_restart(self):
        ''' Tests restarting scheduler with intial args '''
        a_s = self.task_instance.auto_start
        self.task_instance.restart()
        self.assertEqual(a_s, self.task_instance.auto_start)
        self.assertEqual(self.task_instance.next_execution, None)

    def test_06_reload(self):
        ''' Tests reloading scheduler with 45s delay '''
        now = datetime.now()
        start_count = self.task_counter
        self.task_instance.reload(now.hour, now.minute, 45, True)
        time.sleep(35)
        self.assertEqual(start_count, self.task_counter)
        time.sleep(15)
        self.assertEqual(start_count + 1, self.task_counter)

    def test_07_now(self):
        ''' Test bypassing timer '''
        start_count = self.task_counter
        self.task_instance.now()
        self.assertEqual(start_count + 1, self.task_counter)

    def test_08_creep(self):
        ''' Tests time consistency
            This plugin attempts to only be accurate to +- one second,
            so we will test if repeated task calls creep upward in interval.

            Ignore the first execution time ms since it is called after setting
            up the timer and can be much larger without being a problem.
        '''
        now = datetime.now()
        self.task_instance.reload(now.hour, now.minute, 10, True)
        time.sleep(1)
        ms = []
        for i in range(0, 7):
            time.sleep(10)
            ms.append(round(TestScheduler._test_last_execution.microsecond / 1000000, 2))

        self.assertAlmostEqual(ms[1], ms[-1])

    @classmethod
    def tearDownClass(cls):
        cherrypy.engine.stop()
        cherrypy.engine.exit()
        if os.path.isfile('./test_tasks.json'):
            os.unlink('./test_tasks.json')


class ServerRoot(object):
    @cherrypy.expose
    def index(self):  # pragma: no cover
        return 'Test server running'


if __name__ == '__main__':
    SchedulerPlugin(cherrypy.engine, record_file='./test_tasks.json')

    # Start the CherryPy server
    cherrypy.log.screen = None
    cherrypy.engine.signals.subscribe()
    cherrypy.tree.mount(ServerRoot(), '/')
    cherrypy.config.update('./cp_config.conf')
    cherrypy.engine.start()

    threading.Thread(target=unittest.main, kwargs={'verbosity': 2}).start()
    cherrypy.engine.block()

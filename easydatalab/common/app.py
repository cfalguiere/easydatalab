#-*- coding: utf-8 -*-
"""App commons"""
from __future__ import print_function

import os
import datetime
import traceback
import glob
import logging.config, yaml

from easydatalab.common.exceptions import ExecutionError
from easydatalab.common.exceptions import Error

from easydatalab.common.configuration import AppConfiguration

from easydatalab.monitoring.filemonitor import FileMonitor

class AppContext:
    logger = None
    file_monitor = None

    def __init__(self, name='App', log_config_file=None):
        self.name = name
        self.status = -1
        #self.attributes = {}
        self.configuration = None
        self.steps = []

        self.__init_logging(log_config_file)

        self.logger = logging.getLogger('common.AppContext')
        self.logger.info('creating an instance of class AppContext')

    def __init_logging(self, log_config_file):
        if  log_config_file != None:
          with open(log_config_file) as f:
            log_config = yaml.load(f)
            logging.config.dictConfig( log_config )
            logger = logging.getLogger(self.name)
            logger.info('log configuration loaded from %s' % log_config_file)

    def __str__(self):
        return self.name

    def set_status(self, value ):
        self.status = value

    def get_status(self):
        return self.status

    def set_configuration(self, configuration):
        self.configuration = configuration

    def get_configuration(self):
        return self.configuration

    def skip_steps(self, skipped_step_names):
        print('INFO - will skip %s' % str(skipped_step_names) )
        self.skipped_step_names = skipped_step_names

    def new_step(self, stepName):
        should_skip = stepName in self.skipped_step_names
        step = AppStep(stepName, self, skipped = should_skip)
        self.steps.append(step)
        return step

    def new_configuration(self, cfgPath):
        self.configuration = AppConfiguration(cfgPath, self)
        return self.configuration


    def report(self):
        print( '===========================================================')
        print( '|')
        print( '| REPORT')
        print( '|')
        print( '| Number of steps: %s' % len(self.steps) )
        for step in self.steps:
            print( '| {0}'.format( step.get_report() ) )
        print( '===========================================================')

        if  AppContext.file_monitor:
           AppContext.file_monitor.report()

    def __enter__(self):
        self.start = datetime.datetime.now()
        print( "INFO - Starting app"  )
        file_monitor = FileMonitor()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
       self.end = datetime.datetime.now()
       elapsed = self.end  - self.start
       if exc_type == None:
          self.status = "App Completed"
       else:
          traceback.print_exception(exc_type, exc_value, exc_traceback, 30)
          self.status = "App Aborted"
       self.report()
       print( 'INFO - End of App')


class AppStep:
    def __init__(self, stepName, theAppContext, skipped=False):
        self.stepName = stepName
        self.theAppContext = theAppContext
        self.status = "Not Started"
        self.skipped = skipped
        self.report = None
        self.logger = logging.getLogger('common.AppStep')
        self.logger.info('creating an instance of class AppStep')

    def __enter__(self):
        self.start = datetime.datetime.now()
        print( '| ')
        print( '===========================================================')
        print( "| STEP %s is starting" % self.stepName )
        print( '-----------------------------------------------------------')
        if not self.skipped:
           self.status = "Started"
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
       print( '-----------------------------------------------------------')
       self.end = datetime.datetime.now()
       elapsed = self.end  - self.start
       template = "{0} - {1} in {2}.{3} seconds"
       if exc_type == None:
           if self.skipped:
              self.status = 'Skipped'
              template = "{0} - {1}"
           else:
              self.status = "Completed"
       else:
          print( 'ERROR - in step %s' %  (self.stepName) )
          traceback.print_exception(exc_type, exc_value, exc_traceback, 30)
          self.status = "Aborted"

       self.report = template.format(self.stepName, self.status, elapsed.seconds, elapsed.microseconds)
       print( "| STEP {0}".format(self.report ) )
       print( '===========================================================')
       print( '| ')

       #time.strftime("%H:%M:%S", time.gmtime(elapsed_time))

    def subprocess(self, subprocessClass):
        instance = subprocessClass(self.theAppContext, self)
        return  instance

    def assert_input_file(self, filePath):
        # TODO factorisation validator
        if '*' in filePath:
           # lookup a matching file
           foundMatch = False
           for filepath_object in glob.glob(filePath):
               if os.path.isfile(filepath_object):
                  foundMatch = True
           if not foundMatch:
              msg = 'not file is matching required pattern %s' % filePath
              raise ExecutionError('Input assertion', msg)
        else:
          # lookup the exact name
          if not os.path.exists(filePath):
              msg = 'required file %s not found' % filePath
              raise ExecutionError('Input assertion', msg)

    def get_status(self):
       return self.status

    def get_report(self):
       return self.report

    def enabled(self):
       return not self.skipped

    def __del__(self):
        print("__del__")

    def __repr__(self):
        return self.stepName

    def __str__(self):
        return self.stepName




class SkippedStepException(Error):
    """Exception raised to abort a skipped step.

    Attributes:
        expr -- execution item in which the error occurred
        msg  -- explanation of the error
    """

    def __init__(self, step, msg):
        self.step = step
        self.msg = msg

    def __str__(self):
        return 'error in step {0} - {1}'.format( self.step , self.msg )


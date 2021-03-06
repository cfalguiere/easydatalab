#-*- coding: utf-8 -*-
"""R Utils Tests"""

import unittest
import ConfigParser

from easydatalab.r.rutils import RScript
from easydatalab.common.app import AppContext
from easydatalab.common.exceptions import ExecutionError

class TestRScript(unittest.TestCase):

    def test_call(self):
        cfgFile = 'easydatalab/tests/resources/config/r/config_for_r_unittests.cfg'
        with AppContext() as appContext:
          with appContext.new_configuration(cfgFile) as appConfiguration:
            with appContext.new_step ('echo') as step:
              with step.subprocess(RScript) as r:
                requiredParams = [ 'PERIOD:start' ]
                r.call( 'echo.r',  requiredParams )

    def test_call_wrong_path(self):
        cfgFile = 'easydatalab/tests/resources/config/r/config_for_r_unittests.cfg'
        with AppContext() as appContext:
          with appContext.new_configuration(cfgFile) as appConfiguration:
            with appContext.new_step ('echo') as step:
              with step.subprocess(RScript) as r:
                with self.assertRaises(ExecutionError) as ctx:
                  requiredParams = [ 'x']
                  r.call( 'echo.r',  requiredParams )
                  self.assertTrue('ExecutionError' in ctx.exception)
                  self.assertEqual('ExecutionError: error in step echo - Missing parameter - x', str(ctx.exception))

    def test_call_wrong_rscript_path(self):
        cfgFile = 'easydatalab/tests/resources/config/r/config_for_r_wrong_rscript.cfg'
        with AppContext() as appContext:
          with appContext.new_configuration(cfgFile) as appConfiguration:
            with appContext.new_step ('echo') as step:
              with self.assertRaises(ExecutionError) as ctx:
                with step.subprocess(RScript) as r:
                    requiredParams = [ 'x']
                    r.call( 'echo.r',  requiredParams )
                    self.assertTrue('ExecutionError' in ctx.exception)
                    self.assertEqual('ExecutionError: error in step echo - Rscript  not found at doesnotexist', str(ctx.exception))

    def test_call_wrong_rcode_path(self):
        cfgFile = 'easydatalab/tests/resources/config/r/config_for_r_wrong_rcode.cfg'
        with AppContext() as appContext:
          with appContext.new_configuration(cfgFile) as appConfiguration:
            with appContext.new_step ('echo') as step:
              with self.assertRaises(ExecutionError) as ctx:
                with step.subprocess(RScript) as r:
                    requiredParams = [ 'x']
                    r.call( 'echo.r',  requiredParams )
                    self.assertTrue('ExecutionError' in ctx.exception)
                    self.assertEqual('ExecutionError: error in step echo - Root of R scripts (rcode) not found at doesnotexist', str(ctx.exception))

    def test_get_parameters_as_map(self):
        cfgFile = 'easydatalab/tests/resources/config/r/config_for_r_unittests.cfg'
        with AppContext() as appContext:
          with appContext.new_configuration(cfgFile) as appConfiguration:
            with appContext.new_step ('echo') as step:
              with step.subprocess(RScript) as r:
                requiredParams = [ 'PERIOD:start', 'PERIOD:stop']
                params = r.get_parameters_as_map( requiredParams )
                self.assertEqual( len(params), 3 )
                self.assertEqual( params[0], 'pathToCode=easydatalab/tests/mocks/r/' )
                self.assertEqual( params[1], 'PERIOD:start=201709' )
                self.assertEqual( params[2], 'PERIOD:stop=201801' )


if __name__ == '__main__':
    unittest.main()

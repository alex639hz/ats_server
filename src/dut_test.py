"""Author: Alex Zvuluny | Email: alex.639hz@gmail.com"""

import logging

# from engine.framework import framework
from ats_engine.constants import *
from ats_engine.framework import framework
from ats_engine.procedure_builder import ProcedureBuilder
from ats_engine.types import StepInterface
from ats_engine.utils import Utils
from project.project import Project
from project.instruments.types.instrument_scope import Scope
from project.instruments.serial_instrument import InstrumentSerial

logger = logging.getLogger("[user]")


class DutTest(Project):

    def __init__(self, config):
        super().__init__(config)

        dut_test = self.build_dut_test()
        USE_BASE_PROJECT = False
        if USE_BASE_PROJECT:
            final_procedure = self.project_export(dut_test)
        else:
            final_procedure = dut_test

        final_procedure.start()
        framework.procedure_append(final_procedure)

    def build_dut_test(self):
        dut_flow_build = ProcedureBuilder("dut_test")
        # dut_flow_build.step_call(self.runtime_visa)
        dut_flow_build.step_call(self.runtime_dut_test)
        dut_flow = dut_flow_build.generate_procedure()
        return dut_flow

    def runtime_visa(self, step_interface: StepInterface):
        procedure, args = Utils.extract_step_interface(step_interface)

        instrument = InstrumentSerial(6)
        msg_from_visa = instrument.send_and_read(
            address=1, command=13, params={"param1": 22}
        )
        instrument.close()

        return msg_from_visa

    def runtime_dut_test(self, step_interface: StepInterface):
        procedure, args = Utils.extract_step_interface(step_interface)
        counter = procedure.context.attribute_get("counter", 0)
        counter = counter + 1
        procedure.context.attribute_set("counter", counter)
        msg = f"counter: {counter}"
        sleep_seconds = 3
        max_count = 5

        operation = ["forever", "count"][0]

        if operation == "forever":
            procedure.nextstate_sleep_and_repeat(sleep_seconds)
        elif operation == "count":
            if counter < max_count:
                procedure.nextstate_sleep_and_repeat(sleep_seconds)
            else:
                msg = f"completed: {counter}"
                procedure.nextstate_exit()

        return msg

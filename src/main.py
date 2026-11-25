"""Author: Alex Zvuluny | Email: alex.639hz@gmail.com"""

from dut_test import DutTest
from ats_engine.framework import framework

config = {
    "phase": "A0",
    "phases": ["A0", "A1", "A2"],
}


project = DutTest(config)

try:

    framework.wait_shutdown()

except KeyboardInterrupt:
    framework.call_shutdown(" ----- KeyboardInterrupt ----- ")
except Exception as err:
    msg = f" ----- Main EXCEPTION: Error: {err}"
    print(f"main error: {msg}")

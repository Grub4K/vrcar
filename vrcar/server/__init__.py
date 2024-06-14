from __future__ import annotations

import os

# Workaround for annoying libcamera logs
os.environ["LIBCAMERA_LOG_LEVELS"] = "4"

import concurrent.futures

from vrcar.common import suppress
from vrcar.server import camera, controls


@suppress(KeyboardInterrupt)
def run(address: str, camera_port: int, controls_port: int):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        a = executor.submit(camera.run, (address, camera_port))
        b = executor.submit(controls.run, (address, controls_port))

        concurrent.futures.wait([a, b], return_when=concurrent.futures.FIRST_COMPLETED)

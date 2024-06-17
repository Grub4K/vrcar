from __future__ import annotations

import contextlib
import logging

from vrcar.client.camera import Camera
from vrcar.client.controls import Controls

logger = logging.getLogger(__name__)


def run(address: str, camera_port: int, controls_port: int):
    from vrcar.client.provider.openxr import OpenXRProvider
    from vrcar.client.provider.pygame import PygameProvider

    all_providers = [OpenXRProvider, PygameProvider]

    providers = []
    with contextlib.ExitStack() as stack:
        for provider in all_providers:
            if not provider.available:
                continue

            try:
                result = stack.enter_context(provider())
            except Exception:
                logger.exception(f"Exception while loading {provider.__name__}")
            else:
                providers.append(result)

        if not providers:
            logger.error("No available providers found")
            return

        camera = Camera((address, camera_port), providers)
        controls = Controls((address, controls_port), providers)

        camera.start()
        while controls.update():
            print(
                ", ".join(
                    f"{cmd.name.lower()}={value:5.2f}"
                    for cmd, value in controls.state.items()
                ),
                end="\r",
            )

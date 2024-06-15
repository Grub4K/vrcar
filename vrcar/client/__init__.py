from __future__ import annotations

import os

# Workaround for pygame ad message
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import contextlib
import logging

import pygame
import xr

import vrcar
from vrcar.client.camera import Camera
from vrcar.client.controls import Controls

logger = logging.getLogger(__name__)


def run(address: str, camera_port: int, controls_port: int):
    # 172.20.224.36
    pygame.display.init()
    pygame.joystick.init()
    pygame.display.set_caption("Virtual Car")

    display = pygame.display.set_mode((640, 480))

    camera = Camera(display, (address, camera_port))
    camera.start()

    for index in range(pygame.joystick.get_count()):
        stick = pygame.joystick.Joystick(0)
        stick.init()
        logger.info(f"Setup controller {index}: {stick.get_name()}")

    vr_context = None
    with contextlib.suppress(xr.exception.XrException):
        vr_context = xr.ContextObject(
            instance_create_info=xr.InstanceCreateInfo(
                application_info=xr.ApplicationInfo(
                    application_name="vrcar",
                    application_version=xr.Version(*vrcar.version_tuple),
                ),
                enabled_extension_names=[
                    xr.KHR_OPENGL_ENABLE_EXTENSION_NAME,
                ],
            ),
            # need to use stereo since other modes are not suported in Meta Quest 3
            view_configuration_type=xr.ViewConfigurationType.PRIMARY_STEREO,
        ).__enter__()

        instance_props = xr.get_instance_properties(vr_context.instance)
        runtime_name = instance_props.runtime_name.decode()
        logger.info(f"Using VR runtime: {runtime_name}")

    with contextlib.ExitStack() as stack:
        if vr_context:
            stack.push(vr_context)

        controls = Controls((address, controls_port), vr_context)
        controls.start()

    pygame.quit()

from __future__ import annotations

import importlib.util
import logging
import typing

try:
    import xr
    from OpenGL import GL
except ImportError:
    xr: typing.Any
    GL: typing.Any

import vrcar

if typing.TYPE_CHECKING:
    from vrcar.common import Command

logger = logging.getLogger(__name__)


class OpenXRProvider:
    available = (
        importlib.util.find_spec("xr") is not None
        and importlib.util.find_spec("OpenGL") is not None
    )

    def __init__(self):
        self._context = xr.ContextObject(
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
        )

    def __enter__(self):
        self._context.__enter__()
        self._frame_loop = iter(self._context.frame_loop())

        instance_props = xr.get_instance_properties(self._context.instance)
        runtime_name = instance_props.runtime_name.decode()
        logger.info(f"Using VR runtime: {runtime_name}")

        return self

    def __exit__(self, *args):
        self._context.__exit__(*args)

    def draw(self, buffer: bytes):
        # TODO(Grub4K): Implement replacement of image with camera image
        # maybe decompress higher up in stack?
        pass

    def update(self, state: dict[Command, float]) -> bool:
        frame_data = next(self._frame_loop, None)
        if not frame_data:
            return False

        for view in self._context.view_loop(frame_data):
            GL.glClearColor(0, 0, 1, 1)
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

            self.head_h = view.pose.orientation.y
            self.head_v = view.pose.orientation.x

        return True

    def _get_stuff(self):
        "/user/hand/left/input/thumbstick"
        "/user/hand/right/input/thumbstick"

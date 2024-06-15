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

from vrcar.common import Commands

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
        self._setup_thumbsticks()

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

    def update(self, state: dict[Commands, float]) -> bool:
        frame_data = next(self._frame_loop, None)
        if not frame_data:
            return False

        for view in self._context.view_loop(frame_data):
            GL.glClearColor(0, 0, 1, 1)
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

            state[Commands.HEAD_H] = view.pose.orientation.y
            state[Commands.HEAD_V] = view.pose.orientation.x

        return True

    def _setup_thumbsticks(self):
        instance = self._context.instance
        session = self._context.session

        action_set = xr.create_action_set(
            instance=instance,
            create_info=xr.ActionSetCreateInfo(
                action_set_name="action_set",
                localized_action_set_name="Action Set",
                priority=0,
            ),
        )
        controller_paths = (xr.Path * 2)(
            xr.string_to_path(instance, "/user/hand/left"),
            xr.string_to_path(instance, "/user/hand/right"),
        )
        controller_pose_action = xr.create_action(
            action_set=action_set,
            create_info=xr.ActionCreateInfo(
                action_type=xr.ActionType.VECTOR2F_INPUT,
                action_name="controller_thumbstick",
                localized_action_name="Controller Thumbstick",
                count_subaction_paths=len(controller_paths),
                subaction_paths=controller_paths,
            ),
        )
        suggested_bindings = (xr.ActionSuggestedBinding * 2)(
            xr.ActionSuggestedBinding(
                action=controller_pose_action,
                binding=xr.string_to_path(
                    instance=instance,
                    path_string="/user/hand/left/input/thumbstick",
                ),
            ),
            xr.ActionSuggestedBinding(
                action=controller_pose_action,
                binding=xr.string_to_path(
                    instance=instance,
                    path_string="/user/hand/right/input/thumbstick",
                ),
            ),
        )
        xr.suggest_interaction_profile_bindings(
            instance=instance,
            suggested_bindings=xr.InteractionProfileSuggestedBinding(
                interaction_profile=xr.string_to_path(
                    instance,
                    "/interaction_profiles/khr/simple_controller",
                ),
                count_suggested_bindings=len(suggested_bindings),
                suggested_bindings=suggested_bindings,
            ),
        )
        xr.suggest_interaction_profile_bindings(
            instance=instance,
            suggested_bindings=xr.InteractionProfileSuggestedBinding(
                interaction_profile=xr.string_to_path(
                    instance,
                    "/interaction_profiles/htc/vive_controller",
                ),
                count_suggested_bindings=len(suggested_bindings),
                suggested_bindings=suggested_bindings,
            ),
        )
        xr.attach_session_action_sets(
            session=session,
            attach_info=xr.SessionActionSetsAttachInfo(
                action_sets=[action_set],
            ),
        )

        self._action_spaces = [
            xr.create_action_space(
                session=session,
                create_info=xr.ActionSpaceCreateInfo(
                    action=controller_pose_action,
                    subaction_path=controller_paths[0],
                ),
            ),
            xr.create_action_space(
                session=session,
                create_info=xr.ActionSpaceCreateInfo(
                    action=controller_pose_action,
                    subaction_path=controller_paths[1],
                ),
            ),
        ]

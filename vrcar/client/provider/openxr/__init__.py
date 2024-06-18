from __future__ import annotations

import importlib.resources
import importlib.util
import logging
import threading
import typing

try:
    import xr
    from OpenGL import GL
    from OpenGL.GL import shaders
    from PIL import Image
except ImportError:
    xr: typing.Any
    GL: typing.Any
    Image: typing.Any
    shaders: typing.Any

import vrcar
from vrcar.common import CAM_HEIGHT, CAM_WIDTH, Commands

if typing.TYPE_CHECKING:
    import io

logger = logging.getLogger(__name__)
resources = importlib.resources.files()


class OpenXRProvider:
    available = (
        importlib.util.find_spec("xr") is not None
        and importlib.util.find_spec("OpenGL") is not None
        and importlib.util.find_spec("PIL") is not None
    )

    def __init__(self):
        self._context = xr.ContextObject(
            instance_create_info=xr.InstanceCreateInfo(
                application_info=xr.ApplicationInfo(
                    application_name=vrcar.__name__,
                    application_version=xr.Version(*vrcar.__version_tuple__),
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
        self._new_data = None
        self._new_data_lock = threading.Lock()

        instance_props = xr.get_instance_properties(self._context.instance)
        runtime_name = instance_props.runtime_name.decode()
        logger.info(f"Using VR runtime: {runtime_name}")

        self._texture = GL.glGenTextures(1)

        vertex_shader_data = resources.joinpath("plane.vert").read_text()
        fragment_shader_data = resources.joinpath("plane.frag").read_text()

        try:
            vertex_shader = shaders.compileShader(
                vertex_shader_data, GL.GL_VERTEX_SHADER
            )
            fragment_shader = shaders.compileShader(
                fragment_shader_data, GL.GL_FRAGMENT_SHADER
            )
        except shaders.ShaderCompilationError as e:
            raise ValueError(e.args[0]) from None
        self._shader = shaders.compileProgram(vertex_shader, fragment_shader)

        self._vertices = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self._vertices)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glClearColor(0.2, 0.2, 0.2, 1.0)
        GL.glClearDepth(1.0)

        logger.info("Initialized OpenXR runtime")

        return self

    def __exit__(self, *args):
        self._context.__exit__(*args)

    def draw(self, buffer: io.BytesIO):
        image = Image.open(buffer)
        image = image.resize((CAM_WIDTH, CAM_HEIGHT))
        with self._new_data_lock:
            self._new_data = image.tobytes("raw", "RGB")

    def update_texture(self):
        with self._new_data_lock:
            if not self._new_data:
                return

            data = self._new_data
            self._new_data = None

        GL.glBindTexture(GL.GL_TEXTURE_2D, self._texture)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_NEAREST)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_NEAREST)
        GL.glTexParameteri(
            GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_BORDER
        )
        GL.glTexParameteri(
            GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_BORDER
        )
        GL.glTexParameterfv(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_BORDER_COLOR, (1, 1, 1, 1))

        GL.glTexImage2D(
            GL.GL_TEXTURE_2D,
            0,
            GL.GL_RGBA,
            CAM_WIDTH,
            CAM_HEIGHT,
            0,
            GL.GL_RGB,
            GL.GL_UNSIGNED_BYTE,
            data,
        )

    def update(self, state: dict[Commands, float]) -> bool:
        frame_data = next(self._frame_loop, None)
        if not frame_data:
            return False

        self.update_texture()

        for index, view in enumerate(self._context.view_loop(frame_data)):
            state[Commands.HEAD_H] = view.pose.orientation.y
            state[Commands.HEAD_V] = view.pose.orientation.x

            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
            GL.glUseProgram(self._shader)
            GL.glUniform1f(0, index)
            GL.glBindVertexArray(self._vertices)
            GL.glBindTexture(GL.GL_TEXTURE_2D, self._texture)
            GL.glDrawArrays(GL.GL_TRIANGLES, 0, 6)

        return True

    def wait(self):
        pass

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

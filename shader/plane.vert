#version 430

layout(location = 0) uniform float Index = float(1);
out vec2 texCoord;

const vec2 VERTICES[4] = vec2[4](
  vec2(0.0, 0.0), // 0: low left
  vec2(1.0, 0.0), // 1: low right
  vec2(0.0, 1.0), // 2: up left
  vec2(1.0, 1.0)  // 3: up right
);

const int INDICES[6] = int[6](
  0, 1, 2, // low left
  2, 1, 3  // up right
);

void main() {
  int vertexIndex = INDICES[gl_VertexID];

  vec2 vertex = VERTICES[vertexIndex];
  texCoord = vec2(vertex.x, 1.0 - vertex.y);

  // Scale as -1.0 - 1.0 device
  // HACK: overall offset - eye distance
  float offset = 0.25 - 0.5 * Index;
  vec2 position = (vertex * 2 - 1) / 1.5 + vec2(offset, 0);
  gl_Position = vec4(position, 0, 1);
}

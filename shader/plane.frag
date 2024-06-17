#version 430

uniform sampler2D Texture;

in vec2 texCoord;
out vec4 outColor;

void main() {
  outColor = texture2D(Texture, texCoord);
}

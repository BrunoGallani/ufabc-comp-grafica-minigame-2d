#version 400 core

layout(location = 0) in vec4 vPosition;

uniform vec2 u_escala;
uniform vec2 u_deslocamento;
uniform vec2 u_camera;
uniform vec2 u_meia_tela;
uniform vec4 u_cor;

out vec4 v2fcolor;

void main() {
    vec2 mundo = vPosition.xy * u_escala + u_deslocamento;
    gl_Position = vec4((mundo - u_camera) / u_meia_tela, vPosition.zw);
    v2fcolor = u_cor;
}

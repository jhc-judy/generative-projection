#version 330 core
in vec2 i_position;
in vec2 i_size;
in vec3 i_color;
in float i_angle;
in float i_kind;
uniform vec2 u_view;
out vec2 v_local;
out vec2 v_world;
out vec2 v_size;
out vec3 v_color;
flat out int v_kind;
const vec2 corners[6] = vec2[6](
    vec2(-.5,-.5),vec2(.5,-.5),vec2(-.5,.5),
    vec2(-.5,.5),vec2(.5,-.5),vec2(.5,.5));
void main() {
    vec2 p = corners[gl_VertexID] * i_size;
    float c = cos(i_angle), s = sin(i_angle);
    vec2 world = i_position + mat2(c,s,-s,c)*p;
    v_local = p;
    v_world = world;
    v_size = i_size;
    v_color = i_color;
    v_kind = int(i_kind+.5);
    gl_Position = vec4(world/u_view,0.0,1.0);
}

#version 330 core
in vec2 v_local;
in vec2 v_world;
in vec2 v_size;
in vec3 v_color;
flat in int v_kind;
uniform vec2 u_ball;
uniform float u_radius;
uniform float u_spin;
out vec4 fragColor;
void main() {
    float distance;
    if (v_kind == 1) {
        distance = length(v_local)-v_size.x*.5;
    } else {
        float corner = min(v_size.x, v_size.y) * .18;
        vec2 q = abs(v_local)-v_size*.5+corner;
        distance = length(max(q,0.0))+min(max(q.x,q.y),0.0)-corner;
    }
    float aa = max(fwidth(distance),.0001);
    float alpha = 1.0-smoothstep(-aa,aa,distance);
    if (v_kind == 2) {
        float clipDistance = length(v_world-u_ball)-u_radius;
        alpha *= 1.0-smoothstep(-aa,aa,clipDistance);
    }
    if (alpha < .005) discard;
    vec3 color = v_color;
    if (v_kind == 1) {
        vec2 xy = v_local / (v_size.x*.5);
        vec3 normal = vec3(xy,sqrt(max(0.0,1.0-dot(xy,xy))));
        vec3 light = normalize(vec3(-.55,.7,1.1));
        float diffuse = max(0.0,dot(normal,light));
        float highlight = pow(max(0.0,dot(normal,normalize(light+vec3(0,0,1)))),42.0);
        // A very soft rotating surface variation makes slow rolling visible.
        float skin = 1.0+.035*sin(normal.x*5.0+normal.z*3.0-u_spin);
        color *= (.36+.64*diffuse)*skin;
        color += vec3(.30)*highlight;
    }
    fragColor = vec4(color,alpha);
}

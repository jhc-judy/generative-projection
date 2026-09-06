#version 330 core

in vec2 v_uv;
out vec4 fragColor;

uniform vec2 u_resolution;
uniform float u_time;
uniform float u_speed;
uniform sampler2D u_prev_paint;

const float PI = 3.14159265359;

// Increase toward 1.0 for longer persistence.
// Set to 1.0 if you want effectively no fade at all.
const float PERSISTENCE = 0.9998;


// ============================================================
// Helpers
// ============================================================

float hash11(float p)
{
    return fract(
        sin(p * 127.1)
        * 43758.5453123
    );
}


float dotStamp(
    vec2 p,
    vec2 center,
    float radius
)
{
    vec2 d =
        p - center;

    return exp(
        -2.35
        * dot(d, d)
        / (radius * radius)
    );
}


vec3 hsv2rgb(vec3 c)
{
    vec3 p =
        abs(
            fract(
                c.xxx
                + vec3(
                    0.0,
                    2.0 / 3.0,
                    1.0 / 3.0
                )
            )
            * 6.0
            - 3.0
        );

    vec3 rgb =
        clamp(
            p - 1.0,
            0.0,
            1.0
        );

    rgb =
        rgb
        * rgb
        * (
            3.0
            - 2.0 * rgb
        );

    return c.z * mix(
        vec3(1.0),
        rgb,
        c.y
    );
}


vec3 randomPaintColor(float seed)
{
    float hue =
        hash11(seed * 1.83 + 3.1);

    float saturation =
        mix(
            0.42,
            0.88,
            hash11(seed * 4.37 + 8.0)
        );

    float brightness =
        mix(
            0.78,
            1.00,
            hash11(seed * 7.91 + 15.0)
        );

    return hsv2rgb(
        vec3(
            hue,
            saturation,
            brightness
        )
    );
}


// ============================================================
// Original smooth motion
// ============================================================

vec2 baseFlow(float t)
{
    return vec2(
        0.68 * sin(t * 0.73)
        + 0.24 * sin(t * 1.61 + 1.1),

        0.48 * sin(t * 0.91 + 0.8)
        + 0.22 * sin(t * 1.37 + 2.2)
    );
}


vec2 chaseOffset(float t)
{
    float swirl =
        0.34
        + 0.08 * sin(t * 0.47);

    return vec2(
        cos(t * 1.72),
        sin(t * 1.58 + 0.4)
    ) * swirl;
}


vec2 pinkPosition(float t)
{
    vec2 center =
        baseFlow(t);

    vec2 offset =
        chaseOffset(t);

    float swap =
        sin(t * 0.38);

    vec2 pink =
        center
        + offset
        * (
            0.64
            + 0.18 * swap
        );

    pink += vec2(
        0.08 * sin(t * 3.1),
        0.06 * cos(t * 2.7 + 0.8)
    );

    return pink;
}


vec2 bluePosition(float t)
{
    vec2 center =
        baseFlow(t + 0.55);

    vec2 offset =
        chaseOffset(t + PI * 0.72);

    float swap =
        sin(t * 0.38);

    vec2 blue =
        center
        - offset
        * (
            0.64
            - 0.18 * swap
        );

    blue += vec2(
        0.07 * cos(t * 2.8 + 1.5),
        0.06 * sin(t * 3.3)
    );

    return blue;
}


// ============================================================
// Collision paint deposit
//
// This is REAL persistence now because the marks are written
// into an accumulation texture.
// ============================================================

vec3 paintDeposit(
    vec2 p,
    float t
)
{
    vec2 pinkPos =
        pinkPosition(t);

    vec2 bluePos =
        bluePosition(t);

    float separation =
        length(
            pinkPos - bluePos
        );

    float previousTime =
        t - 0.06;

    float previousSeparation =
        length(
            pinkPosition(previousTime)
            - bluePosition(previousTime)
        );

    float separatingSpeed =
        separation
        - previousSeparation;

    // Only start depositing after closest approach.
    float separatingGate =
        smoothstep(
            0.001,
            0.014,
            separatingSpeed
        );

    float collisionWindow =
        1.0
        - smoothstep(
            0.17,
            0.46,
            separation
        );

    float impactStrength =
        separatingGate
        * collisionWindow;

    if (impactStrength <= 0.001)
    {
        return vec3(0.0);
    }

    vec2 midpoint =
        (pinkPos + bluePos) * 0.5;

    float eventSeed =
        floor(t * 18.0);

    vec3 total =
        vec3(0.0);

    const int DOT_COUNT = 8;

    for (int i = 0; i < DOT_COUNT; i++)
    {
        float fi = float(i);

        float seed =
            eventSeed * 23.17
            + fi * 11.9;

        float angle =
            hash11(seed + 1.0)
            * PI
            * 2.0;

        float spread =
            mix(
                0.020,
                0.200,
                hash11(seed + 2.0)
            );

        vec2 position =
            midpoint
            + vec2(
                cos(angle),
                sin(angle)
            )
            * spread;

        float radius =
            mix(
                0.010,
                0.024,
                hash11(seed + 3.0)
            );

        vec3 color =
            randomPaintColor(seed + 4.0);

        float stamp =
            dotStamp(
                p,
                position,
                radius
            );

        total +=
            color
            * stamp
            * impactStrength
            * 0.24;
    }

    return total;
}


// ============================================================
// Main
// ============================================================

void main()
{
    vec2 uv =
        v_uv;

    vec2 p =
        uv * 2.0 - 1.0;

    p.x *=
        u_resolution.x / u_resolution.y;

    float t =
        u_time * u_speed;

    vec3 previousPaint =
        texture(
            u_prev_paint,
            uv
        ).rgb;

    previousPaint *= PERSISTENCE;

    vec3 newPaint =
        paintDeposit(
            p,
            t
        );

    vec3 color =
        previousPaint + newPaint;

    color =
        min(
            color,
            vec3(1.0)
        );

    fragColor =
        vec4(
            color,
            1.0
        );
}
#version 330 core

in vec2 v_uv;
out vec4 fragColor;

uniform vec2 u_resolution;
uniform float u_time;
uniform float u_speed;
uniform vec3 u_paper_tint;
uniform vec3 u_bg_tint;
uniform sampler2D u_paint_texture;

const float PI = 3.14159265359;


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
        -2.7
        * dot(d, d)
        / (radius * radius)
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


float encounterAmount(
    vec2 pinkPos,
    vec2 bluePos
)
{
    float separation =
        length(
            pinkPos - bluePos
        );

    return (
        1.0
        - smoothstep(
            0.16,
            0.38,
            separation
        )
    );
}


// ============================================================
// Brighter glow balls
//
// Brighter than before,
// and with a SMALL amount of white added back.
// ============================================================

vec3 glowLight(
    vec2 p,
    vec2 center,
    vec3 color,
    float pulse
)
{
    float d =
        length(
            p - center
        );

    float halo =
        exp(
            -9.0
            * d * d
        );

    float glow =
        exp(
            -46.0
            * d * d
        );

    float core =
        exp(
            -250.0
            * d * d
        );

    float hotCore =
        exp(
            -620.0
            * d * d
        );

    vec3 result =
        vec3(0.0);

    result +=
        color
        * halo
        * 0.070
        * pulse;

    result +=
        color
        * glow
        * 0.34
        * pulse;

    result +=
        color
        * core
        * 0.74;

    // Small white lift in the very center only.
    result +=
        mix(
            color,
            vec3(1.0),
            0.25
        )
        * hotCore
        * 0.12;

    return result;
}


// ============================================================
// Original 22-step trace
// ============================================================

vec3 lightTrail(
    vec2 p,
    float t,
    bool isPink
)
{
    vec3 color =
        isPink

        ? vec3(
            1.00,
            0.67,
            0.82
        )

        : vec3(
            0.58,
            0.80,
            1.00
        );

    float total =
        0.0;

    const int TRAIL_STEPS = 22;

    for (int i = 0; i < TRAIL_STEPS; i++)
    {
        float fi =
            float(i);

        float age =
            fi / float(TRAIL_STEPS - 1);

        float sampleTime =
            t - age * 1.15;

        vec2 pos =
            isPink
            ? pinkPosition(sampleTime)
            : bluePosition(sampleTime);

        float d =
            length(
                p - pos
            );

        float thickness =
            mix(
                0.040,
                0.010,
                age
            );

        float trailPoint =
            exp(
                -d * d
                / (
                    thickness
                    * thickness
                )
            );

        float fade =
            pow(
                1.0 - age,
                2.2
            );

        total +=
            trailPoint
            * fade;
    }

    total /=
        float(TRAIL_STEPS);

    return (
        color
        * total
        * 1.7
    );
}


// ============================================================
// Collision spray
//
// Keeps the "only after closest approach" logic,
// so sparks do not collapse inward first.
// ============================================================

vec3 collisionSpray(
    vec2 p,
    vec2 pinkPos,
    vec2 bluePos,
    float t
)
{
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

    float separatingGate =
        smoothstep(
            0.001,
            0.014,
            separatingSpeed
        );

    if (separatingGate <= 0.001)
    {
        return vec3(0.0);
    }

    float collisionWindow =
        1.0
        - smoothstep(
            0.18,
            0.48,
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

    vec2 collisionAxis =
        normalize(
            bluePos - pinkPos
            + vec2(
                0.00001,
                0.0
            )
        );

    vec2 collisionSide =
        vec2(
            -collisionAxis.y,
             collisionAxis.x
        );

    float burstProgress =
        smoothstep(
            0.17,
            0.46,
            separation
        );

    vec3 yellow =
        vec3(
            1.00,
            0.88,
            0.12
        );

    vec3 amber =
        vec3(
            1.00,
            0.68,
            0.06
        );

    vec3 orange =
        vec3(
            1.00,
            0.42,
            0.03
        );

    vec3 total =
        vec3(0.0);

    const int SPARK_COUNT = 18;

    for (int i = 0; i < SPARK_COUNT; i++)
    {
        float fi =
            float(i);

        float seed =
            fi * 11.73 + 4.0;

        float angle =
            hash11(seed + 1.0)
            * PI
            * 2.0;

        vec2 radialDirection =
            vec2(
                cos(angle),
                sin(angle)
            );

        vec2 direction =
            normalize(
                radialDirection
                + collisionSide
                * (
                    hash11(seed + 2.0)
                    - 0.5
                )
                * 0.25
                + collisionAxis
                * (
                    hash11(seed + 3.0)
                    - 0.5
                )
                * 0.15
            );

        float initialDistance =
            mix(
                0.040,
                0.095,
                hash11(seed + 4.0)
            );

        float travelDistance =
            mix(
                0.26,
                0.56,
                hash11(seed + 5.0)
            );

        vec2 particlePosition =
            midpoint
            + direction
            * (
                initialDistance
                + travelDistance
                * burstProgress
            );

        particlePosition +=
            collisionSide
            * sin(
                t
                * (
                    1.2
                    + hash11(seed + 6.0)
                    * 2.5
                )
                + seed
            )
            * 0.008;

        float particleRadius =
            mix(
                0.0045,
                0.0105,
                hash11(seed + 7.0)
            );

        float particle =
            dotStamp(
                p,
                particlePosition,
                particleRadius
            );

        float colorChoice =
            hash11(seed + 8.0);

        vec3 sparkColor;

        if (colorChoice < 0.34)
        {
            sparkColor = yellow;
        }
        else if (colorChoice < 0.67)
        {
            sparkColor = amber;
        }
        else
        {
            sparkColor = orange;
        }

        float twinkle =
            0.74
            + 0.26
            * sin(
                t
                * (
                    7.0
                    + hash11(seed + 9.0)
                    * 6.0
                )
                + seed
            );

        total +=
            sparkColor
            * particle
            * impactStrength
            * twinkle
            * 0.82;
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

    vec3 babyPink =
        vec3(
            1.00,
            0.67,
            0.82
        );

    vec3 babyBlue =
        vec3(
            0.58,
            0.80,
            1.00
        );

    // --------------------------------------------------------
    // Background
    // --------------------------------------------------------

    vec3 color =
        vec3(
            0.014,
            0.018,
            0.032
        );

    float vignette =
        1.0
        - 0.18
        * pow(
            length(uv - 0.5) * 1.45,
            1.8
        );

    color *= vignette;

    // --------------------------------------------------------
    // Persistent pointillist canvas
    // --------------------------------------------------------

    vec3 paint =
        texture(
            u_paint_texture,
            uv
        ).rgb;

    color +=
        paint * 1.15;

    // --------------------------------------------------------
    // Current positions
    // --------------------------------------------------------

    vec2 pinkPos =
        pinkPosition(t);

    vec2 bluePos =
        bluePosition(t);

    float encounter =
        encounterAmount(
            pinkPos,
            bluePos
        );

    // --------------------------------------------------------
    // Original trails
    // --------------------------------------------------------

    color +=
        lightTrail(
            p,
            t,
            true
        );

    color +=
        lightTrail(
            p,
            t,
            false
        );

    // --------------------------------------------------------
    // Balls
    //
    // Brighter overall, but still dim a bit during collision
    // so the spray can read.
    // --------------------------------------------------------

    float proximityDim =
        mix(
            1.0,
            0.72,
            encounter
        );

    float pinkPulse =
        (
            0.92
            + 0.08
            * sin(
                t * 5.1
                + 0.3
            )
        )
        * proximityDim;

    float bluePulse =
        (
            0.92
            + 0.08
            * sin(
                t * 5.4
                + 1.8
            )
        )
        * proximityDim;

    color +=
        glowLight(
            p,
            pinkPos,
            babyPink,
            pinkPulse
        );

    color +=
        glowLight(
            p,
            bluePos,
            babyBlue,
            bluePulse
        );

    // --------------------------------------------------------
    // Collision spray on top
    // --------------------------------------------------------

    color +=
        collisionSpray(
            p,
            pinkPos,
            bluePos,
            t
        );

    // --------------------------------------------------------
    // Gentle compression
    // --------------------------------------------------------

    color =
        color
        / (
            vec3(1.0)
            + color * 0.10
        );

    fragColor =
        vec4(
            color,
            1.0
        );
}
#version 330 core

in vec2 v_uv;
out vec4 fragColor;

uniform vec2 u_resolution;

uniform float u_time;
uniform float u_show_time;
uniform float u_speed;

uniform sampler2D u_paint_texture;

uniform vec4 u_choreo0;
uniform vec4 u_choreo1;
uniform vec4 u_choreo2;
uniform vec4 u_choreo3;
uniform vec4 u_choreo4;
uniform vec4 u_choreo5;
uniform vec4 u_choreo6;
uniform vec4 u_choreo7;


const float PI = 3.14159265359;

const float INTRO_DURATION = 10.0;
const float PAINT_DURATION = 180.0;

const float FINAL_COLLISION_DURATION = 1.2;
const float WHITE_HOLD_DURATION = 0.6;
const float SHRINK_DURATION = 3.0;
const float BLACK_HOLD_DURATION = 1.5;

const float FINALE_START =
    INTRO_DURATION
    + PAINT_DURATION;

const float WHITE_HOLD_START =
    FINALE_START
    + FINAL_COLLISION_DURATION;

const float SHRINK_START =
    WHITE_HOLD_START
    + WHITE_HOLD_DURATION;

const float BLACK_START =
    SHRINK_START
    + SHRINK_DURATION;

const float CONTACT_THRESHOLD = 0.22;


// ============================================================
// Helpers
// ============================================================

float dotStamp(
    vec2 p,
    vec2 center,
    float radius
)
{
    vec2 delta =
        p - center;

    return exp(
        -2.7
        * dot(
            delta,
            delta
        )
        / (
            radius * radius
        )
    );
}


// ============================================================
// Base movement
// ============================================================

vec2 baseFlow(float t)
{
    float x =
        0.68
        * sin(
            t * u_choreo1.x
            + u_choreo0.x
        )

        + 0.24
        * sin(
            t * u_choreo1.y
            + 1.1
            + u_choreo0.y
        );

    float y =
        0.48
        * sin(
            t * u_choreo1.z
            + 0.8
            + u_choreo0.z
        )

        + 0.22
        * sin(
            t * u_choreo1.w
            + 2.2
            + u_choreo0.w
        );

    return vec2(
        x,
        y
    );
}


vec2 chaseOffset(float t)
{
    float swirl =
        0.34
        + 0.08
        * sin(
            t * u_choreo2.x
            + u_choreo2.w
        );

    return (
        vec2(
            cos(
                t * u_choreo2.y
                + u_choreo2.w * 0.47
            ),

            sin(
                t * u_choreo2.z
                + 0.4
                - u_choreo2.w * 0.31
            )
        )
        * swirl
    );
}


// ============================================================
// Wide sweep
// ============================================================

vec2 wideSweep(
    float t,
    float phase
)
{
    return vec2(
        0.18
        * sin(
            t * u_choreo3.y
            + phase
            + u_choreo3.x
        ),

        0.11
        * cos(
            t * u_choreo3.z
            + phase * 1.31
            - u_choreo3.x * 0.43
        )
    );
}


// ============================================================
// Outer excursions
// ============================================================

float excursionGate(
    float t
)
{
    float wave =
        0.5
        + 0.5
        * sin(
            t * u_choreo3.w
            + u_choreo4.x
        );

    float gate =
        smoothstep(
            0.48,
            0.96,
            wave
        );

    return (
        gate
        * gate
        * (
            3.0
            - 2.0 * gate
        )
    );
}


vec2 edgeTarget(
    float t,
    float phase
)
{
    float angle =
        t * u_choreo4.y
        + phase
        + u_choreo4.z
        + 0.42
        * sin(
            t * u_choreo4.w
            + phase * 1.7
        );

    float x =
        1.56
        * cos(angle)
        + 0.12
        * cos(
            angle * 3.0
        );

    float y =
        0.86
        * sin(angle)
        - 0.08
        * sin(
            angle * 3.0
        );

    return vec2(
        x,
        y
    );
}


// ============================================================
// Role A
// ============================================================

vec2 roleAPath(float t)
{
    vec2 center =
        baseFlow(t);

    vec2 offset =
        chaseOffset(t);

    float swap =
        sin(
            t * u_choreo5.x
            + u_choreo5.y
        );

    vec2 position =
        center
        + offset
        * (
            0.64
            + 0.18 * swap
        );

    position.x +=
        0.08
        * sin(
            t * 3.1
            + u_choreo6.x
        );

    position.y +=
        0.06
        * cos(
            t * 2.7
            + 0.8
            + u_choreo6.y
        );

    position +=
        wideSweep(
            t,
            0.25
        );

    float excursion =
        excursionGate(t);

    vec2 target =
        edgeTarget(
            t,
            0.32
        );

    return mix(
        position,
        target,
        excursion * 0.94
    );
}


// ============================================================
// Role B
// ============================================================

vec2 roleBPath(float t)
{
    vec2 center =
        baseFlow(
            t + 0.55
        );

    vec2 offset =
        chaseOffset(
            t
            + PI * 0.72
        );

    float swap =
        sin(
            t * u_choreo5.x
            + u_choreo5.y
        );

    vec2 position =
        center
        - offset
        * (
            0.64
            - 0.18 * swap
        );

    position.x +=
        0.07
        * cos(
            t * 2.8
            + 1.5
            + u_choreo6.z
        );

    position.y +=
        0.06
        * sin(
            t * 3.3
            + u_choreo6.w
        );

    position +=
        wideSweep(
            t,
            2.05
        );

    float excursion =
        excursionGate(
            t
            - u_choreo7.x
        );

    vec2 target =
        edgeTarget(
            t - 0.55,
            0.48
        );

    return mix(
        position,
        target,
        excursion * 0.94
    );
}


// ============================================================
// Both performers can chase
// ============================================================

float roleMix(float t)
{
    float wave =
        0.5
        + 0.5
        * sin(
            t * u_choreo5.z
            + u_choreo5.w
        );

    return smoothstep(
        0.32,
        0.68,
        wave
    );
}


vec2 pinkPosition(float t)
{
    vec2 roleA =
        roleAPath(t);

    vec2 roleB =
        roleBPath(t);

    return mix(
        roleA,
        roleB,
        roleMix(t)
    );
}


vec2 bluePosition(float t)
{
    vec2 roleA =
        roleAPath(t);

    vec2 roleB =
        roleBPath(t);

    return mix(
        roleB,
        roleA,
        roleMix(t)
    );
}


// ============================================================
// Ball glow
// ============================================================

vec3 glowingBall(
    vec2 p,
    vec2 position,
    vec3 baseColor,
    float pulse
)
{
    vec2 delta =
        p - position;

    float d2 =
        dot(
            delta,
            delta
        );

    float halo =
        exp(
            -8.0 * d2
        );

    float glow =
        exp(
            -38.0 * d2
        );

    float core =
        exp(
            -180.0 * d2
        );

    float whiteCore =
        exp(
            -700.0 * d2
        );

    vec3 result =
        vec3(0.0);

    result +=
        baseColor
        * halo
        * 0.10
        * pulse;

    result +=
        baseColor
        * glow
        * 0.55
        * pulse;

    result +=
        baseColor
        * core
        * 0.98;

    result +=
        vec3(1.0)
        * whiteCore
        * 0.17;

    return result;
}


// ============================================================
// Negative space around actors
// ============================================================

float paintClearField(
    vec2 p,
    vec2 center
)
{
    vec2 delta =
        p - center;

    float d2 =
        dot(
            delta,
            delta
        );

    float broad =
        exp(
            -10.0 * d2
        );

    float close =
        exp(
            -42.0 * d2
        );

    return clamp(
        broad * 0.34
        + close * 0.28,
        0.0,
        0.62
    );
}


// ============================================================
// Trails
// ============================================================

float pinkTrailSample(
    vec2 p,
    float t,
    float age
)
{
    float sampleTime =
        t - age * 1.15;

    vec2 position =
        pinkPosition(
            sampleTime
        );

    float d =
        length(
            p - position
        );

    float thickness =
        mix(
            0.040,
            0.010,
            age
        );

    float point =
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

    return (
        point * fade
    );
}


float blueTrailSample(
    vec2 p,
    float t,
    float age
)
{
    float sampleTime =
        t - age * 1.15;

    vec2 position =
        bluePosition(
            sampleTime
        );

    float d =
        length(
            p - position
        );

    float thickness =
        mix(
            0.040,
            0.010,
            age
        );

    float point =
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

    return (
        point * fade
    );
}


// ============================================================
// Pink trail
// ============================================================

vec3 pinkTrail(
    vec2 p,
    float t
)
{
    float total = 0.0;

    total += pinkTrailSample(p, t, 0.000000);
    total += pinkTrailSample(p, t, 0.047619);
    total += pinkTrailSample(p, t, 0.095238);
    total += pinkTrailSample(p, t, 0.142857);
    total += pinkTrailSample(p, t, 0.190476);
    total += pinkTrailSample(p, t, 0.238095);
    total += pinkTrailSample(p, t, 0.285714);
    total += pinkTrailSample(p, t, 0.333333);
    total += pinkTrailSample(p, t, 0.380952);
    total += pinkTrailSample(p, t, 0.428571);
    total += pinkTrailSample(p, t, 0.476190);
    total += pinkTrailSample(p, t, 0.523810);
    total += pinkTrailSample(p, t, 0.571429);
    total += pinkTrailSample(p, t, 0.619048);
    total += pinkTrailSample(p, t, 0.666667);
    total += pinkTrailSample(p, t, 0.714286);
    total += pinkTrailSample(p, t, 0.761905);
    total += pinkTrailSample(p, t, 0.809524);
    total += pinkTrailSample(p, t, 0.857143);
    total += pinkTrailSample(p, t, 0.904762);
    total += pinkTrailSample(p, t, 0.952381);
    total += pinkTrailSample(p, t, 1.000000);

    total /= 22.0;

    return (
        vec3(
            1.00,
            0.67,
            0.82
        )
        * total
        * 1.7
    );
}


// ============================================================
// Blue trail
// ============================================================

vec3 blueTrail(
    vec2 p,
    float t
)
{
    float total = 0.0;

    total += blueTrailSample(p, t, 0.000000);
    total += blueTrailSample(p, t, 0.047619);
    total += blueTrailSample(p, t, 0.095238);
    total += blueTrailSample(p, t, 0.142857);
    total += blueTrailSample(p, t, 0.190476);
    total += blueTrailSample(p, t, 0.238095);
    total += blueTrailSample(p, t, 0.285714);
    total += blueTrailSample(p, t, 0.333333);
    total += blueTrailSample(p, t, 0.380952);
    total += blueTrailSample(p, t, 0.428571);
    total += blueTrailSample(p, t, 0.476190);
    total += blueTrailSample(p, t, 0.523810);
    total += blueTrailSample(p, t, 0.571429);
    total += blueTrailSample(p, t, 0.619048);
    total += blueTrailSample(p, t, 0.666667);
    total += blueTrailSample(p, t, 0.714286);
    total += blueTrailSample(p, t, 0.761905);
    total += blueTrailSample(p, t, 0.809524);
    total += blueTrailSample(p, t, 0.857143);
    total += blueTrailSample(p, t, 0.904762);
    total += blueTrailSample(p, t, 0.952381);
    total += blueTrailSample(p, t, 1.000000);

    total /= 22.0;

    return (
        vec3(
            0.58,
            0.80,
            1.00
        )
        * total
        * 1.7
    );
}


// ============================================================
// Irregular natural spark
// ============================================================

vec3 collisionSpark(
    vec2 p,
    vec2 midpoint,
    float progress,
    float impact,
    float t,

    float angle,
    float initialDistance,
    float travelDistance,
    float headRadius,
    float colorType,
    float flickerFrequency,
    float flickerPhase
)
{
    vec2 direction =
        vec2(
            cos(angle),
            sin(angle)
        );

    float currentDistance =
        initialDistance
        + travelDistance
        * progress;

    vec2 headPosition =
        midpoint
        + direction
        * currentDistance;

    vec3 sparkColor;

    if (colorType < 0.5)
    {
        sparkColor =
            vec3(
                1.00,
                0.92,
                0.12
            );
    }

    else if (colorType < 1.5)
    {
        sparkColor =
            vec3(
                1.00,
                0.68,
                0.04
            );
    }

    else
    {
        sparkColor =
            vec3(
                1.00,
                0.38,
                0.02
            );
    }

    float tailDistance1 =
        max(
            initialDistance,
            currentDistance
            - 0.035
        );

    float tailDistance2 =
        max(
            initialDistance,
            currentDistance
            - 0.070
        );

    vec2 tailPosition1 =
        midpoint
        + direction
        * tailDistance1;

    vec2 tailPosition2 =
        midpoint
        + direction
        * tailDistance2;

    float halo =
        dotStamp(
            p,
            headPosition,
            headRadius * 2.4
        );

    float head =
        dotStamp(
            p,
            headPosition,
            headRadius
        );

    float hotCore =
        dotStamp(
            p,
            headPosition,
            headRadius * 0.42
        );

    float tail1 =
        dotStamp(
            p,
            tailPosition1,
            headRadius * 0.72
        );

    float tail2 =
        dotStamp(
            p,
            tailPosition2,
            headRadius * 0.48
        );

    float twinkle =
        0.84
        + 0.16
        * sin(
            t * flickerFrequency
            + flickerPhase
        );

    vec3 result =
        vec3(0.0);

    result +=
        sparkColor
        * halo
        * 0.32;

    result +=
        sparkColor
        * head
        * 1.35;

    result +=
        mix(
            sparkColor,
            vec3(1.0),
            0.30
        )
        * hotCore
        * 0.52;

    result +=
        sparkColor
        * tail1
        * 0.58;

    result +=
        sparkColor
        * tail2
        * 0.27;

    return (
        result
        * impact
        * twinkle
    );
}


// ============================================================
// Natural collision spray
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
            pinkPos
            - bluePos
        );

    float sep1 =
        length(
            pinkPosition(
                t - 0.04
            )
            - bluePosition(
                t - 0.04
            )
        );

    float sep2 =
        length(
            pinkPosition(
                t - 0.08
            )
            - bluePosition(
                t - 0.08
            )
        );

    float sep3 =
        length(
            pinkPosition(
                t - 0.12
            )
            - bluePosition(
                t - 0.12
            )
        );

    float sep4 =
        length(
            pinkPosition(
                t - 0.16
            )
            - bluePosition(
                t - 0.16
            )
        );

    float sep5 =
        length(
            pinkPosition(
                t - 0.20
            )
            - bluePosition(
                t - 0.20
            )
        );

    float sep6 =
        length(
            pinkPosition(
                t - 0.24
            )
            - bluePosition(
                t - 0.24
            )
        );

    float recentClosest =
        min(
            separation,
            min(
                sep1,
                min(
                    sep2,
                    min(
                        sep3,
                        min(
                            sep4,
                            min(
                                sep5,
                                sep6
                            )
                        )
                    )
                )
            )
        );

    float contactGate =
        1.0
        - step(
            CONTACT_THRESHOLD,
            recentClosest
        );

    float separatingSpeed =
        separation
        - sep1;

    float separatingGate =
        smoothstep(
            0.0004,
            0.008,
            separatingSpeed
        );

    float collisionWindow =
        1.0
        - smoothstep(
            0.22,
            0.60,
            separation
        );

    float impact =
        contactGate
        * separatingGate
        * collisionWindow;

    vec2 midpoint =
        (
            pinkPos
            + bluePos
        ) * 0.5;

    float progress =
        smoothstep(
            0.17,
            0.48,
            separation
        );

    vec3 total =
        vec3(0.0);

    total += collisionSpark(p, midpoint, progress, impact, t, 0.14, 0.054, 0.52, 0.0085, 0.0, 8.3, 0.4);
    total += collisionSpark(p, midpoint, progress, impact, t, 0.48, 0.083, 0.34, 0.0068, 1.0, 10.7, 1.7);
    total += collisionSpark(p, midpoint, progress, impact, t, 0.91, 0.061, 0.63, 0.0112, 2.0, 9.5, 2.4);
    total += collisionSpark(p, midpoint, progress, impact, t, 1.22, 0.101, 0.41, 0.0077, 0.0, 11.2, 3.1);
    total += collisionSpark(p, midpoint, progress, impact, t, 1.68, 0.047, 0.58, 0.0125, 1.0, 7.8, 4.0);
    total += collisionSpark(p, midpoint, progress, impact, t, 2.04, 0.074, 0.46, 0.0094, 2.0, 12.0, 5.1);
    total += collisionSpark(p, midpoint, progress, impact, t, 2.39, 0.095, 0.31, 0.0065, 1.0, 9.1, 6.2);
    total += collisionSpark(p, midpoint, progress, impact, t, 2.73, 0.058, 0.66, 0.0108, 0.0, 10.2, 7.0);
    total += collisionSpark(p, midpoint, progress, impact, t, 3.10, 0.109, 0.38, 0.0081, 2.0, 8.7, 8.4);
    total += collisionSpark(p, midpoint, progress, impact, t, 3.42, 0.069, 0.55, 0.0120, 1.0, 11.6, 9.3);
    total += collisionSpark(p, midpoint, progress, impact, t, 3.83, 0.050, 0.44, 0.0072, 0.0, 7.4, 10.1);
    total += collisionSpark(p, midpoint, progress, impact, t, 4.17, 0.088, 0.62, 0.0099, 2.0, 10.9, 11.7);
    total += collisionSpark(p, midpoint, progress, impact, t, 4.56, 0.064, 0.36, 0.0117, 1.0, 9.7, 12.6);
    total += collisionSpark(p, midpoint, progress, impact, t, 4.93, 0.103, 0.50, 0.0069, 0.0, 12.3, 13.4);
    total += collisionSpark(p, midpoint, progress, impact, t, 5.27, 0.055, 0.67, 0.0103, 2.0, 8.0, 14.8);
    total += collisionSpark(p, midpoint, progress, impact, t, 5.61, 0.079, 0.42, 0.0088, 1.0, 11.0, 15.6);
    total += collisionSpark(p, midpoint, progress, impact, t, 5.89, 0.046, 0.57, 0.0128, 0.0, 9.0, 16.5);
    total += collisionSpark(p, midpoint, progress, impact, t, 6.16, 0.092, 0.33, 0.0075, 2.0, 10.4, 17.9);

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
        uv * 2.0
        - 1.0;

    float aspect =
        u_resolution.x
        / max(
            u_resolution.y,
            1.0
        );

    p.x *= aspect;

    float speed =
        max(
            u_speed,
            0.001
        );

    float showTime =
        u_show_time;

    float motionClock =
        clamp(
            showTime
            - INTRO_DURATION,
            0.0,
            PAINT_DURATION
        )
        * speed;

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

    vec3 color =
        vec3(0.0);


    // ========================================================
    // Entrance + performance
    // ========================================================

    if (
        showTime
        < FINALE_START
    )
    {
        float introProgress =
            clamp(
                showTime
                / INTRO_DURATION,
                0.0,
                1.0
            );

        float introEase =
            introProgress
            * introProgress
            * (
                3.0
                - 2.0 * introProgress
            );

        vec2 activePink =
            pinkPosition(
                motionClock
            );

        vec2 activeBlue =
            bluePosition(
                motionClock
            );

        vec2 pinkOffstage =
            vec2(
                -aspect - 0.35,
                -0.23
            );

        vec2 blueOffstage =
            vec2(
                aspect + 0.35,
                0.23
            );

        vec2 pinkPos =
            mix(
                pinkOffstage,
                activePink,
                introEase
            );

        vec2 bluePos =
            mix(
                blueOffstage,
                activeBlue,
                introEase
            );

        color =
            vec3(
                0.012,
                0.016,
                0.030
            );

        float vignette =
            1.0
            - 0.18
            * pow(
                length(
                    uv - 0.5
                )
                * 1.45,
                1.8
            );

        color *= vignette;

        vec3 paint =
            texture(
                u_paint_texture,
                uv
            ).rgb;

        float clearAmount =
            max(
                paintClearField(
                    p,
                    pinkPos
                ),
                paintClearField(
                    p,
                    bluePos
                )
            );

        color +=
            paint
            * 1.30
            * (
                1.0
                - clearAmount
            );

        if (
            showTime
            >= INTRO_DURATION
        )
        {
            color +=
                pinkTrail(
                    p,
                    motionClock
                );

            color +=
                blueTrail(
                    p,
                    motionClock
                );
        }

        float actorOpacity =
            smoothstep(
                0.08,
                0.80,
                introProgress
            );

        float pinkPulse =
            0.94
            + 0.06
            * sin(
                motionClock * 5.1
                + 0.3
            );

        float bluePulse =
            0.94
            + 0.06
            * sin(
                motionClock * 5.4
                + 1.8
            );

        color +=
            glowingBall(
                p,
                pinkPos,
                babyPink,
                pinkPulse
            )
            * actorOpacity;

        color +=
            glowingBall(
                p,
                bluePos,
                babyBlue,
                bluePulse
            )
            * actorOpacity;

        if (
            showTime
            >= INTRO_DURATION
        )
        {
            color +=
                collisionSpray(
                    p,
                    pinkPos,
                    bluePos,
                    motionClock
                );
        }

        color =
            color
            / (
                vec3(1.0)
                + color * 0.08
            );
    }


    // ========================================================
    // Final collision
    //
    // White begins at the actual collision point and expands
    // outward as one clean circle.
    // ========================================================

    else if (
        showTime
        < WHITE_HOLD_START
    )
    {
        float finalTime =
            PAINT_DURATION
            * speed;

        vec2 pinkStart =
            pinkPosition(
                finalTime
            );

        vec2 blueStart =
            bluePosition(
                finalTime
            );

        vec2 collisionPoint =
            (
                pinkStart
                + blueStart
            ) * 0.5;

        float progress =
            (
                showTime
                - FINALE_START
            )
            / FINAL_COLLISION_DURATION;

        progress =
            clamp(
                progress,
                0.0,
                1.0
            );

        // ----------------------------------------------------
        // The two performers deliberately meet.
        // ----------------------------------------------------

        float approach =
            smoothstep(
                0.0,
                0.62,
                progress
            );

        vec2 pinkPos =
            mix(
                pinkStart,
                collisionPoint,
                approach
            );

        vec2 bluePos =
            mix(
                blueStart,
                collisionPoint,
                approach
            );

        // ----------------------------------------------------
        // Finished painting remains underneath.
        // ----------------------------------------------------

        color =
            vec3(
                0.012,
                0.016,
                0.030
            );

        color +=
            texture(
                u_paint_texture,
                uv
            ).rgb
            * 1.30;

        color +=
            glowingBall(
                p,
                pinkPos,
                babyPink,
                1.0
            );

        color +=
            glowingBall(
                p,
                bluePos,
                babyBlue,
                1.0
            );

        color =
            color
            / (
                vec3(1.0)
                + color * 0.08
            );

        // ----------------------------------------------------
        // Circular whiteout.
        //
        // It starts at contact and expands until it reaches
        // the farthest corner of the display.
        // ----------------------------------------------------

        float whiteProgress =
            smoothstep(
                0.60,
                1.0,
                progress
            );

        vec2 cornerA =
            vec2(
                -aspect,
                -1.0
            );

        vec2 cornerB =
            vec2(
                 aspect,
                -1.0
            );

        vec2 cornerC =
            vec2(
                -aspect,
                 1.0
            );

        vec2 cornerD =
            vec2(
                 aspect,
                 1.0
            );

        float maxRadius =
            max(
                max(
                    length(
                        cornerA
                        - collisionPoint
                    ),
                    length(
                        cornerB
                        - collisionPoint
                    )
                ),
                max(
                    length(
                        cornerC
                        - collisionPoint
                    ),
                    length(
                        cornerD
                        - collisionPoint
                    )
                )
            )
            + 0.10;

        float whiteRadius =
            maxRadius
            * whiteProgress;

        float distanceFromCollision =
            length(
                p
                - collisionPoint
            );

        float whiteCircle =
            1.0
            - smoothstep(
                whiteRadius,
                whiteRadius + 0.045,
                distanceFromCollision
            );

        color =
            mix(
                color,
                vec3(1.0),
                whiteCircle
            );
    }


    // ========================================================
    // Full white
    // ========================================================

    else if (
        showTime
        < SHRINK_START
    )
    {
        color =
            vec3(1.0);
    }


    // ========================================================
    // White contracts toward center
    // ========================================================

    else if (
        showTime
        < BLACK_START
    )
    {
        float progress =
            (
                showTime
                - SHRINK_START
            )
            / SHRINK_DURATION;

        progress =
            clamp(
                progress,
                0.0,
                1.0
            );

        float eased =
            progress
            * progress
            * (
                3.0
                - 2.0 * progress
            );

        float radius =
            mix(
                2.45,
                0.0,
                eased
            );

        float distanceToCenter =
            length(p);

        float whiteField =
            1.0
            - smoothstep(
                radius,
                radius + 0.05,
                distanceToCenter
            );

        color =
            vec3(
                whiteField
            );
    }


    // ========================================================
    // Black reset
    // ========================================================

    else
    {
        color =
            vec3(0.0);
    }


    fragColor =
        vec4(
            color,
            1.0
        );
}
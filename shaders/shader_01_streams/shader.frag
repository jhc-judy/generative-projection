#version 330 core

uniform float u_time;
uniform vec2 u_resolution;
uniform float u_activity;

in vec2 uv;
out vec4 fragColor;

const float PI  = 3.14159265359;
const float TAU = 6.28318530718;


// =========================================================
// Helpers
// =========================================================

float hash(float n)
{
    return fract(
        sin(n) * 43758.5453123
    );
}

float hash2(vec2 p)
{
    return fract(
        sin(
            dot(
                p,
                vec2(127.1, 311.7)
            )
        ) * 43758.5453123
    );
}

float noise(vec2 p)
{
    vec2 i = floor(p);
    vec2 f = fract(p);

    f = f * f * (3.0 - 2.0 * f);

    float a = hash2(i);
    float b = hash2(i + vec2(1.0, 0.0));
    float c = hash2(i + vec2(0.0, 1.0));
    float d = hash2(i + vec2(1.0, 1.0));

    return mix(
        mix(a, b, f.x),
        mix(c, d, f.x),
        f.y
    );
}

vec2 rotate2D(
    vec2 p,
    float angle
)
{
    float c = cos(angle);
    float s = sin(angle);

    return vec2(
        c * p.x - s * p.y,
        s * p.x + c * p.y
    );
}

float sdCircle(
    vec2 p,
    vec2 center,
    float radius
)
{
    return length(p - center) - radius;
}


// =========================================================
// Marble bounce / breathing
// =========================================================

float marblePulse(
    float seed
)
{
    float speed =
        0.72
        + 0.16 * hash(seed * 1.91);

    float phase =
        seed * 2.37;

    float wave =
        sin(
            u_time * speed
            + phase
        );

    // ±6%
    return 1.0
        + wave * 0.06;
}


// =========================================================
// Marble layout
// =========================================================

float obstacleSDF(
    vec2 p,
    float aspect
)
{
    float d = 1000.0;

    d = min(
        d,
        sdCircle(
            p,
            vec2(0.15 * aspect, 0.20),
            0.045 * marblePulse(1.2)
        )
    );

    d = min(
        d,
        sdCircle(
            p,
            vec2(0.82 * aspect, 0.18),
            0.032 * marblePulse(2.6)
        )
    );

    d = min(
        d,
        sdCircle(
            p,
            vec2(0.56 * aspect, 0.42),
            0.085 * marblePulse(3.9)
        )
    );

    d = min(
        d,
        sdCircle(
            p,
            vec2(0.25 * aspect, 0.56),
            0.052 * marblePulse(5.1)
        )
    );

    d = min(
        d,
        sdCircle(
            p,
            vec2(0.90 * aspect, 0.57),
            0.045 * marblePulse(6.7)
        )
    );

    d = min(
        d,
        sdCircle(
            p,
            vec2(0.16 * aspect, 0.80),
            0.060 * marblePulse(8.3)
        )
    );

    d = min(
        d,
        sdCircle(
            p,
            vec2(0.48 * aspect, 0.76),
            0.038 * marblePulse(9.5)
        )
    );

    d = min(
        d,
        sdCircle(
            p,
            vec2(0.84 * aspect, 0.82),
            0.072 * marblePulse(10.8)
        )
    );

    d = min(
        d,
        sdCircle(
            p,
            vec2(0.36 * aspect, 0.29),
            0.036 * marblePulse(12.4)
        )
    );

    d = min(
        d,
        sdCircle(
            p,
            vec2(0.60 * aspect, 0.66),
            0.050 * marblePulse(14.1)
        )
    );

    d = min(
        d,
        sdCircle(
            p,
            vec2(0.075 * aspect, 0.45),
            0.040 * marblePulse(15.7)
        )
    );

    return d;
}

float obstacleSolidMask(
    vec2 p,
    float aspect
)
{
    float sdf =
        obstacleSDF(
            p,
            aspect
        );

    float aa =
        1.5
        / u_resolution.y;

    return 1.0
        - smoothstep(
            0.0,
            aa,
            sdf
        );
}


// =========================================================
// Original mixed stream palette
// =========================================================

int familyIndex(float seed)
{
    if (seed < 0.34)
        return 0;

    if (seed < 0.60)
        return 1;

    if (seed < 0.78)
        return 2;

    if (seed < 0.90)
        return 3;

    return 4;
}

vec3 familyBase(int idx)
{
    if (idx == 0)
        return vec3(
            0.00,
            0.82,
            0.88
        );

    if (idx == 1)
        return vec3(
            0.08,
            0.19,
            0.68
        );

    if (idx == 2)
        return vec3(
            0.82,
            0.10,
            0.44
        );

    if (idx == 3)
        return vec3(
            0.92,
            0.34,
            0.14
        );

    return vec3(
        0.96,
        0.84,
        0.12
    );
}

vec3 familyAccent(int idx)
{
    if (idx == 0)
        return vec3(
            0.18,
            0.98,
            1.00
        );

    if (idx == 1)
        return vec3(
            0.18,
            0.34,
            0.92
        );

    if (idx == 2)
        return vec3(
            0.90,
            0.18,
            0.56
        );

    if (idx == 3)
        return vec3(
            0.98,
            0.46,
            0.18
        );

    return vec3(
        1.00,
        0.90,
        0.22
    );
}


// =========================================================
// Stream motion
// =========================================================

float movingPulse(
    float y,
    float speed,
    float phase
)
{
    float travel =
        y * 7.0
        - u_time
        * (
            0.75
            + speed * 8.0
        )
        + phase;

    float wave =
        0.5
        + 0.5
        * sin(travel);

    float wave2 =
        0.5
        + 0.5
        * sin(
            travel * 0.48
            + phase * 1.7
        );

    float pulse =
        0.60 * wave
        + 0.40 * wave2;

    return smoothstep(
        0.18,
        0.95,
        pulse
    );
}

vec3 flowingThemeColor(
    int idx,
    float y,
    float speed,
    float phase
)
{
    vec3 base =
        familyBase(idx);

    vec3 accent =
        familyAccent(idx);

    float pulse =
        movingPulse(
            y,
            speed,
            phase
        );

    vec3 darkTone =
        base * 0.52;

    vec3 midTone =
        mix(
            base,
            accent,
            0.24
        );

    vec3 brightTone =
        mix(
            base,
            accent,
            0.68
        );

    vec3 tone =
        mix(
            darkTone,
            midTone,
            0.68
        );

    tone =
        mix(
            tone,
            brightTone,
            pulse * 0.92
        );

    return tone;
}

float streamBand(
    vec2 p,
    float center,
    float width,
    float speed,
    float phase
)
{
    float d =
        abs(
            p.x - center
        );

    float band =
        1.0
        - smoothstep(
            width,
            width * 2.4,
            d
        );

    float pulse =
        movingPulse(
            p.y,
            speed,
            phase
        );

    float texture =
        0.84
        + 0.16
        * noise(
            vec2(
                center * 13.0
                + phase,

                p.y * 5.0
                - u_time
                * speed
                * 3.0
            )
        );

    return band
        * texture
        * (
            0.55
            + pulse * 0.45
        );
}


// =========================================================
// Stream splitting around marble
// =========================================================

void splitAroundObstacle(
    vec2 p,
    float baseCenter,
    float width,
    float speed,
    float phase,
    vec2 center,
    vec2 influenceRadius,
    float splitPush,
    float cutStrength,
    float radiusScale,
    inout float ribbon
)
{
    float dxBase =
        baseCenter
        - center.x;

    vec2 scaledInfluence =
        influenceRadius
        * radiusScale;

    float streamAlignment =
        1.0
        - smoothstep(
            scaledInfluence.x * 0.45,
            scaledInfluence.x,
            abs(dxBase)
        );

    float yInfluence =
        exp(
            -pow(
                (
                    p.y
                    - center.y
                )
                / scaledInfluence.y,
                2.0
            )
        );

    float influence =
        streamAlignment
        * yInfluence;

    if (influence < 0.001)
    {
        return;
    }

    float centerBand =
        streamBand(
            p,
            baseCenter,
            width * 0.95,
            speed,
            phase
        );

    float splitAmount =
        splitPush
        * radiusScale
        * influence;

    float leftBand =
        streamBand(
            p,
            baseCenter
            - splitAmount,

            width
            * (
                1.10
                + influence * 0.28
            ),

            speed,
            phase
        );

    float rightBand =
        streamBand(
            p,
            baseCenter
            + splitAmount,

            width
            * (
                1.10
                + influence * 0.28
            ),

            speed,
            phase
        );

    ribbon -=
        centerBand
        * influence
        * cutStrength;

    ribbon +=
        leftBand
        * influence
        * 1.05;

    ribbon +=
        rightBand
        * influence
        * 1.05;
}


// =========================================================
// Classic marble palette
//
// 0 = blue + orange
// 1 = green + yellow
// 2 = orange + white
// 3 = yellow + blue
// 4 = blue + white
// 5 = green + blue
// 6 = orange + yellow
// 7 = white + blue
// =========================================================

void marblePalette(
    int paletteSlot,
    out vec3 colorA,
    out vec3 colorB
)
{
    vec3 ORANGE =
        vec3(
            1.00,
            0.30,
            0.02
        );

    vec3 BLUE =
        vec3(
            0.02,
            0.24,
            0.98
        );

    vec3 YELLOW =
        vec3(
            1.00,
            0.86,
            0.02
        );

    vec3 GREEN =
        vec3(
            0.04,
            0.86,
            0.18
        );

    vec3 WHITE =
        vec3(
            1.00,
            0.995,
            0.97
        );

    if (paletteSlot == 0)
    {
        colorA = BLUE;
        colorB = ORANGE;
    }
    else if (paletteSlot == 1)
    {
        colorA = GREEN;
        colorB = YELLOW;
    }
    else if (paletteSlot == 2)
    {
        colorA = ORANGE;
        colorB = WHITE;
    }
    else if (paletteSlot == 3)
    {
        colorA = YELLOW;
        colorB = BLUE;
    }
    else if (paletteSlot == 4)
    {
        colorA = BLUE;
        colorB = WHITE;
    }
    else if (paletteSlot == 5)
    {
        colorA = GREEN;
        colorB = BLUE;
    }
    else if (paletteSlot == 6)
    {
        colorA = ORANGE;
        colorB = YELLOW;
    }
    else
    {
        colorA = WHITE;
        colorB = BLUE;
    }
}


// =========================================================
// Cane geometry
// =========================================================

float marbleAxisAngle(
    float seed
)
{
    return mix(
        -1.25,
        1.25,
        hash(
            seed * 5.13
        )
    );
}

float caneBulge(
    float axisCoord
)
{
    float x =
        clamp(
            abs(axisCoord),
            0.0,
            1.0
        );

    float center =
        pow(
            max(
                0.0,
                1.0 - x * x
            ),
            0.36
        );

    float pointedEnds =
        1.0
        - smoothstep(
            0.78,
            0.995,
            x
        );

    return center
        * pointedEnds;
}

float sharedCaneCurve(
    float axisCoord,
    float seed
)
{
    float bulge =
        caneBulge(
            axisCoord
        );

    float broadCurve =
        sin(
            axisCoord * PI
            + seed * 0.63
        );

    float softCurve =
        sin(
            axisCoord
            * PI
            * 0.55
            - seed * 0.29
        );

    return bulge
        * (
            broadCurve * 0.105
            + softCurve * 0.045
        );
}

float coloredCaneStrand(
    vec2 qAligned,
    float seed,
    float detailScale,
    float strandPhase,
    float widthScale,
    out float depthValue
)
{
    float axisCoord =
        qAligned.y;

    float bulge =
        caneBulge(
            axisCoord
        );

    float spin =
        u_time
        * (
            0.34
            + 0.08
            * hash(
                seed * 2.11
            )
        )
        + seed * 3.1;

    float twistTurns =
        mix(
            0.22,
            0.38,
            detailScale
        );

    float twistPhase =
        spin
        + axisCoord
        * twistTurns
        * TAU
        + strandPhase;

    float baseCurve =
        sharedCaneCurve(
            axisCoord,
            seed
        );

    float separation =
        bulge
        * mix(
            0.080,
            0.145,
            hash(seed * 4.73)
        );

    float sidewaysOrbit =
        separation
        * sin(twistPhase);

    float depthOrbit =
        separation
        * cos(twistPhase);

    float centerLine =
        baseCurve
        + sidewaysOrbit;

    float tipWidth =
        0.0015;

    float middleWidth =
        mix(
            0.145,
            0.215,
            hash(seed * 3.93)
        );

    float width =
        tipWidth
        + bulge
        * middleWidth
        * widthScale;

    float facing =
        abs(
            cos(twistPhase)
        );

    width *=
        mix(
            0.80,
            1.0,
            facing
        );

    float distanceToStrand =
        abs(
            qAligned.x
            - centerLine
        );

    float mask =
        1.0
        - smoothstep(
            width,
            width + 0.012,
            distanceToStrand
        );

    depthValue =
        depthOrbit;

    return mask;
}


// =========================================================
// Clear glass marble
// =========================================================

vec3 drawMarbleSphere(
    vec3 color,
    vec2 p,
    vec2 center,
    float baseRadius,
    float seed,
    int paletteSlot
)
{
    float pulse =
        marblePulse(seed);

    float radius =
        baseRadius
        * pulse;

    vec2 q =
        (
            p - center
        )
        / radius;

    float r =
        length(q);

    float clip =
        1.0
        - smoothstep(
            0.994,
            1.0,
            r
        );

    if (clip <= 0.0)
    {
        return color;
    }

    float z =
        sqrt(
            max(
                0.0,
                1.0 - r * r
            )
        );

    vec3 glass =
        color;

    float axisAngle =
        marbleAxisAngle(seed);

    vec2 qAligned =
        rotate2D(
            q,
            -axisAngle
        );

    float detailScale =
        clamp(
            (
                baseRadius - 0.032
            )
            / (
                0.085 - 0.032
            ),
            0.0,
            1.0
        );

    vec3 colorA;
    vec3 colorB;

    marblePalette(
        paletteSlot,
        colorA,
        colorB
    );

    float depthA;
    float depthB;

    // larger dominant streak
    float maskA =
        coloredCaneStrand(
            qAligned,
            seed,
            detailScale,
            0.0,
            1.32,
            depthA
        );

    // smaller secondary streak
    float maskB =
        coloredCaneStrand(
            qAligned,
            seed,
            detailScale,
            PI,
            0.60,
            depthB
        );

    float overlap =
        min(
            maskA,
            maskB
        );

    float onlyA =
        maskA
        * (
            1.0 - overlap
        );

    float onlyB =
        maskB
        * (
            1.0 - overlap
        );

    glass =
        mix(
            glass,
            colorA,
            onlyA * 0.93
        );

    glass =
        mix(
            glass,
            colorB,
            onlyB * 0.93
        );

    float depthDifference =
        depthA
        - depthB;

    float aFront =
        smoothstep(
            -0.065,
            0.065,
            depthDifference
        );

    vec3 backColor =
        mix(
            colorA,
            colorB,
            aFront
        );

    vec3 frontColor =
        mix(
            colorB,
            colorA,
            aFront
        );

    glass =
        mix(
            glass,
            backColor,
            overlap * 0.20
        );

    glass =
        mix(
            glass,
            frontColor,
            overlap * 0.88
        );


    // =====================================================
    // Glass edge tint
    // =====================================================

    float edgeTint =
        pow(
            1.0 - z,
            2.3
        );

    glass =
        mix(
            glass,
            vec3(
                0.86,
                0.96,
                1.0
            ),
            edgeTint * 0.085
        );


    // =====================================================
    // Strong top-left highlight
    // =====================================================

    vec2 highlightPoint =
        q
        - vec2(
            -0.28,
            0.31
        );

    highlightPoint.x *=
        1.32;

    highlightPoint.y *=
        0.72;

    float highlight =
        1.0
        - smoothstep(
            0.055,
            0.235,
            length(
                highlightPoint
            )
        );

    glass =
        mix(
            glass,
            vec3(1.0),
            highlight * 0.60
        );


    // =====================================================
    // Secondary soft reflection
    // =====================================================

    vec2 highlightPoint2 =
        q
        - vec2(
            -0.02,
            0.10
        );

    highlightPoint2.x *=
        1.8;

    highlightPoint2.y *=
        0.50;

    float highlight2 =
        1.0
        - smoothstep(
            0.03,
            0.14,
            length(
                highlightPoint2
            )
        );

    glass =
        mix(
            glass,
            vec3(1.0),
            highlight2 * 0.18
        );


    // =====================================================
    // Sharp glint
    // =====================================================

    float glint =
        1.0
        - smoothstep(
            0.010,
            0.050,
            length(
                q
                - vec2(
                    -0.09,
                    0.15
                )
            )
        );

    glass =
        mix(
            glass,
            vec3(1.0),
            glint * 0.88
        );


    // =====================================================
    // Subtle lower-right shading
    // =====================================================

    float lowerRightShade =
        smoothstep(
            0.05,
            0.90,
            q.x
        )
        * smoothstep(
            0.05,
            0.90,
            -q.y
        );

    lowerRightShade *=
        smoothstep(
            0.30,
            1.0,
            r
        );

    glass *=
        1.0
        - lowerRightShade
        * 0.055;


    float bottomShade =
        smoothstep(
            0.15,
            0.95,
            -q.y
        )
        * smoothstep(
            0.72,
            1.0,
            r
        );

    glass *=
        1.0
        - bottomShade
        * 0.035;


    // =====================================================
    // Bright rim
    // =====================================================

    float brightRim =
        smoothstep(
            0.945,
            0.980,
            r
        )
        * (
            1.0
            - smoothstep(
                0.980,
                0.998,
                r
            )
        );

    glass =
        mix(
            glass,
            vec3(
                0.94,
                0.99,
                1.0
            ),
            brightRim * 0.30
        );


    // =====================================================
    // Thin contour
    // =====================================================

    float boundary =
        smoothstep(
            0.988,
            0.999,
            r
        );

    glass =
        mix(
            glass,
            vec3(
                0.20,
                0.27,
                0.29
            ),
            boundary * 0.085
        );


    return mix(
        color,
        glass,
        clip
    );
}


// =========================================================
// Main
// =========================================================

void main()
{
    vec2 p =
        uv;

    float aspect =
        u_resolution.x
        / u_resolution.y;

    p.x *=
        aspect;


    // =====================================================
    // Warm ivory ground
    // =====================================================

    vec3 background =
        vec3(
            0.965,
            0.945,
            0.90
        );


    vec3 outsideColor =
        background;

    vec3 underneathColor =
        background;


    float solidMask =
        obstacleSolidMask(
            p,
            aspect
        );

    float sdf =
        obstacleSDF(
            p,
            aspect
        );


    // =====================================================
    // 18 mixed-color streams + 1 orange stream
    // =====================================================

    const int STREAM_COUNT =
        19;


    for (
        int i = 0;
        i < STREAM_COUNT;
        i++
    )
    {
        float fi =
            float(i);

        float seedA =
            hash(
                fi * 4.31
                + 2.0
            );

        float seedB =
            hash(
                fi * 8.17
                + 1.5
            );

        float seedC =
            hash(
                fi * 6.93
                + 3.7
            );

        float seedD =
            hash(
                fi * 10.19
                + 7.0
            );

        float baseCenter =
            (
                0.04
                + seedA * 0.92
            )
            * aspect;

        float width =
            0.022
            + seedB * 0.025;

        float speed =
            0.018
            + seedC * 0.010
            + u_activity * 0.008;

        float strength =
            0.64
            + seedD * 0.28;

        float phase =
            seedB * 10.0;

        int idx =
            familyIndex(
                seedC
            );


        // =================================================
        // Dedicated orange stream
        // =================================================

        if (
            i == STREAM_COUNT - 1
        )
        {
            baseCenter =
                0.915 * aspect;

            width =
                0.029;

            speed =
                0.022
                + u_activity * 0.006;

            strength =
                0.94;

            phase =
                2.35;

            idx =
                3;
        }


        vec3 streamColor =
            flowingThemeColor(
                idx,
                p.y,
                speed,
                phase
            );


        // =================================================
        // Uninterrupted stream beneath clear marble
        // =================================================

        float underRibbon =
            streamBand(
                p,
                baseCenter,
                width,
                speed,
                phase
            );

        underRibbon *=
            strength;

        underRibbon =
            clamp(
                underRibbon,
                0.0,
                1.0
            );

        underneathColor =
            mix(
                underneathColor,
                streamColor,
                underRibbon * 0.92
            );


        // =================================================
        // Outside stream bends around marbles
        // =================================================

        float ribbon =
            streamBand(
                p,
                baseCenter,
                width,
                speed,
                phase
            );


        splitAroundObstacle(
            p,
            baseCenter,
            width,
            speed,
            phase,
            vec2(
                0.56 * aspect,
                0.42
            ),
            vec2(
                0.24,
                0.26
            ),
            0.135,
            1.05,
            marblePulse(3.9),
            ribbon
        );


        splitAroundObstacle(
            p,
            baseCenter,
            width,
            speed,
            phase,
            vec2(
                0.84 * aspect,
                0.82
            ),
            vec2(
                0.22,
                0.22
            ),
            0.115,
            0.95,
            marblePulse(10.8),
            ribbon
        );


        splitAroundObstacle(
            p,
            baseCenter,
            width,
            speed,
            phase,
            vec2(
                0.25 * aspect,
                0.56
            ),
            vec2(
                0.15,
                0.20
            ),
            0.082,
            0.88,
            marblePulse(5.1),
            ribbon
        );


        splitAroundObstacle(
            p,
            baseCenter,
            width,
            speed,
            phase,
            vec2(
                0.90 * aspect,
                0.57
            ),
            vec2(
                0.15,
                0.19
            ),
            0.090,
            0.94,
            marblePulse(6.7),
            ribbon
        );


        splitAroundObstacle(
            p,
            baseCenter,
            width,
            speed,
            phase,
            vec2(
                0.16 * aspect,
                0.80
            ),
            vec2(
                0.15,
                0.18
            ),
            0.080,
            0.80,
            marblePulse(8.3),
            ribbon
        );


        splitAroundObstacle(
            p,
            baseCenter,
            width,
            speed,
            phase,
            vec2(
                0.48 * aspect,
                0.76
            ),
            vec2(
                0.12,
                0.16
            ),
            0.065,
            0.76,
            marblePulse(9.5),
            ribbon
        );


        splitAroundObstacle(
            p,
            baseCenter,
            width,
            speed,
            phase,
            vec2(
                0.15 * aspect,
                0.20
            ),
            vec2(
                0.12,
                0.14
            ),
            0.060,
            0.70,
            marblePulse(1.2),
            ribbon
        );


        splitAroundObstacle(
            p,
            baseCenter,
            width,
            speed,
            phase,
            vec2(
                0.82 * aspect,
                0.18
            ),
            vec2(
                0.10,
                0.12
            ),
            0.050,
            0.65,
            marblePulse(2.6),
            ribbon
        );


        splitAroundObstacle(
            p,
            baseCenter,
            width,
            speed,
            phase,
            vec2(
                0.36 * aspect,
                0.29
            ),
            vec2(
                0.11,
                0.14
            ),
            0.055,
            0.68,
            marblePulse(12.4),
            ribbon
        );


        splitAroundObstacle(
            p,
            baseCenter,
            width,
            speed,
            phase,
            vec2(
                0.60 * aspect,
                0.66
            ),
            vec2(
                0.15,
                0.18
            ),
            0.078,
            0.82,
            marblePulse(14.1),
            ribbon
        );


        splitAroundObstacle(
            p,
            baseCenter,
            width,
            speed,
            phase,
            vec2(
                0.075 * aspect,
                0.45
            ),
            vec2(
                0.11,
                0.15
            ),
            0.058,
            0.70,
            marblePulse(15.7),
            ribbon
        );


        ribbon *=
            strength;

        ribbon =
            clamp(
                ribbon,
                0.0,
                1.0
            );

        ribbon *=
            (
                1.0
                - solidMask
            );

        outsideColor =
            mix(
                outsideColor,
                streamColor,
                ribbon * 0.86
            );
    }


    // =====================================================
    // Slight concentration around marble boundaries
    // =====================================================

    float edge =
        exp(
            -abs(sdf)
            * 22.0
        );

    edge *=
        (
            1.0
            - solidMask
        );

    outsideColor =
        mix(
            outsideColor,
            outsideColor * 1.15,
            edge * 0.18
        );


    // =====================================================
    // Clear glass reveals uninterrupted streams
    // =====================================================

    vec3 color =
        mix(
            outsideColor,
            underneathColor,
            solidMask
        );


    // =====================================================
    // Marbles
    // =====================================================

    // lower-left
    // orange + yellow
    color =
        drawMarbleSphere(
            color,
            p,
            vec2(
                0.15 * aspect,
                0.20
            ),
            0.045,
            1.2,
            6
        );


    // lower-right
    // blue + orange
    color =
        drawMarbleSphere(
            color,
            p,
            vec2(
                0.82 * aspect,
                0.18
            ),
            0.032,
            2.6,
            0
        );


    // large center
    // green + yellow
    color =
        drawMarbleSphere(
            color,
            p,
            vec2(
                0.56 * aspect,
                0.42
            ),
            0.085,
            3.9,
            1
        );


    // middle-left
    // blue + white
    color =
        drawMarbleSphere(
            color,
            p,
            vec2(
                0.25 * aspect,
                0.56
            ),
            0.052,
            5.1,
            4
        );


    // right / orange stream interaction
    // yellow + blue
    color =
        drawMarbleSphere(
            color,
            p,
            vec2(
                0.90 * aspect,
                0.57
            ),
            0.045,
            6.7,
            3
        );


    // upper-left
    // orange + white
    color =
        drawMarbleSphere(
            color,
            p,
            vec2(
                0.16 * aspect,
                0.80
            ),
            0.060,
            8.3,
            2
        );


    // upper-middle
    // green + blue
    color =
        drawMarbleSphere(
            color,
            p,
            vec2(
                0.48 * aspect,
                0.76
            ),
            0.038,
            9.5,
            5
        );


    // large upper-right
    // orange + yellow
    color =
        drawMarbleSphere(
            color,
            p,
            vec2(
                0.84 * aspect,
                0.82
            ),
            0.072,
            10.8,
            6
        );


    // lower-middle-left
    // white + blue
    color =
        drawMarbleSphere(
            color,
            p,
            vec2(
                0.36 * aspect,
                0.29
            ),
            0.036,
            12.4,
            7
        );


    // upper-middle-right
    // orange + white
    color =
        drawMarbleSphere(
            color,
            p,
            vec2(
                0.60 * aspect,
                0.66
            ),
            0.050,
            14.1,
            2
        );


    // far-left middle
    // green + yellow
    color =
        drawMarbleSphere(
            color,
            p,
            vec2(
                0.075 * aspect,
                0.45
            ),
            0.040,
            15.7,
            1
        );


    fragColor =
        vec4(
            color,
            1.0
        );
}
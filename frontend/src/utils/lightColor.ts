// Colors of the lamps' light, and the sliders' tracks that show them.
// Slider positions are 0-100, colors are [r, g, b] 0-255.

export type RGB = [number, number, number];

// The light's color at a temperature. 0 = warmest (amber), 50 = neutral white, 100 = coolest (blue-white).
// Also used for the temperature slider's track, keep them the same.
export const temperatureStops: [number, RGB][] = [
    [0, [255, 147, 44]],
    [15, [255, 180, 107]],
    [35, [255, 219, 186]],
    [50, [255, 246, 237]],
    [70, [225, 235, 255]],
    [100, [175, 205, 255]]
];

// The color wheel unrolled: full-saturation hues, red -> yellow -> green -> cyan -> blue -> magenta -> red.
// Also used for the color slider's track, so the track shows exactly the color we send.
export const colorStops: [number, RGB][] = [
    [0, [255, 0, 0]],
    [100 / 6, [255, 255, 0]],
    [200 / 6, [0, 255, 0]],
    [300 / 6, [0, 255, 255]],
    [400 / 6, [0, 0, 255]],
    [500 / 6, [255, 0, 255]],
    [100, [255, 0, 0]]
];

// How bright the light looks at a brightness. Our eyes see dim light as brighter
// than it is, so it rises fast at the start and slower at the end.
const brightnessStops: [number, number][] = [
    [0, 0.1],
    [10, 0.35],
    [25, 0.54],
    [50, 0.735],
    [100, 1]
];

// The color at a position (0-100) between the stops
export function getStopColor(stops: [number, RGB][], position: number): RGB {

    for (let i = 1; i < stops.length; i++) {

        const [pos, color] = stops[i]!;
        const [prevPos, prevColor] = stops[i - 1]!;

        if (position <= pos) {

            const t = (position - prevPos) / (pos - prevPos);
            return prevColor.map((value, c) => value + (color[c]! - value) * t) as RGB;
        }
    }

    return stops[stops.length - 1]![1];
}

export function getTemperatureColor(temperature: number): RGB {

    return getStopColor(temperatureStops, temperature);
}

// The color at a position on the color slider, rounded so it can be sent to a lamp
export function getHueColor(position: number): RGB {

    return getStopColor(colorStops, position).map(Math.round) as RGB;
}

// Where a color is on the color slider (0-100), the reverse of getHueColor. Gray/white gives 0.
export function getHuePosition([r, g, b]: RGB): number {

    const max = Math.max(r, g, b);
    const range = max - Math.min(r, g, b);

    if (range == 0)
        return 0;

    let hueDegrees;

    if (max == r)
        hueDegrees = 60 * (((g - b) / range + 6) % 6);
    else if (max == g)
        hueDegrees = 60 * ((b - r) / range + 2);
    else
        hueDegrees = 60 * ((r - g) / range + 4);

    return Math.round(hueDegrees / 360 * 100);
}

// "#rrggbb" (from a color input) to RGB
export function hexToRgb(hex: string): RGB {

    const value = parseInt(hex.slice(1), 16);
    return [(value >> 16) & 255, (value >> 8) & 255, value & 255];
}

// "rgb(r, g, b)" for CSS, rounded
export function toCssColor(color: RGB): string {

    const [r, g, b] = color.map(Math.round);
    return `rgb(${r}, ${g}, ${b})`;
}

// A left-to-right CSS gradient through the stops, for a slider's track
export function toCssGradient(stops: [number, RGB][]): string {

    return `linear-gradient(90deg, ${stops.map(([pos, color]) => `${toCssColor(color)} ${pos}%`).join(", ")})`;
}

export const temperatureGradient = toCssGradient(temperatureStops);
export const colorGradient = toCssGradient(colorStops);

// The temperature's color, from dim to full brightness, for the brightness slider's track
export function getBrightnessGradient(temperature: number): string {

    const color = getTemperatureColor(temperature);

    return toCssGradient(brightnessStops.map(([pos, amount]) => [pos, color.map(value => value * amount) as RGB]));
}

export type RGB = [number, number, number];

// The light's color at a temperature. 0 = warmest (~2200K, amber), 100 = coolest (~6500K, daylight).
// Also used for the temperature slider's track, keep them the same.
export const temperatureStops: [number, RGB][] = [
    [0, [255, 147, 44]],
    [12, [255, 169, 87]],
    [30, [255, 196, 137]],
    [53, [255, 219, 186]],
    [77, [255, 236, 224]],
    [100, [235, 242, 255]]
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

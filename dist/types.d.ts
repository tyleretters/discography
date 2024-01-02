export interface Release {
    title: string;
    project: string;
    released: string;
    type: string;
    format: string;
    role: string;
    label: string;
    tracks: Array<Track>;
    notes: string;
    credits: string;
    release_slug: string;
    project_slug: string;
    id: string;
}
export interface Track {
    number: number;
    title: string;
    length: string;
    track_slug: string;
    id: string;
}

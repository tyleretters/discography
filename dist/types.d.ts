export interface Release {
    title: string;
    project: string;
    released: string;
    type: string;
    format: string;
    role: string;
    label: string;
    mp3: boolean;
    wav: boolean;
    tracks: Array<Track>;
    notes: string;
    credits: string;
    release_slug: string;
    project_slug: string;
    cover_slug: string;
    id: string;
}
export interface Track {
    number: number;
    title: string;
    length: string;
    mp3_slug?: string;
    wav_slug?: string;
    id: string;
}

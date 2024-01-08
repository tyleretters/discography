export interface Release {
  title: string
  project: string
  released: string
  type: string
  format: string
  role: string
  label: string
  mp3: boolean
  mp3_url?: string
  wav: boolean
  wav_url?: string
  tracks: Array<Track>
  streams?: Array<Stream> 
  monospaceNotes?: boolean
  notes: string
  credits: string
  release_slug: string
  project_slug: string
  cover_url: string
  id: string
}

export interface Track {
  number: number
  title: string
  length: string
  mp3_url?: string
  wav_url?: string
  id: string
}

export interface Stream {
  platform: string
  url: string
  id: string
}
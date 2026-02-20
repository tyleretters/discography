export type ReleaseType = 'Mix' | 'LP' | 'EP' | 'Single' | 'OST' | 'Compilation' | 'Triple LP' | 'Demo'
export type ReleaseFormat = 'Digital' | 'CD-R' | 'Vinyl' | 'CD' | 'CD, Digital' | 'Cassette, Digital'
export type ReleaseRole = 'DJ' | 'Artist' | 'Producer' | 'Musician' | 'Band Member' | 'Principal Musician' | 'Operator'

export interface Release {
  title: string
  slug?: string
  project: string
  released: string
  type: ReleaseType
  format: ReleaseFormat
  role: ReleaseRole
  label: string
  mp3: boolean
  mp3_url?: string
  wav: boolean
  wav_url?: string
  tracks: Array<Track>
  trackIds?: string[]
  streams?: Array<Stream>
  monospaceNotes?: boolean
  notes: string
  credits: string
  release_slug: string
  project_slug: string
  runtime: string
  cover_url: string
  id: string
}

export interface Track {
  number: number
  artist?: string
  title: string
  slug?: string
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

import { useQuery } from '@tanstack/react-query'

// Shapes returned by the Flask API in src/api.py.

/** How a play is tinted in tables. */
export type Outcome = 'correct' | 'wrong' | 'spectated'

export interface Play {
  id: number
  /** Local time, ISO 8601. */
  timestamp: string
  mode: string
  annId: number
  difficulty: number | null
  /** Seconds into the song the sample started. */
  startSample: number | null
  /** Seconds. */
  videoLength: number | null
  /** Milliseconds. */
  guessTime: number | null
  answer: string | null
  outcome: Outcome
}

export interface SongPlay extends Play {
  anime: string
  name: string
  artist: string
  type: string
  animeType: string
  vintage: string
}

export interface SongHistory {
  correct: number
  wrong: number
  spectated: number
  /** Most recent first. */
  plays: Play[]
}

export interface SiteLink {
  name: string
  url: string
}

export interface LastSong {
  anime: string
  name: string
  artist: string
  type: string
  difficulty: number | null
  links: SiteLink[]
  history: SongHistory
}

export interface SongDetails {
  name: string
  artist: string
  altAnswers: string[]
  history: SongHistory
}

export interface SongStats {
  name: string
  artist: string
  correct: number
  wrong: number
  spectated: number
  total: number
}

export interface Confusion {
  name: string
  artist: string
  anime: string
  answer: string
  times: number
}

export interface ConfusionRate {
  repeats: number
  chances: number
}

export interface OutcomeCount {
  outcome: 'Correct' | 'Incorrect' | 'Spectated'
  count: number
}

export interface DifficultyGuessTime {
  /** Bin label, e.g. "30-40". */
  difficulty: string
  /** Mean guess time in ms, null when no songs fall in the bin. */
  guessTime: number | null
}

export interface DailyCount {
  /** YYYY-MM-DD */
  date: string
  songs: number
}

export interface MonthlyConfusionRate extends ConfusionRate {
  /** YYYY-MM */
  month: string
  /** Percent. */
  rate: number
}

export interface Dashboard {
  kpis: {
    songsPlayed: number
    songsSpectated: number
    /** Percent. */
    guessRate: number | null
    /** Milliseconds. */
    avgGuessTime: number | null
    repeatConfusion: { allTime: ConfusionRate; last30Days: ConfusionRate }
  }
  outcomes: OutcomeCount[]
  guessTimeByDifficulty: DifficultyGuessTime[]
  songsPerDay: DailyCount[]
  repeatConfusionTrend: MonthlyConfusionRate[]
  topListened: SongStats[]
  topMissed: SongStats[]
  topConfusions: Confusion[]
}

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`/api${path}`)
  if (!response.ok) {
    const body = await response.json().catch(() => null)
    throw new Error(body?.error ?? `${response.status} ${response.statusText}`)
  }
  return response.json()
}

/**
 * Computed once per session, like the Dash app did; the Home page's
 * "Update data" button refetches it.
 */
export const useDashboard = () =>
  useQuery({
    queryKey: ['dashboard'],
    queryFn: () => getJson<Dashboard | null>('/dashboard'),
    staleTime: Infinity,
    gcTime: Infinity,
  })

/** Polled so the page follows the game live. */
export const useLastSong = () =>
  useQuery({
    queryKey: ['last-song'],
    queryFn: () => getJson<LastSong | null>('/last-song'),
    refetchInterval: 500,
  })

export const useAllSongs = () =>
  useQuery({
    queryKey: ['songs'],
    queryFn: () => getJson<SongPlay[]>('/songs'),
    refetchInterval: 30_000,
  })

export const useSongDetails = (name: string, artist: string) =>
  useQuery({
    queryKey: ['song', name, artist],
    queryFn: () => getJson<SongDetails>(`/song?${new URLSearchParams({ name, artist })}`),
    retry: false,
  })

/** Route of the Song Details page for a song. */
export function songDetailsPath({ name, artist }: { name: string; artist: string }) {
  return `/song-details?${new URLSearchParams({ name, artist })}`
}

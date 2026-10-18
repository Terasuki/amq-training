const integer = new Intl.NumberFormat(undefined, { maximumFractionDigits: 0 })

/** 31428 -> "31,428" */
export function formatCount(value: number) {
  return integer.format(value)
}

/** 51.24 -> "51.2 %" */
export function formatPercent(value: number) {
  return `${value.toFixed(1)} %`
}

/** 10229.9 -> "10,230 ms" */
export function formatMs(value: number) {
  return `${integer.format(value)} ms`
}

/** 75.4 -> "1:15" */
export function formatSeconds(seconds: number | null) {
  if (seconds == null || Number.isNaN(seconds)) return '0:00'
  const minutes = Math.floor(seconds / 60)
  return `${minutes}:${String(Math.floor(seconds % 60)).padStart(2, '0')}`
}

/** Where the sample started out of the song's length, e.g. "1:15/2:01". */
export function formatSample(startSample: number | null, videoLength: number | null) {
  return `${formatSeconds(startSample)}/${formatSeconds(videoLength)}`
}

/** "2026-10-17T21:36:01.17" -> "2026/10/17, 21:36" (kept in the recorded local time) */
export function formatTimestamp(timestamp: string) {
  return `${timestamp.slice(0, 10).replaceAll('-', '/')}, ${timestamp.slice(11, 16)}`
}

// Chart dates are plain calendar days, so they're parsed and formatted as UTC
// to keep the browser's time zone from shifting them.

/** "2026-10-17" or "2026-10" -> epoch ms */
export function parseDay(day: string) {
  return Date.parse(day.length === 7 ? `${day}-01` : day)
}

const monthYear = new Intl.DateTimeFormat(undefined, {
  month: 'short',
  year: 'numeric',
  timeZone: 'UTC',
})
const fullDay = new Intl.DateTimeFormat(undefined, {
  weekday: 'short',
  day: 'numeric',
  month: 'short',
  year: 'numeric',
  timeZone: 'UTC',
})

/** epoch ms -> "Oct 2026" */
export function formatMonth(time: number) {
  return monthYear.format(time)
}

/** epoch ms -> "Sat, 17 Oct 2026" */
export function formatDay(time: number) {
  return fullDay.format(time)
}

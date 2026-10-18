import type { Play, SongHistory } from '../api'
import { formatSample, formatTimestamp } from '../format'
import { Card } from './Card'
import { DataTable, type Column } from './DataTable'

/** "correct / wrong / spectated", optionally followed by the total. */
export function HistorySummary({
  correct,
  wrong,
  spectated,
  total,
}: {
  correct: number
  wrong: number
  spectated: number
  total?: number
}) {
  return (
    <span title="Correct / wrong / spectated">
      <span className="text-success-light">{correct}</span>
      {' / '}
      <span className="text-danger-light">{wrong}</span>
      {' / '}
      <span className="text-neutral-light">{spectated}</span>
      {total !== undefined && (
        <>
          {' ('}
          <span className="text-total">{total}</span>)
        </>
      )}
    </span>
  )
}

const PLAY_COLUMNS: Column<Play>[] = [
  { header: 'Date', value: (play) => formatTimestamp(play.timestamp) },
  { header: 'Mode', value: (play) => play.mode },
  { header: 'ANNID', value: (play) => play.annId },
  { header: 'Diff.', value: (play) => play.difficulty },
  { header: 'Sample', value: (play) => formatSample(play.startSample, play.videoLength) },
  { header: 'Guess time', value: (play) => play.guessTime },
  { header: 'Answer', value: (play) => play.answer },
]

/** Every play of a song, tinted by outcome. */
export function HistoryCard({ history }: { history: SongHistory }) {
  return (
    <Card title="History">
      <p className="history-summary">
        <HistorySummary {...history} />
      </p>
      <DataTable
        rows={history.plays}
        columns={PLAY_COLUMNS}
        rowKey={(play) => play.id}
        rowClassName={(play) => `row-${play.outcome}`}
      />
    </Card>
  )
}

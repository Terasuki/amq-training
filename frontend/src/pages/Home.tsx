import { useNavigate } from 'react-router'
import {
  songDetailsPath,
  useDashboard,
  type Confusion,
  type ConfusionRate,
  type Dashboard,
  type SongStats,
} from '../api'
import { Card, ValueCard } from '../components/Card'
import { ConfusionTrendChart, GuessTimeChart, OutcomeChart, SongsPerDayChart } from '../components/charts'
import { DataTable, type Column } from '../components/DataTable'
import { HistorySummary } from '../components/History'
import { Page } from '../components/Layout'
import { LoadStatus } from '../components/Status'
import { formatCount, formatMs, formatPercent } from '../format'

const SONG_STATS_COLUMNS: Column<SongStats>[] = [
  { header: 'Song name', value: (song) => song.name, width: '40%' },
  { header: 'Artist', value: (song) => song.artist, width: '30%' },
  {
    header: 'History',
    value: (song) => song.total,
    render: (song) => <HistorySummary {...song} />,
    width: '30%',
  },
]

const CONFUSION_COLUMNS: Column<Confusion>[] = [
  { header: 'Song name', value: (confusion) => confusion.name, width: '30%' },
  { header: 'Anime', value: (confusion) => confusion.anime, width: '30%' },
  { header: 'Your answer', value: (confusion) => confusion.answer, width: '28%' },
  { header: 'Times', value: (confusion) => confusion.times, width: '12%' },
]

function confusionRate({ repeats, chances }: ConfusionRate) {
  return chances === 0 ? '–' : formatPercent((repeats / chances) * 100)
}

function DashboardView({ dashboard }: { dashboard: Dashboard }) {
  const navigate = useNavigate()
  const openSong = (song: { name: string; artist: string }) => navigate(songDetailsPath(song))
  const { kpis } = dashboard
  const recentConfusions = kpis.repeatConfusion.last30Days

  return (
    <>
      <div className="grid grid-kpi">
        <ValueCard title="Songs played">{formatCount(kpis.songsPlayed)}</ValueCard>
        <ValueCard title="Guess rate">
          {kpis.guessRate == null ? '–' : formatPercent(kpis.guessRate)}
        </ValueCard>
        <ValueCard title="Average guess time">
          {kpis.avgGuessTime == null ? '–' : formatMs(kpis.avgGuessTime)}
        </ValueCard>
        <ValueCard title="Songs spectated">{formatCount(kpis.songsSpectated)}</ValueCard>
        <ValueCard title="Repeat confusions">
          <div>{confusionRate(kpis.repeatConfusion.allTime)}</div>
          <div className="card-subtext">
            Last 30 days: {confusionRate(recentConfusions)}
            {recentConfusions.chances > 0 &&
              ` (${recentConfusions.repeats}/${recentConfusions.chances})`}
          </div>
        </ValueCard>
      </div>

      <div className="grid grid-2">
        <Card title="Outcomes" tint={1} className="chart-card">
          <OutcomeChart outcomes={dashboard.outcomes} />
        </Card>
        <Card
          title="Average guess time by difficulty"
          subtitle="Milliseconds, by song difficulty"
          tint={1}
          className="chart-card"
        >
          <GuessTimeChart data={dashboard.guessTimeByDifficulty} />
        </Card>
      </div>

      <div className="grid">
        <Card
          title="Songs played over time"
          subtitle="Songs played + spectated per day"
          tint={2}
          className="chart-card"
        >
          <SongsPerDayChart data={dashboard.songsPerDay} />
        </Card>
      </div>

      <div className="grid grid-2">
        <Card
          title="Repeat confusions over time"
          subtitle="Same wrong answer repeated, as a share of replays of confused songs"
          tint={2}
          className="chart-card"
        >
          <ConfusionTrendChart data={dashboard.repeatConfusionTrend} />
        </Card>
        <Card title="Top repeat confusions" tint={2}>
          <DataTable
            rows={dashboard.topConfusions}
            columns={CONFUSION_COLUMNS}
            rowKey={(confusion) => `${confusion.name}\n${confusion.artist}\n${confusion.answer}`}
            onRowClick={openSong}
            fixedLayout
          />
        </Card>
      </div>

      <div className="grid grid-2">
        <Card title="Top listened songs" tint={3}>
          <DataTable
            rows={dashboard.topListened}
            columns={SONG_STATS_COLUMNS}
            rowKey={(song) => `${song.name}\n${song.artist}`}
            onRowClick={openSong}
            fixedLayout
          />
        </Card>
        <Card title="Top missed songs" tint={3}>
          <DataTable
            rows={dashboard.topMissed}
            columns={SONG_STATS_COLUMNS}
            rowKey={(song) => `${song.name}\n${song.artist}`}
            onRowClick={openSong}
            fixedLayout
          />
        </Card>
      </div>
    </>
  )
}

export default function Home() {
  const { data: dashboard, error, isFetching, refetch } = useDashboard()

  return (
    <Page title="Home" fluid>
      <div className="toolbar">
        <button type="button" className="btn btn-primary" onClick={() => refetch()} disabled={isFetching}>
          {isFetching && <span className="spinner spinner--inline" aria-hidden />}
          Update data
        </button>
      </div>
      {dashboard === undefined ? (
        <LoadStatus error={error} />
      ) : dashboard === null ? (
        <p className="notice">No songs recorded yet.</p>
      ) : (
        <>
          {error && <p className="notice">Couldn't update data: {error.message}</p>}
          <div className={isFetching ? 'is-refreshing' : undefined} aria-busy={isFetching}>
            <DashboardView dashboard={dashboard} />
          </div>
        </>
      )}
    </Page>
  )
}

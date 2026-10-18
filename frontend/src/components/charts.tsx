import { useMemo, type ReactNode } from 'react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  type TooltipContentProps,
} from 'recharts'
import type { DailyCount, DifficultyGuessTime, MonthlyConfusionRate, OutcomeCount } from '../api'
import {
  formatCount,
  formatDay,
  formatMonth,
  formatMs,
  formatPercent,
  parseDay,
} from '../format'

// Chart colors are the tokens in theme.css.
const SERIES = 'var(--chart-series)'
const OUTCOME_COLORS: Record<OutcomeCount['outcome'], string> = {
  Correct: 'var(--success-chart)',
  Incorrect: 'var(--danger-chart)',
  Spectated: 'var(--neutral-chart)',
}

const AXIS = {
  stroke: 'var(--chart-axis)',
  tick: { fill: 'var(--text-secondary)' },
  tickLine: false,
}
const LINE_CURSOR = { stroke: 'var(--ink-soft)', strokeWidth: 1 }
const MARGIN = { top: 8, right: 16, bottom: 0, left: 0 }

/** Fills the card's remaining height, at least 360px. */
function ChartFrame({ children }: { children: ReactNode }) {
  return (
    <div className="chart">
      <div className="chart-inner">
        <ResponsiveContainer width="100%" height="100%">
          {children}
        </ResponsiveContainer>
      </div>
    </div>
  )
}

/** Tooltip content for the hovered data point, as `render` lays it out. */
function tooltip<T>(render: (row: T) => ReactNode) {
  return ({ active, payload }: TooltipContentProps) =>
    active && payload?.length ? (
      <div className="chart-tooltip">{render(payload[0].payload as T)}</div>
    ) : null
}

/** First-of-month ticks from `start` to `end`, thinned out to at most `max`. */
function monthTicks(start: number, end: number, max = 8) {
  const first = new Date(start)
  const ticks: number[] = []
  // Date.UTC rolls months past December over into the next year.
  for (let month = first.getUTCMonth() + (first.getUTCDate() > 1 ? 1 : 0); ; month++) {
    const tick = Date.UTC(first.getUTCFullYear(), month, 1)
    if (tick > end) break
    ticks.push(tick)
  }
  const step = Math.ceil(ticks.length / max)
  return ticks.filter((_, i) => i % step === 0)
}

/** Time axis over the data's `time` field, labelled by month. */
function timeAxisProps(data: { time: number }[]) {
  const start = data[0]?.time ?? 0
  const end = data.at(-1)?.time ?? 0
  return {
    ...AXIS,
    dataKey: 'time',
    type: 'number' as const,
    scale: 'time' as const,
    domain: [start, end],
    ticks: monthTicks(start, end),
    tickFormatter: formatMonth,
    padding: { left: 12, right: 12 },
  }
}

export function OutcomeChart({ outcomes }: { outcomes: OutcomeCount[] }) {
  const total = outcomes.reduce((sum, { count }) => sum + count, 0)
  const share = (count: number) => formatPercent(total ? (count / total) * 100 : 0)

  return (
    <>
      <ChartFrame>
        <PieChart>
          <Pie
            data={outcomes}
            dataKey="count"
            nameKey="outcome"
            innerRadius="55%"
            outerRadius="90%"
            paddingAngle={1}
            cornerRadius={4}
            stroke="none"
          >
            {outcomes.map(({ outcome }) => (
              <Cell key={outcome} fill={OUTCOME_COLORS[outcome]} />
            ))}
          </Pie>
          <Tooltip
            content={tooltip<OutcomeCount>(({ outcome, count }) => (
              <>
                <div>{outcome}</div>
                <div className="chart-tooltip-value">{share(count)}</div>
                <div className="chart-tooltip-detail">{formatCount(count)} songs</div>
              </>
            ))}
          />
        </PieChart>
      </ChartFrame>
      <ul className="chart-legend">
        {outcomes.map(({ outcome, count }) => (
          <li key={outcome}>
            <span className="chart-legend-swatch" style={{ background: OUTCOME_COLORS[outcome] }} />
            {outcome}
            <span className="chart-legend-detail">
              {share(count)} ({formatCount(count)})
            </span>
          </li>
        ))}
      </ul>
    </>
  )
}

export function GuessTimeChart({ data }: { data: DifficultyGuessTime[] }) {
  return (
    <ChartFrame>
      <BarChart data={data} margin={MARGIN}>
        <CartesianGrid vertical={false} stroke="var(--chart-grid)" />
        <XAxis {...AXIS} dataKey="difficulty" />
        <YAxis {...AXIS} tickFormatter={formatCount} width={56} />
        <Tooltip
          cursor={{ fill: 'var(--chart-grid)' }}
          content={tooltip<DifficultyGuessTime>(({ difficulty, guessTime }) => (
            <>
              <div>Difficulty {difficulty}</div>
              <div className="chart-tooltip-value">
                {guessTime == null ? 'No songs' : formatMs(guessTime)}
              </div>
            </>
          ))}
        />
        <Bar dataKey="guessTime" fill={SERIES} maxBarSize={24} radius={[4, 4, 0, 0]} />
      </BarChart>
    </ChartFrame>
  )
}

export function SongsPerDayChart({ data }: { data: DailyCount[] }) {
  const points = useMemo(() => data.map((day) => ({ ...day, time: parseDay(day.date) })), [data])

  return (
    <ChartFrame>
      <LineChart data={points} margin={MARGIN}>
        <CartesianGrid vertical={false} stroke="var(--chart-grid)" />
        <XAxis {...timeAxisProps(points)} />
        <YAxis {...AXIS} allowDecimals={false} width={40} />
        <Tooltip
          cursor={LINE_CURSOR}
          content={tooltip<(typeof points)[number]>(({ time, songs }) => (
            <>
              <div>{formatDay(time)}</div>
              <div className="chart-tooltip-value">{formatCount(songs)} songs</div>
            </>
          ))}
        />
        <Line
          dataKey="songs"
          type="linear"
          stroke={SERIES}
          strokeWidth={2}
          dot={false}
          activeDot={{ r: 4, strokeWidth: 0 }}
        />
      </LineChart>
    </ChartFrame>
  )
}

export function ConfusionTrendChart({ data }: { data: MonthlyConfusionRate[] }) {
  const points = useMemo(() => data.map((month) => ({ ...month, time: parseDay(month.month) })), [data])

  return (
    <ChartFrame>
      <LineChart data={points} margin={MARGIN}>
        <CartesianGrid vertical={false} stroke="var(--chart-grid)" />
        <XAxis {...timeAxisProps(points)} />
        <YAxis {...AXIS} domain={[0, 'auto']} tickFormatter={(rate) => `${rate} %`} width={48} />
        <Tooltip
          cursor={LINE_CURSOR}
          content={tooltip<(typeof points)[number]>(({ time, rate, repeats, chances }) => (
            <>
              <div>{formatMonth(time)}</div>
              <div className="chart-tooltip-value">{formatPercent(rate)}</div>
              <div className="chart-tooltip-detail">
                {formatCount(repeats)} of {formatCount(chances)} replays of confused songs
              </div>
            </>
          ))}
        />
        <Line
          dataKey="rate"
          type="linear"
          stroke={SERIES}
          strokeWidth={2}
          dot={{ r: 4, fill: SERIES, strokeWidth: 0 }}
          activeDot={{ r: 5, strokeWidth: 0 }}
        />
      </LineChart>
    </ChartFrame>
  )
}

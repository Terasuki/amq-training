import { useNavigate } from 'react-router'
import { songDetailsPath, useAllSongs, type SongPlay } from '../api'
import { DataTable, type Column } from '../components/DataTable'
import { Page } from '../components/Layout'
import { LoadStatus } from '../components/Status'
import { formatSample, formatTimestamp } from '../format'

const COLUMNS: Column<SongPlay>[] = [
  { header: 'Date', value: (play) => formatTimestamp(play.timestamp) },
  { header: 'Mode', value: (play) => play.mode },
  { header: 'Anime', value: (play) => play.anime },
  { header: 'Song name', value: (play) => play.name },
  { header: 'Artist', value: (play) => play.artist },
  { header: 'Type', value: (play) => play.type },
  { header: 'Anime Type', value: (play) => play.animeType },
  { header: 'Vintage', value: (play) => play.vintage },
  { header: 'Diff.', value: (play) => play.difficulty },
  { header: 'Answer', value: (play) => play.answer },
  { header: 'Guess time', value: (play) => play.guessTime },
  { header: 'ANNID', value: (play) => play.annId },
  { header: 'Sample', value: (play) => formatSample(play.startSample, play.videoLength) },
]

export default function AllSongs() {
  const { data: songs, error } = useAllSongs()
  const navigate = useNavigate()

  return (
    <Page fluid>
      {songs === undefined ? (
        <LoadStatus error={error} />
      ) : (
        <DataTable
          rows={songs}
          columns={COLUMNS}
          rowKey={(play) => play.id}
          rowClassName={(play) => `row-${play.outcome}`}
          onRowClick={(play) => navigate(songDetailsPath(play))}
          interactive
          pageSize={50}
          rowNoun="plays"
        />
      )}
    </Page>
  )
}

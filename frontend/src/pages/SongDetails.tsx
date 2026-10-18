import { useSearchParams } from 'react-router'
import { useSongDetails } from '../api'
import { ValueCard } from '../components/Card'
import { HistoryCard } from '../components/History'
import { Page } from '../components/Layout'
import { LoadStatus } from '../components/Status'

function SongDetailsView({ name, artist }: { name: string; artist: string }) {
  const { data: song, error } = useSongDetails(name, artist)
  if (!song) return <LoadStatus error={error} />

  return (
    <>
      <div className="grid grid-md-2">
        <div className="stack">
          <ValueCard title="Song">
            <p>{song.name}</p>
          </ValueCard>
          <ValueCard title="Artist">
            <p>{song.artist}</p>
          </ValueCard>
        </div>
        <ValueCard title="Possible answers">
          <div className="answer-list">
            {song.altAnswers.map((answer) => (
              <p key={answer}>{answer}</p>
            ))}
          </div>
        </ValueCard>
      </div>
      <HistoryCard history={song.history} />
    </>
  )
}

/** A song picked from one of the tables, given by ?name=…&artist=… */
export default function SongDetails() {
  const [params] = useSearchParams()
  const name = params.get('name')
  const artist = params.get('artist')

  return (
    <Page title="Selected Song">
      {name === null || artist === null ? (
        <p className="notice">Pick a song from a table on the Home or All Songs page.</p>
      ) : (
        <SongDetailsView name={name} artist={artist} />
      )}
    </Page>
  )
}

import { useLastSong } from '../api'
import { ValueCard } from '../components/Card'
import { HistoryCard } from '../components/History'
import { Page } from '../components/Layout'
import { LoadStatus } from '../components/Status'

export default function LastSong() {
  const { data: song, error } = useLastSong()

  return (
    <Page>
      {song === undefined ? (
        <LoadStatus error={error} />
      ) : song === null ? (
        <p className="notice">No songs recorded yet.</p>
      ) : (
        <>
          <div className="grid grid-3">
            <ValueCard title="Anime">{song.anime}</ValueCard>
            <ValueCard title="Song">{song.name}</ValueCard>
            <ValueCard title="Artist">{song.artist}</ValueCard>
            <ValueCard title="Type">{song.type}</ValueCard>
            <ValueCard title="Links">
              <span className="song-links">
                {song.links.map((link) => (
                  <a key={link.name} href={link.url} target="_blank" rel="noreferrer">
                    {link.name}
                  </a>
                ))}
              </span>
            </ValueCard>
            <ValueCard title="Difficulty">{song.difficulty}</ValueCard>
          </div>
          <HistoryCard history={song.history} />
        </>
      )}
    </Page>
  )
}

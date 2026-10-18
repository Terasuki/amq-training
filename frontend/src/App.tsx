import { Navigate, Route, Routes } from 'react-router'
import { Nav } from './components/Layout'
import AllSongs from './pages/AllSongs'
import Home from './pages/Home'
import LastSong from './pages/LastSong'
import SongDetails from './pages/SongDetails'

export default function App() {
  return (
    <>
      <Nav />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/last-song" element={<LastSong />} />
        <Route path="/all-songs" element={<AllSongs />} />
        <Route path="/song-details" element={<SongDetails />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </>
  )
}

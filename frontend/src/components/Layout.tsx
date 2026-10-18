import { useQueryClient } from '@tanstack/react-query'
import { useState, type ReactNode } from 'react'
import { NavLink } from 'react-router'

const PAGES = [
  { to: '/', label: 'Home' },
  { to: '/last-song', label: 'Last Song' },
  { to: '/all-songs', label: 'All Songs' },
]

export function Nav() {
  return (
    <nav className="app-nav" aria-label="Pages">
      {PAGES.map(({ to, label }) => (
        <NavLink key={to} to={to} end>
          {label}
        </NavLink>
      ))}
      <UpdateDataButton />
    </nav>
  )
}

/** Refetches the queries on screen and marks the rest (e.g. the dashboard) stale. */
function UpdateDataButton() {
  const queryClient = useQueryClient()
  const [updating, setUpdating] = useState(false)

  const update = async () => {
    setUpdating(true)
    try {
      await queryClient.invalidateQueries()
    } finally {
      setUpdating(false)
    }
  }

  return (
    <button type="button" className="btn btn-primary app-nav-update" onClick={update} disabled={updating}>
      {updating && <span className="spinner spinner--inline" aria-hidden />}
      Update data
    </button>
  )
}

interface PageProps {
  /** Use the full window width instead of a centered column. */
  fluid?: boolean
  children: ReactNode
}

export function Page({ fluid = false, children }: PageProps) {
  return (
    <main className={fluid ? 'page page--fluid' : 'page'}>
      {children}
    </main>
  )
}

import type { ReactNode } from 'react'
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
    </nav>
  )
}

interface PageProps {
  title: string
  /** Use the full window width instead of a centered column. */
  fluid?: boolean
  children: ReactNode
}

export function Page({ title, fluid = false, children }: PageProps) {
  return (
    <main className={fluid ? 'page page--fluid' : 'page'}>
      <h2 className="page-title">{title}</h2>
      {children}
    </main>
  )
}

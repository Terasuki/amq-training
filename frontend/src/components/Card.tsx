import type { ReactNode } from 'react'

interface CardProps {
  title?: string
  subtitle?: string
  /**
   * Index into the pastel palette (`.card-tint-*` in index.css) for the
   * background, so a row of cards can rotate through the palette instead of
   * repeating one color. Mauve when left out.
   */
  tint?: number
  className?: string
  children: ReactNode
}

export function Card({ title, subtitle, tint, className, children }: CardProps) {
  const classes = ['card', tint !== undefined && `card-tint-${tint}`, className]
  return (
    <section className={classes.filter(Boolean).join(' ')}>
      {title && <h5 className="card-title">{title}</h5>}
      {subtitle && <p className="card-subtitle">{subtitle}</p>}
      {children}
    </section>
  )
}

/** A card showing one value large and centered, e.g. a KPI. */
export function ValueCard({
  title,
  tint = 0,
  children,
}: {
  title: string
  tint?: number
  children: ReactNode
}) {
  return (
    <Card title={title} tint={tint}>
      <div className="card-contents">{children}</div>
    </Card>
  )
}

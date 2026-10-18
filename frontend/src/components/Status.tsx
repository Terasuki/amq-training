export function Spinner() {
  return <span className="spinner" role="status" aria-label="Loading" />
}

/** What a page shows before its data arrives: a spinner, or why it failed. */
export function LoadStatus({ error }: { error: Error | null }) {
  if (error) return <p className="notice">Couldn't load data: {error.message}</p>
  return <Spinner />
}

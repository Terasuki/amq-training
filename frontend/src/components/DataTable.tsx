import { useDeferredValue, useMemo, useState, type ReactNode } from 'react'
import { formatCount } from '../format'

export type CellValue = string | number | null

export interface Column<T> {
  header: string
  /** What the cell shows, and what it sorts and filters by. */
  value: (row: T) => CellValue
  /** Custom cell content in place of the value. */
  render?: (row: T) => ReactNode
  /** Column width under `fixedLayout`, e.g. "40%". */
  width?: string
}

interface DataTableProps<T> {
  rows: T[]
  columns: Column<T>[]
  rowKey: (row: T) => string | number
  rowClassName?: (row: T) => string
  onRowClick?: (row: T) => void
  /** Sortable headers, with a filter box under each one. */
  interactive?: boolean
  /** Splits the rows into pages, with a row count and page controls below. */
  pageSize?: number
  /** Noun for the row count, e.g. "plays". */
  rowNoun?: string
  /** Sizes columns by their `width` instead of their contents. */
  fixedLayout?: boolean
}

interface Sort {
  column: number
  descending: boolean
}

type Predicate = (value: CellValue) => boolean

const collator = new Intl.Collator(undefined, { numeric: true, sensitivity: 'base' })
const OPERATOR = /^(>=|<=|!=|>|<|=)\s*(.*)$/

/**
 * Filter box syntax, as in the Dash tables this replaces: plain text keeps
 * cells containing it, ignoring case. A leading =, !=, >, >=, < or <= compares
 * instead, numerically in number columns (e.g. ">50" under Diff.).
 */
function parseFilter(text: string): Predicate | null {
  const trimmed = text.trim()
  const match = trimmed.match(OPERATOR)
  const operator = match?.[1]
  const operand = (match ? match[2] : trimmed).toLowerCase()
  if (!operand) return null
  if (!operator) {
    return (value) => value != null && String(value).toLowerCase().includes(operand)
  }

  const number = Number(operand)
  return (value) => {
    if (value == null) return false
    const order =
      typeof value === 'number' && !Number.isNaN(number)
        ? value - number
        : collator.compare(String(value), operand)
    switch (operator) {
      case '=':
        return order === 0
      case '!=':
        return order !== 0
      case '>':
        return order > 0
      case '>=':
        return order >= 0
      case '<':
        return order < 0
      default:
        return order <= 0
    }
  }
}

/** Ascending order, with empty cells last. */
function compareCells(a: CellValue, b: CellValue) {
  if (a == null || b == null) return a == null ? (b == null ? 0 : 1) : -1
  if (typeof a === 'number' && typeof b === 'number') return a - b
  return collator.compare(String(a), String(b))
}

export function DataTable<T>({
  rows,
  columns,
  rowKey,
  rowClassName,
  onRowClick,
  interactive = false,
  pageSize,
  rowNoun = 'rows',
  fixedLayout = false,
}: DataTableProps<T>) {
  const [filters, setFilters] = useState(() => columns.map(() => ''))
  const [sort, setSort] = useState<Sort | null>(null)
  const [page, setPage] = useState(0)
  // Typing stays responsive while a large table re-filters in the background.
  const deferredFilters = useDeferredValue(filters)

  const filtered = useMemo(() => {
    const active = deferredFilters.flatMap((text, i) => {
      const matches = parseFilter(text)
      return matches ? [{ value: columns[i].value, matches }] : []
    })
    if (active.length === 0) return rows
    return rows.filter((row) => active.every(({ value, matches }) => matches(value(row))))
  }, [rows, columns, deferredFilters])

  const sorted = useMemo(() => {
    if (!sort) return filtered
    const { value } = columns[sort.column]
    const direction = sort.descending ? -1 : 1
    return filtered
      .map((row) => ({ row, key: value(row) }))
      .sort((a, b) =>
        a.key == null || b.key == null
          ? compareCells(a.key, b.key)
          : compareCells(a.key, b.key) * direction,
      )
      .map(({ row }) => row)
  }, [filtered, columns, sort])

  const pageCount = pageSize ? Math.max(1, Math.ceil(sorted.length / pageSize)) : 1
  // Rows can shrink under the current page when the data refreshes.
  const pageIndex = Math.min(page, pageCount - 1)
  const visible = pageSize ? sorted.slice(pageIndex * pageSize, (pageIndex + 1) * pageSize) : sorted

  const setFilter = (column: number, text: string) => {
    setFilters((current) => current.with(column, text))
    setPage(0)
  }

  // Unsorted -> ascending -> descending -> unsorted
  const toggleSort = (column: number) => {
    setSort((current) =>
      current?.column !== column
        ? { column, descending: false }
        : current.descending
          ? null
          : { column, descending: true },
    )
    setPage(0)
  }

  const sortState = (column: number) =>
    sort?.column !== column ? 'none' : sort.descending ? 'descending' : 'ascending'

  return (
    <>
      <div className="table-wrap">
        <table className={fixedLayout ? 'data-table data-table--fixed' : 'data-table'}>
          {fixedLayout && (
            <colgroup>
              {columns.map((column) => (
                <col key={column.header} style={{ width: column.width }} />
              ))}
            </colgroup>
          )}
          <thead>
            <tr>
              {columns.map((column, i) => (
                <th key={column.header} scope="col" aria-sort={interactive ? sortState(i) : undefined}>
                  {interactive ? (
                    <button type="button" className="sort-button" onClick={() => toggleSort(i)}>
                      {column.header}
                      <span className="sort-indicator" aria-hidden>
                        {{ none: '', ascending: '▲', descending: '▼' }[sortState(i)]}
                      </span>
                    </button>
                  ) : (
                    column.header
                  )}
                </th>
              ))}
            </tr>
            {interactive && (
              <tr className="filter-row">
                {columns.map((column, i) => (
                  <th key={column.header}>
                    <input
                      type="search"
                      aria-label={`Filter ${column.header}`}
                      value={filters[i]}
                      onChange={(event) => setFilter(i, event.target.value)}
                    />
                  </th>
                ))}
              </tr>
            )}
          </thead>
          <tbody>
            {visible.map((row) => (
              <tr
                key={rowKey(row)}
                className={[rowClassName?.(row), onRowClick && 'row-clickable']
                  .filter(Boolean)
                  .join(' ')}
                {...(onRowClick && {
                  tabIndex: 0,
                  onClick: () => onRowClick(row),
                  onKeyDown: (event) => {
                    if (event.key === 'Enter') onRowClick(row)
                  },
                })}
              >
                {columns.map((column) => (
                  <td key={column.header}>{column.render ? column.render(row) : column.value(row)}</td>
                ))}
              </tr>
            ))}
            {visible.length === 0 && (
              <tr className="empty-row">
                <td colSpan={columns.length}>{rows.length ? 'No matches' : 'Nothing here yet'}</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
      {pageSize !== undefined && (
        <div className="table-footer">
          <span>
            {formatCount(sorted.length)} {rowNoun}
          </span>
          {pageCount > 1 && (
            <nav className="pagination" aria-label="Table pages">
              <button type="button" onClick={() => setPage(0)} disabled={pageIndex === 0} aria-label="First page">
                «
              </button>
              <button
                type="button"
                onClick={() => setPage(pageIndex - 1)}
                disabled={pageIndex === 0}
                aria-label="Previous page"
              >
                ‹
              </button>
              <span className="pagination-status">
                {formatCount(pageIndex + 1)} / {formatCount(pageCount)}
              </span>
              <button
                type="button"
                onClick={() => setPage(pageIndex + 1)}
                disabled={pageIndex === pageCount - 1}
                aria-label="Next page"
              >
                ›
              </button>
              <button
                type="button"
                onClick={() => setPage(pageCount - 1)}
                disabled={pageIndex === pageCount - 1}
                aria-label="Last page"
              >
                »
              </button>
            </nav>
          )}
        </div>
      )}
    </>
  )
}

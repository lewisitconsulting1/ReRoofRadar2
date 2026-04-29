import { useState, useMemo } from 'react'
import { ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { cn } from '@/lib/utils'
import type { Property, SortField, SortConfig, PaginationState, FilterState } from '@/types/search'

interface ResultsTableProps {
  properties: Property[]
  isLoading: boolean
  filters: FilterState
}

function ResultsTable({ properties, isLoading, filters }: ResultsTableProps): JSX.Element {
  const [sort, setSort] = useState<SortConfig>({ field: 'confidence_score', direction: 'desc' })
  const [pagination, setPagination] = useState<PaginationState>({ page: 1, size: 25 })

  const filteredProperties = useMemo(() => {
    let result = [...properties]

    if (filters.scoreRange[0] > 0 || filters.scoreRange[1] < 1) {
      result = result.filter(
        (p) => p.confidence_score >= filters.scoreRange[0] && p.confidence_score <= filters.scoreRange[1]
      )
    }

    if (filters.severityRange[0] > 0 || filters.severityRange[1] < 4) {
      result = result.filter(
        (p) => p.severity >= filters.severityRange[0] && p.severity <= filters.severityRange[1]
      )
    }

    if (filters.yearBuiltRange[0] > 1800 || filters.yearBuiltRange[1] < 2030) {
      result = result.filter(
        (p) =>
          p.year_built !== null &&
          p.year_built >= filters.yearBuiltRange[0] &&
          p.year_built <= filters.yearBuiltRange[1]
      )
    }

    if (filters.hasOwnerEmail) {
      result = result.filter((p) => p.owner_email !== null && p.owner_email.length > 0)
    }

    return result
  }, [properties, filters])

  const sortedProperties = useMemo(() => {
    const result = [...filteredProperties]
    result.sort((a, b) => {
      let aVal: string | number
      let bVal: string | number
      switch (sort.field) {
        case 'address':
          aVal = `${a.address} ${a.city}`.toLowerCase()
          bVal = `${b.address} ${b.city}`.toLowerCase()
          break
        case 'city':
          aVal = a.city.toLowerCase()
          bVal = b.city.toLowerCase()
          break
        case 'confidence_score':
          aVal = a.confidence_score
          bVal = b.confidence_score
          break
        case 'severity':
          aVal = a.severity
          bVal = b.severity
          break
        case 'year_built':
          aVal = a.year_built ?? 0
          bVal = b.year_built ?? 0
          break
      }
      if (typeof aVal === 'string' && typeof bVal === 'string') {
        return sort.direction === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal)
      }
      return sort.direction === 'asc' ? (aVal as number) - (bVal as number) : (bVal as number) - (aVal as number)
    })
    return result
  }, [filteredProperties, sort])

  const paginatedProperties = useMemo(() => {
    const start = (pagination.page - 1) * pagination.size
    return sortedProperties.slice(start, start + pagination.size)
  }, [sortedProperties, pagination])

  const totalPages = Math.ceil(filteredProperties.length / pagination.size)

  const handleSort = (field: SortField): void => {
    setSort((prev) => ({
      field,
      direction: prev.field === field && prev.direction === 'asc' ? 'desc' : 'asc',
    }))
  }

  const getSortIcon = (field: SortField): JSX.Element | null => {
    if (sort.field !== field) return <ArrowUpDown className="ml-1 h-4 w-4" />
    return sort.direction === 'asc' ? (
      <ArrowUp className="ml-1 h-4 w-4" />
    ) : (
      <ArrowDown className="ml-1 h-4 w-4" />
    )
  }

  const formatScore = (score: number): string => score.toFixed(2)

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <p className="text-sm text-muted-foreground">Loading results...</p>
      </div>
    )
  }

  if (paginatedProperties.length === 0 && !isLoading) {
    return (
      <div className="rounded-lg border p-8 text-center">
        <p className="text-muted-foreground">No properties match the current filters.</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          Showing {paginatedProperties.length} of {filteredProperties.length} properties
        </p>
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground">Per page:</span>
          <Select
            value={String(pagination.size)}
            onValueChange={(value) => {
              setPagination({ page: 1, size: Number(value) as 25 | 50 | 100 })
            }}
          >
            <SelectTrigger className="h-8 w-[80px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="25">25</SelectItem>
              <SelectItem value="50">50</SelectItem>
              <SelectItem value="100">100</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>
                <Button variant="ghost" size="sm" className="h-8 p-0 font-semibold" onClick={() => handleSort('address')}>
                  Address {getSortIcon('address')}
                </Button>
              </TableHead>
              <TableHead>
                <Button variant="ghost" size="sm" className="h-8 p-0 font-semibold" onClick={() => handleSort('city')}>
                  City {getSortIcon('city')}
                </Button>
              </TableHead>
              <TableHead>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-8 p-0 font-semibold"
                  onClick={() => handleSort('confidence_score')}
                >
                  Score {getSortIcon('confidence_score')}
                </Button>
              </TableHead>
              <TableHead>
                <Button variant="ghost" size="sm" className="h-8 p-0 font-semibold" onClick={() => handleSort('severity')}>
                  Severity {getSortIcon('severity')}
                </Button>
              </TableHead>
              <TableHead>
                <Button variant="ghost" size="sm" className="h-8 p-0 font-semibold" onClick={() => handleSort('year_built')}>
                  Year Built {getSortIcon('year_built')}
                </Button>
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {paginatedProperties.map((property) => (
              <TableRow
                key={property.id}
                className={cn(property.confidence_score >= 0.6 && 'bg-red-50/50 dark:bg-red-950/20')}
              >
                <TableCell className="font-medium">
                  {property.address}
                  {property.confidence_score >= 0.6 && (
                    <Badge variant="hot" className="ml-2">
                      Hot Lead
                    </Badge>
                  )}
                </TableCell>
                <TableCell>{property.city}</TableCell>
                <TableCell>
                  <span className={cn('font-semibold', property.confidence_score >= 0.6 ? 'text-red-600' : '')}>
                    {formatScore(property.confidence_score)}
                  </span>
                </TableCell>
                <TableCell>{property.severity.toFixed(1)}&quot;</TableCell>
                <TableCell>{property.year_built ?? 'N/A'}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          Page {pagination.page} of {totalPages || 1}
        </p>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            disabled={pagination.page <= 1}
            onClick={() => setPagination((prev) => ({ ...prev, page: prev.page - 1 }))}
          >
            Previous
          </Button>
          <Button
            variant="outline"
            size="sm"
            disabled={pagination.page >= totalPages}
            onClick={() => setPagination((prev) => ({ ...prev, page: prev.page + 1 }))}
          >
            Next
          </Button>
        </div>
      </div>
    </div>
  )
}

export { ResultsTable }

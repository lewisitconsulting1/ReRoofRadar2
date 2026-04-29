import { useState } from 'react'
import { format, subMonths } from 'date-fns'
import { CalendarIcon, Loader2, SearchIcon, AlertCircle } from 'lucide-react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Slider } from '@/components/ui/slider'
import { Calendar } from '@/components/ui/calendar'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { cn } from '@/lib/utils'
import type { SearchParams } from '@/types/search'

interface SearchDashboardProps {
  onSearch: (params: SearchParams) => void
  isLoading: boolean
  error: Error | null
  hasSearched: boolean
}

function SearchDashboard({ onSearch, isLoading, error, hasSearched }: SearchDashboardProps): JSX.Element {
  const [zipCode, setZipCode] = useState('')
  const [zipError, setZipError] = useState('')
  const [radius, setRadius] = useState([10])
  const [dateFrom, setDateFrom] = useState<Date | undefined>(subMonths(new Date(), 24))
  const [dateTo, setDateTo] = useState<Date | undefined>(new Date())
  const [minSeverity, setMinSeverity] = useState([0])
  const [fromOpen, setFromOpen] = useState(false)
  const [toOpen, setToOpen] = useState(false)

  const validateZip = (value: string): boolean => {
    if (!/^\d{5}$/.test(value)) {
      setZipError('Enter a valid 5-digit ZIP code')
      return false
    }
    setZipError('')
    return true
  }

  const handleZipChange = (value: string): void => {
    const cleaned = value.replace(/\D/g, '').slice(0, 5)
    setZipCode(cleaned)
    if (cleaned.length > 0) validateZip(cleaned)
    else setZipError('')
  }

  const handleSearch = (): void => {
    if (!validateZip(zipCode)) return
    if (!dateFrom || !dateTo) {
      toast.error('Please select both start and end dates')
      return
    }
    onSearch({
      zip_code: zipCode,
      radius_miles: radius[0],
      date_from: format(dateFrom, 'yyyy-MM-dd'),
      date_to: format(dateTo, 'yyyy-MM-dd'),
      min_severity: minSeverity[0],
    })
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <SearchIcon className="h-5 w-5" />
            Search Hail Damage
          </CardTitle>
          <CardDescription>
            Enter a ZIP code and adjust filters to find properties affected by hail.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div className="space-y-2">
              <Label htmlFor="zip-code">ZIP Code</Label>
              <Input
                id="zip-code"
                placeholder="e.g. 75201"
                value={zipCode}
                onChange={(e) => handleZipChange(e.target.value)}
                className={cn(zipError && 'border-destructive')}
                maxLength={5}
                inputMode="numeric"
              />
              {zipError && <p className="text-sm text-destructive">{zipError}</p>}
            </div>

            <div className="space-y-2">
              <Label>Radius: {radius[0]} miles</Label>
              <Slider
                value={radius}
                onValueChange={setRadius}
                min={0}
                max={50}
                step={1}
                className="mt-2"
              />
            </div>

            <div className="space-y-2">
              <Label>Date From</Label>
              <Popover open={fromOpen} onOpenChange={setFromOpen}>
                <PopoverTrigger asChild>
                  <Button
                    variant="outline"
                    className={cn('w-full justify-start text-left font-normal', !dateFrom && 'text-muted-foreground')}
                  >
                    <CalendarIcon className="mr-2 h-4 w-4" />
                    {dateFrom ? format(dateFrom, 'MMM dd, yyyy') : 'Pick a date'}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0">
                  <Calendar
                    mode="single"
                    selected={dateFrom}
                    onSelect={(date) => {
                      setDateFrom(date)
                      setFromOpen(false)
                    }}
                    disabled={(date) => date > (dateTo ?? new Date()) || date > new Date()}
                    initialFocus
                  />
                </PopoverContent>
              </Popover>
            </div>

            <div className="space-y-2">
              <Label>Date To</Label>
              <Popover open={toOpen} onOpenChange={setToOpen}>
                <PopoverTrigger asChild>
                  <Button
                    variant="outline"
                    className={cn('w-full justify-start text-left font-normal', !dateTo && 'text-muted-foreground')}
                  >
                    <CalendarIcon className="mr-2 h-4 w-4" />
                    {dateTo ? format(dateTo, 'MMM dd, yyyy') : 'Pick a date'}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0">
                  <Calendar
                    mode="single"
                    selected={dateTo}
                    onSelect={(date) => {
                      setDateTo(date)
                      setToOpen(false)
                    }}
                    disabled={(date) => date < (dateFrom ?? new Date(0)) || date > new Date()}
                    initialFocus
                  />
                </PopoverContent>
              </Popover>
            </div>
          </div>

          <div className="space-y-2">
            <Label>Minimum Severity: {minSeverity[0].toFixed(1)}&quot;</Label>
            <Slider
              value={minSeverity}
              onValueChange={setMinSeverity}
              min={0}
              max={4}
              step={0.1}
              className="mt-2"
            />
          </div>

          <Button onClick={handleSearch} disabled={isLoading || !zipCode || !!zipError} className="w-full sm:w-auto">
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Searching...
              </>
            ) : (
              <>
                <SearchIcon className="mr-2 h-4 w-4" />
                Search
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {isLoading && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
            <p className="mt-4 text-sm text-muted-foreground">Searching for hail events and properties...</p>
          </CardContent>
        </Card>
      )}

      {error && (
        <Card className="border-destructive">
          <CardContent className="flex items-start gap-3 py-6">
            <AlertCircle className="h-5 w-5 text-destructive mt-0.5 shrink-0" />
            <div>
              <p className="font-medium text-destructive">Search failed</p>
              <p className="mt-1 text-sm text-muted-foreground">{error.message}</p>
            </div>
          </CardContent>
        </Card>
      )}

      {!isLoading && !error && hasSearched && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <div className="rounded-full bg-muted p-4">
              <SearchIcon className="h-8 w-8 text-muted-foreground" />
            </div>
            <p className="mt-4 font-medium">No results found</p>
            <p className="mt-1 text-sm text-muted-foreground">
              Try adjusting your search criteria or radius.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export { SearchDashboard }

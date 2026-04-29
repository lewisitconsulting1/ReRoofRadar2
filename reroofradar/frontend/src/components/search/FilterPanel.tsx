import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { Slider } from '@/components/ui/slider'
import { Checkbox } from '@/components/ui/checkbox'
import type { FilterState } from '@/types/search'

interface FilterPanelProps {
  filters: FilterState
  onFilterChange: (filters: FilterState) => void
  maxSeverity?: number
  minYear?: number
  maxYear?: number
}

function FilterPanel({
  filters,
  onFilterChange,
  maxSeverity = 4,
  minYear = 1900,
  maxYear = 2025,
}: FilterPanelProps): JSX.Element {
  const handleScoreChange = (value: number[]): void => {
    onFilterChange({ ...filters, scoreRange: [value[0], value[1]] })
  }

  const handleSeverityChange = (value: number[]): void => {
    onFilterChange({ ...filters, severityRange: [value[0], value[1]] })
  }

  const handleYearBuiltChange = (value: number[]): void => {
    onFilterChange({ ...filters, yearBuiltRange: [value[0], value[1]] })
  }

  const handleOwnerEmailChange = (checked: boolean): void => {
    onFilterChange({ ...filters, hasOwnerEmail: checked })
  }

  return (
    <Card>
      <CardHeader className="pb-4">
        <CardTitle className="text-base">Filters</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-3">
          <Label>
            Confidence Score: {filters.scoreRange[0].toFixed(2)} - {filters.scoreRange[1].toFixed(2)}
          </Label>
          <Slider
            value={[filters.scoreRange[0], filters.scoreRange[1]]}
            onValueChange={handleScoreChange}
            min={0}
            max={1}
            step={0.01}
          />
        </div>

        <div className="space-y-3">
          <Label>
            Severity: {filters.severityRange[0].toFixed(1)}&quot; - {filters.severityRange[1].toFixed(1)}&quot;
          </Label>
          <Slider
            value={[filters.severityRange[0], filters.severityRange[1]]}
            onValueChange={handleSeverityChange}
            min={0}
            max={maxSeverity}
            step={0.1}
          />
        </div>

        <div className="space-y-3">
          <Label>
            Year Built: {filters.yearBuiltRange[0]} - {filters.yearBuiltRange[1]}
          </Label>
          <Slider
            value={[filters.yearBuiltRange[0], filters.yearBuiltRange[1]]}
            onValueChange={handleYearBuiltChange}
            min={minYear}
            max={maxYear}
            step={1}
          />
        </div>

        <div className="flex items-center space-x-2">
          <Checkbox
            id="has-owner-email"
            checked={filters.hasOwnerEmail}
            onCheckedChange={handleOwnerEmailChange}
          />
          <Label htmlFor="has-owner-email" className="text-sm font-normal">
            Has owner email
          </Label>
        </div>
      </CardContent>
    </Card>
  )
}

export { FilterPanel }

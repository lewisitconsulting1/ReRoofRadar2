import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { toast } from 'sonner'
import { Layout } from '@/components/layout/Layout'
import { SearchDashboard } from '@/components/search/SearchDashboard'
import { ResultsTable } from '@/components/search/ResultsTable'
import { FilterPanel } from '@/components/search/FilterPanel'
import { ExportButton } from '@/components/search/ExportButton'
import { api } from '@/lib/api'
import type { SearchParams, Property, FilterState, SearchResponse } from '@/types/search'

const defaultFilters: FilterState = {
  scoreRange: [0, 1],
  severityRange: [0, 4],
  yearBuiltRange: [1900, 2025],
  hasOwnerEmail: false,
}

function Dashboard(): JSX.Element {
  const [properties, setProperties] = useState<Property[]>([])
  const [campaignId, setCampaignId] = useState<string | null>(null)
  const [filters, setFilters] = useState<FilterState>(defaultFilters)
  const [hasSearched, setHasSearched] = useState(false)

  const searchMutation = useMutation({
    mutationFn: async (params: SearchParams): Promise<SearchResponse> => {
      const response = await api.post('/api/search/hail', params)
      return response.data
    },
    onSuccess: (data) => {
      setProperties(data.properties)
      setCampaignId(data.campaign.id)
      setHasSearched(true)
      toast.success(`Found ${data.properties.length} properties across ${data.campaign.hail_events_found} hail events`)
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Search failed')
      setHasSearched(true)
    },
  })

  const handleSearch = (params: SearchParams): void => {
    setFilters(defaultFilters)
    searchMutation.mutate(params)
  }

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Search</h1>
          <p className="text-muted-foreground">Search for hail-damaged properties by ZIP code.</p>
        </div>

        <SearchDashboard
          onSearch={handleSearch}
          isLoading={searchMutation.isPending}
          error={searchMutation.error}
          hasSearched={hasSearched}
        />

        {hasSearched && properties.length > 0 && (
          <div className="grid gap-6 lg:grid-cols-[260px_1fr]">
            <aside>
              <FilterPanel filters={filters} onFilterChange={setFilters} />
            </aside>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold">Results</h2>
                {campaignId && <ExportButton campaignId={campaignId} />}
              </div>
              <ResultsTable
                properties={properties}
                isLoading={searchMutation.isPending}
                filters={filters}
              />
            </div>
          </div>
        )}
      </div>
    </Layout>
  )
}

export { Dashboard }

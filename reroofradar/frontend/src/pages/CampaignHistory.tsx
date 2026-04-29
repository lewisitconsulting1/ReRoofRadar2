import { useQuery } from '@tanstack/react-query'
import { Layout } from '@/components/layout/Layout'
import { api } from '@/lib/api'
import type { Campaign } from '@/types/search'

function CampaignHistory(): JSX.Element {
  const { data: campaigns = [], isLoading } = useQuery<Campaign[]>({
    queryKey: ['campaigns'],
    queryFn: async () => {
      const response = await api.get('/api/campaigns')
      return response.data
    },
  })

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Campaigns</h1>
          <p className="text-muted-foreground">View your search campaign history.</p>
        </div>
        <div className="rounded-lg border p-12 text-center">
          <p className="text-lg text-muted-foreground">Campaign history</p>
          <p className="mt-2 text-sm text-muted-foreground">{isLoading ? 'Loading...' : `${campaigns.length} campaigns found`}</p>
        </div>
      </div>
    </Layout>
  )
}

export { CampaignHistory }

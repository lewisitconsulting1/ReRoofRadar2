import { Layout } from '@/components/layout/Layout'

function Dashboard(): JSX.Element {
  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Search</h1>
          <p className="text-muted-foreground">Search for hail-damaged properties by ZIP code.</p>
        </div>
        <div className="rounded-lg border border-dashed p-12 text-center">
          <p className="text-lg text-muted-foreground">Search interface coming soon</p>
          <p className="mt-2 text-sm text-muted-foreground">Build out the search dashboard in the next step.</p>
        </div>
      </div>
    </Layout>
  )
}

export { Dashboard }

export interface Property {
  id: string
  address: string
  city: string
  state: string
  zip_code: string
  latitude: number
  longitude: number
  owner_name: string | null
  owner_email: string | null
  owner_phone: string | null
  year_built: number | null
  confidence_score: number
  severity: number
  last_hail_date: string | null
  data_source: string | null
  property_value: number | null
  created_at: string
}

export interface HailEvent {
  id: string
  event_date: string
  severity: number
  source: string
  state: string | null
  county: string | null
  polygon: [number, number][]
}

export interface Campaign {
  id: string
  zip_code: string
  radius_miles: number
  date_from: string
  date_to: string
  min_severity: number
  hail_events_found: number
  properties_returned: number
  status: 'pending' | 'running' | 'complete' | 'failed'
  error_message: string | null
  created_at: string
  completed_at: string | null
}

export interface SearchParams {
  zip_code: string
  radius_miles: number
  date_from: string
  date_to: string
  min_severity: number
}

export interface FilterState {
  scoreRange: [number, number]
  severityRange: [number, number]
  yearBuiltRange: [number, number]
  hasOwnerEmail: boolean
}

export type SortField = 'address' | 'city' | 'confidence_score' | 'severity' | 'year_built'
export type SortDirection = 'asc' | 'desc'

export interface SortConfig {
  field: SortField
  direction: SortDirection
}

export interface PaginationState {
  page: number
  size: 25 | 50 | 100
}

export interface SearchResponse {
  campaign: Campaign
  properties: Property[]
  total: number
  hail_events: HailEvent[]
}

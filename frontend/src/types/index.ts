export interface TopProblem {
  rank: number;
  problem_id: number;
  problem_summary: string;
  product: string;
  mentions_count: number;
  trend: 'rising' | 'stable' | 'declining';
  sources: string[];
  severity_score: number;
  sentiment_score: number;
  ranking_score: number;
}

export interface Mention {
  id: number;
  source: string;
  source_url: string;
  raw_text: string;
  excerpt: string;
  author: string;
  sentiment_score: number;
  created_at: string;
}

export interface ProblemDetail {
  id: number;
  problem_summary: string;
  problem_description: string;
  product: string;
  severity_score: number;
  sentiment_score: number;
  frequency: number;
  first_seen: string;
  last_seen: string;
  trend: string;
  mentions: Mention[];
}

export interface DashboardStats {
  total_problems: number;
  total_mentions: number;
  last_updated: string | null;
  sources_count: Record<string, number>;
  product_distribution: Record<string, number>;
}

export interface TimeSeriesData {
  date: string;
  count: number;
}

export interface ScrapingStatus {
  is_running: boolean;
  last_run: string | null;
  next_run: string | null;
  sources_status: Record<string, {
    status: string;
    last_run: string | null;
    items_collected: number;
  }>;
}

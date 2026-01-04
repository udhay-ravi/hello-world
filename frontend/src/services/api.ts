import axios from 'axios';
import { TopProblem, ProblemDetail, DashboardStats, TimeSeriesData, ScrapingStatus } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const dashboardApi = {
  getTopProblems: async (limit: number = 10, product?: string, days: number = 30): Promise<TopProblem[]> => {
    const params: any = { limit, days };
    if (product && product !== 'All') {
      params.product = product;
    }
    const response = await api.get('/api/dashboard/top-problems', { params });
    return response.data;
  },

  getProblemDetail: async (problemId: number): Promise<ProblemDetail> => {
    const response = await api.get(`/api/dashboard/problem/${problemId}`);
    return response.data;
  },

  getStats: async (): Promise<DashboardStats> => {
    const response = await api.get('/api/dashboard/stats');
    return response.data;
  },

  getTimeSeries: async (days: number = 30, product?: string): Promise<TimeSeriesData[]> => {
    const params: any = { days };
    if (product && product !== 'All') {
      params.product = product;
    }
    const response = await api.get('/api/dashboard/time-series', { params });
    return response.data;
  },

  getProducts: async (): Promise<string[]> => {
    const response = await api.get('/api/dashboard/products');
    return response.data.products;
  },

  exportCSV: async (limit: number = 10, product?: string, days: number = 30): Promise<{ filename: string; content: string }> => {
    const params: any = { limit, days };
    if (product && product !== 'All') {
      params.product = product;
    }
    const response = await api.get('/api/dashboard/export/csv', { params });
    return response.data;
  },

  exportMarkdown: async (limit: number = 10, product?: string, days: number = 30): Promise<{ filename: string; content: string }> => {
    const params: any = { limit, days };
    if (product && product !== 'All') {
      params.product = product;
    }
    const response = await api.get('/api/dashboard/export/markdown', { params });
    return response.data;
  },
};

export const scrapingApi = {
  triggerScraping: async (): Promise<{ status: string; message: string }> => {
    const response = await api.post('/api/scraping/trigger');
    return response.data;
  },

  getStatus: async (): Promise<ScrapingStatus> => {
    const response = await api.get('/api/scraping/status');
    return response.data;
  },
};

import React, { useState, useEffect } from 'react';
import { dashboardApi, scrapingApi } from '../services/api';
import { TopProblem, DashboardStats, TimeSeriesData } from '../types';
import TopProblemsTable from '../components/TopProblemsTable';
import StatsCards from '../components/StatsCards';
import { TimeSeriesChart, SourceDistributionChart, ProductDistributionChart } from '../components/Charts';
import ProblemDetailModal from '../components/ProblemDetailModal';
import Filters from '../components/Filters';
import { downloadFile } from '../utils/helpers';

const Dashboard: React.FC = () => {
  const [topProblems, setTopProblems] = useState<TopProblem[]>([]);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [timeSeriesData, setTimeSeriesData] = useState<TimeSeriesData[]>([]);
  const [products, setProducts] = useState<string[]>(['All']);
  const [selectedProduct, setSelectedProduct] = useState<string>('All');
  const [selectedDays, setSelectedDays] = useState<number>(30);
  const [selectedProblemId, setSelectedProblemId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  useEffect(() => {
    loadAllData();
  }, [selectedProduct, selectedDays]);

  const loadAllData = async () => {
    try {
      setLoading(true);

      // Load all data in parallel
      const [problemsData, statsData, timeSeriesData, productsData] = await Promise.all([
        dashboardApi.getTopProblems(10, selectedProduct, selectedDays),
        dashboardApi.getStats(),
        dashboardApi.getTimeSeries(selectedDays, selectedProduct),
        dashboardApi.getProducts()
      ]);

      setTopProblems(problemsData);
      setStats(statsData);
      setTimeSeriesData(timeSeriesData);
      setProducts(productsData);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      await scrapingApi.triggerScraping();
      // Wait a bit for scraping to complete, then reload data
      setTimeout(() => {
        loadAllData();
        setIsRefreshing(false);
      }, 5000);
    } catch (error) {
      console.error('Error triggering scraping:', error);
      setIsRefreshing(false);
    }
  };

  const handleExportCSV = async () => {
    try {
      const result = await dashboardApi.exportCSV(10, selectedProduct, selectedDays);
      downloadFile(result.filename, result.content);
    } catch (error) {
      console.error('Error exporting CSV:', error);
    }
  };

  const handleExportMarkdown = async () => {
    try {
      const result = await dashboardApi.exportMarkdown(10, selectedProduct, selectedDays);
      downloadFile(result.filename, result.content);
    } catch (error) {
      console.error('Error exporting Markdown:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-do-blue mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-do-dark text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold">DigitalOcean Customer Insights Dashboard</h1>
              <p className="mt-1 text-blue-200">IaaS Networking Products - Customer Pain Points Analysis</p>
            </div>
            <div className="flex gap-3">
              <button
                onClick={handleExportCSV}
                className="px-4 py-2 bg-white text-do-dark rounded-lg hover:bg-gray-100 transition-colors font-medium"
              >
                Export CSV
              </button>
              <button
                onClick={handleExportMarkdown}
                className="px-4 py-2 bg-white text-do-dark rounded-lg hover:bg-gray-100 transition-colors font-medium"
              >
                Export Report
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Cards */}
        {stats && <StatsCards stats={stats} />}

        {/* Filters */}
        <Filters
          products={products}
          selectedProduct={selectedProduct}
          onProductChange={setSelectedProduct}
          selectedDays={selectedDays}
          onDaysChange={setSelectedDays}
          onRefresh={handleRefresh}
          isRefreshing={isRefreshing}
        />

        {/* Top Problems Table */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Top 10 Customer Problems</h2>
          <TopProblemsTable
            problems={topProblems}
            onProblemClick={setSelectedProblemId}
          />
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <TimeSeriesChart data={timeSeriesData} />
          {stats && (
            <>
              <SourceDistributionChart data={stats.sources_count} />
              <ProductDistributionChart data={stats.product_distribution} />
            </>
          )}
        </div>
      </main>

      {/* Problem Detail Modal */}
      {selectedProblemId && (
        <ProblemDetailModal
          problemId={selectedProblemId}
          onClose={() => setSelectedProblemId(null)}
        />
      )}
    </div>
  );
};

export default Dashboard;

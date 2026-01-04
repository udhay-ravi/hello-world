import React from 'react';

interface Props {
  products: string[];
  selectedProduct: string;
  onProductChange: (product: string) => void;
  selectedDays: number;
  onDaysChange: (days: number) => void;
  onRefresh: () => void;
  isRefreshing: boolean;
}

const Filters: React.FC<Props> = ({
  products,
  selectedProduct,
  onProductChange,
  selectedDays,
  onDaysChange,
  onRefresh,
  isRefreshing
}) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-4 mb-6">
      <div className="flex flex-wrap items-center gap-4">
        {/* Product Filter */}
        <div className="flex items-center gap-2">
          <label className="text-sm font-medium text-gray-700">Product:</label>
          <select
            value={selectedProduct}
            onChange={(e) => onProductChange(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-do-blue"
          >
            {products.map((product) => (
              <option key={product} value={product}>
                {product}
              </option>
            ))}
          </select>
        </div>

        {/* Time Range Filter */}
        <div className="flex items-center gap-2">
          <label className="text-sm font-medium text-gray-700">Time Range:</label>
          <select
            value={selectedDays}
            onChange={(e) => onDaysChange(Number(e.target.value))}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-do-blue"
          >
            <option value={7}>Last 7 days</option>
            <option value={30}>Last 30 days</option>
            <option value={90}>Last 90 days</option>
          </select>
        </div>

        {/* Refresh Button */}
        <button
          onClick={onRefresh}
          disabled={isRefreshing}
          className="ml-auto flex items-center gap-2 px-4 py-2 bg-do-blue text-white rounded-lg hover:bg-blue-600 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          <svg
            className={`w-5 h-5 ${isRefreshing ? 'animate-spin' : ''}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
            />
          </svg>
          {isRefreshing ? 'Refreshing...' : 'Refresh Data'}
        </button>
      </div>
    </div>
  );
};

export default Filters;

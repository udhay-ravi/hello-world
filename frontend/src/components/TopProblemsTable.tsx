import React from 'react';
import { TopProblem } from '../types';
import { getTrendIcon, getTrendColor, getSourceBadgeColor, getSourceDisplayName } from '../utils/helpers';

interface Props {
  problems: TopProblem[];
  onProblemClick: (problemId: number) => void;
}

const TopProblemsTable: React.FC<Props> = ({ problems, onProblemClick }) => {
  return (
    <div className="bg-white shadow-md rounded-lg overflow-hidden">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Rank
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Problem Summary
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Product
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Mentions
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Severity
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Trend
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Sources
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {problems.map((problem) => (
              <tr
                key={problem.rank}
                onClick={() => onProblemClick(problem.problem_id)}
                className="hover:bg-gray-50 cursor-pointer transition-colors"
              >
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center justify-center w-8 h-8 rounded-full bg-do-blue text-white font-bold">
                    {problem.rank}
                  </div>
                </td>
                <td className="px-6 py-4">
                  <div className="text-sm font-medium text-gray-900 max-w-lg">
                    {problem.problem_summary}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                    {problem.product}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900 font-semibold">
                    {problem.mentions_count}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                      <div
                        className={`h-2 rounded-full ${
                          problem.severity_score >= 8 ? 'bg-red-600' :
                          problem.severity_score >= 6 ? 'bg-orange-500' :
                          'bg-yellow-500'
                        }`}
                        style={{ width: `${(problem.severity_score / 10) * 100}%` }}
                      />
                    </div>
                    <span className="text-xs text-gray-600">
                      {problem.severity_score.toFixed(1)}
                    </span>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`text-2xl ${getTrendColor(problem.trend)}`}>
                    {getTrendIcon(problem.trend)}
                  </span>
                  <span className={`ml-2 text-xs ${getTrendColor(problem.trend)}`}>
                    {problem.trend}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex flex-wrap gap-1">
                    {problem.sources.slice(0, 3).map((source) => (
                      <span
                        key={source}
                        className={`px-2 py-1 text-xs font-medium text-white rounded ${getSourceBadgeColor(source)}`}
                      >
                        {getSourceDisplayName(source)}
                      </span>
                    ))}
                    {problem.sources.length > 3 && (
                      <span className="px-2 py-1 text-xs font-medium text-gray-600 bg-gray-200 rounded">
                        +{problem.sources.length - 3}
                      </span>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default TopProblemsTable;

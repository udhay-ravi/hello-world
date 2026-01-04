import React, { useEffect, useState } from 'react';
import { ProblemDetail } from '../types';
import { dashboardApi } from '../services/api';
import { formatDateTime, getSentimentColor, getSentimentLabel, getSourceBadgeColor, getSourceDisplayName, copyToClipboard } from '../utils/helpers';

interface Props {
  problemId: number;
  onClose: () => void;
}

const ProblemDetailModal: React.FC<Props> = ({ problemId, onClose }) => {
  const [problem, setProblem] = useState<ProblemDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    const fetchProblem = async () => {
      try {
        const data = await dashboardApi.getProblemDetail(problemId);
        setProblem(data);
      } catch (error) {
        console.error('Error fetching problem details:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchProblem();
  }, [problemId]);

  const handleCopyInsight = async () => {
    if (!problem) return;

    const uniqueSources = Array.from(new Set(problem.mentions.map(m => m.source_url)));
    const text = `${problem.problem_summary}

${problem.problem_description}

Sources:
${uniqueSources.map((url, idx) => `${idx + 1}. ${url}`).join('\n')}`;

    const success = await copyToClipboard(text);
    if (success) {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-do-blue mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading problem details...</p>
        </div>
      </div>
    );
  }

  if (!problem) {
    return null;
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-900">Problem Details</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {/* Problem Summary */}
          <div className="mb-6">
            <h3 className="text-xl font-semibold text-gray-900 mb-2">{problem.problem_summary}</h3>
            <p className="text-gray-700">{problem.problem_description}</p>
          </div>

          {/* Metadata */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-xs text-gray-500 uppercase mb-1">Product</p>
              <p className="text-lg font-semibold text-gray-900">{problem.product}</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-xs text-gray-500 uppercase mb-1">Severity</p>
              <p className="text-lg font-semibold text-gray-900">{problem.severity_score.toFixed(1)}/10</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-xs text-gray-500 uppercase mb-1">Sentiment</p>
              <p className={`text-lg font-semibold ${getSentimentColor(problem.sentiment_score)}`}>
                {getSentimentLabel(problem.sentiment_score)}
              </p>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-xs text-gray-500 uppercase mb-1">Mentions</p>
              <p className="text-lg font-semibold text-gray-900">{problem.frequency}</p>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3 mb-6">
            <button
              onClick={handleCopyInsight}
              className="flex items-center gap-2 px-4 py-2 bg-do-blue text-white rounded-lg hover:bg-blue-600 transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              {copied ? 'Copied!' : 'Share Insight'}
            </button>
          </div>

          {/* Mentions List */}
          <div>
            <h4 className="text-lg font-semibold text-gray-900 mb-4">
              All Mentions ({problem.mentions.length})
            </h4>
            <div className="space-y-4">
              {problem.mentions.map((mention) => (
                <div key={mention.id} className="border border-gray-200 rounded-lg p-4 hover:border-do-blue transition-colors">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className={`px-2 py-1 text-xs font-medium text-white rounded ${getSourceBadgeColor(mention.source)}`}>
                        {getSourceDisplayName(mention.source)}
                      </span>
                      <span className="text-sm text-gray-500">by {mention.author}</span>
                    </div>
                    <span className="text-xs text-gray-400">{formatDateTime(mention.created_at)}</span>
                  </div>
                  <p className="text-gray-700 mb-2">{mention.excerpt}</p>
                  <a
                    href={mention.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-do-blue hover:underline flex items-center gap-1"
                  >
                    View source
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                  </a>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProblemDetailModal;

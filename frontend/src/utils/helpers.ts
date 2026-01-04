export const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};

export const formatDateTime = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

export const getTrendIcon = (trend: string): string => {
  switch (trend) {
    case 'rising':
      return '↑';
    case 'declining':
      return '↓';
    case 'stable':
    default:
      return '→';
  }
};

export const getTrendColor = (trend: string): string => {
  switch (trend) {
    case 'rising':
      return 'text-red-600';
    case 'declining':
      return 'text-green-600';
    case 'stable':
    default:
      return 'text-yellow-600';
  }
};

export const getSentimentColor = (sentiment: number): string => {
  if (sentiment > 0.2) return 'text-green-600';
  if (sentiment < -0.2) return 'text-red-600';
  return 'text-yellow-600';
};

export const getSentimentLabel = (sentiment: number): string => {
  if (sentiment > 0.2) return 'Positive';
  if (sentiment < -0.2) return 'Negative';
  return 'Neutral';
};

export const getSourceBadgeColor = (source: string): string => {
  const colors: Record<string, string> = {
    reddit: 'bg-orange-500',
    twitter: 'bg-blue-400',
    stackoverflow: 'bg-orange-600',
    hackernews: 'bg-orange-700',
    digitalocean_ideas: 'bg-blue-600',
    trustpilot: 'bg-green-600',
    google_trends: 'bg-red-500',
  };
  return colors[source] || 'bg-gray-500';
};

export const getSourceDisplayName = (source: string): string => {
  const names: Record<string, string> = {
    reddit: 'Reddit',
    twitter: 'Twitter',
    stackoverflow: 'Stack Overflow',
    hackernews: 'Hacker News',
    digitalocean_ideas: 'DO Ideas',
    trustpilot: 'Trustpilot',
    google_trends: 'Google Trends',
  };
  return names[source] || source;
};

export const downloadFile = (filename: string, content: string) => {
  const blob = new Blob([content], { type: 'text/plain' });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};

export const copyToClipboard = async (text: string): Promise<boolean> => {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (err) {
    console.error('Failed to copy:', err);
    return false;
  }
};

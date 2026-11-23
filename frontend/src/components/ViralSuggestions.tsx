import React, { useState, useEffect } from 'react';

interface ViralSuggestionsProps {
  transcriptionJob: any;
  suggestions: any[];
  onSuggestions: (suggestions: any[]) => void;
}

const ViralSuggestions: React.FC<ViralSuggestionsProps> = ({
  transcriptionJob,
  suggestions,
  onSuggestions,
}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (suggestions.length === 0 && transcriptionJob) {
      fetchSuggestions();
    }
  }, [transcriptionJob, suggestions.length]);

  const fetchSuggestions = async () => {
    setLoading(true);
    setError('');

    try {
      const response = await fetch('/api/analyze/viral', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ transcription_job_id: transcriptionJob.job_id }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to analyze');
      }

      onSuggestions(data.suggestions);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-gray-900">Viral Clip Suggestions</h3>
          <button
            onClick={fetchSuggestions}
            disabled={loading}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
          >
            {loading ? 'Analyzing...' : 'Analyze for Viral Clips'}
          </button>
        </div>

        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}

        {suggestions.length === 0 && !loading && (
          <div className="text-center py-12 text-gray-500">
            <p>Click "Analyze for Viral Clips" to get AI-powered suggestions</p>
          </div>
        )}

        {suggestions.length > 0 && (
          <div className="space-y-4">
            {suggestions.map((suggestion: any, index: number) => (
              <div
                key={index}
                className="bg-gray-50 rounded-lg p-4 border border-gray-200"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="px-2 py-1 bg-indigo-100 text-indigo-700 text-xs font-medium rounded">
                        #{index + 1}
                      </span>
                      <span className="px-2 py-1 bg-green-100 text-green-700 text-xs font-medium rounded">
                        {Math.round(suggestion.viral_score * 100)}% Viral Score
                      </span>
                      <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs font-medium rounded">
                        {suggestion.template}
                      </span>
                    </div>
                    <p className="text-gray-900 mb-2">{suggestion.reason}</p>
                    <div className="flex gap-4 text-sm text-gray-500">
                      <span>⏱ {formatTime(suggestion.start_time)} - {formatTime(suggestion.end_time)}</span>
                      <span>📏 {formatTime(suggestion.end_time - suggestion.start_time)}</span>
                    </div>
                  </div>
                  <button
                    onClick={() => createClipFromSuggestion(suggestion)}
                    className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 text-sm font-medium shrink-0"
                  >
                    Create This Clip
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

const createClipFromSuggestion = async (suggestion: any) => {
  // This would be handled by the parent component
  console.log('Create clip from suggestion:', suggestion);
};

const formatTime = (seconds: number): string => {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};

export default ViralSuggestions;
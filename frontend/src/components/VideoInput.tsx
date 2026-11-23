import React, { useState } from 'react';

interface VideoInputProps {
  onComplete: (job: any) => void;
}

const VideoInput: React.FC<VideoInputProps> = ({ onComplete }) => {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [jobId, setJobId] = useState<string | null>(null);
  const [status, setStatus] = useState<'idle' | 'processing' | 'completed' | 'failed'>('idle');
  const [progress, setProgress] = useState(0);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    setStatus('processing');
    setProgress(0);

    try {
      const response = await fetch('/api/transcribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to start transcription');
      }

      setJobId(data.job_id);
      pollStatus(data.job_id);
    } catch (err: any) {
      setError(err.message);
      setStatus('failed');
      setLoading(false);
    }
  };

  const pollStatus = async (jobId: string) => {
    try {
      const response = await fetch(`/api/transcribe/${jobId}/status`);
      const data = await response.json();

      if (data.status === 'completed') {
        setStatus('completed');
        setLoading(false);
        setProgress(100);
        onComplete(data);
      } else if (data.status === 'failed') {
        setStatus('failed');
        setLoading(false);
        setError(data.error || 'Transcription failed');
      } else {
        setProgress(data.progress || 0);
        setTimeout(() => pollStatus(jobId), 2000);
      }
    } catch (err) {
      setStatus('failed');
      setLoading(false);
      setError('Failed to check status');
    }
  };

  return (
    <div className="max-w-3xl mx-auto">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">Transcribe Video</h2>
        <p className="text-gray-600">
          Paste a YouTube URL or video link to get started with AI-powered transcription
        </p>
      </div>

      <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="mb-6">
          <label htmlFor="video-url" className="block text-sm font-medium text-gray-700 mb-2">
            Video URL
          </label>
          <input
            id="video-url"
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://youtube.com/watch?v=... or https://example.com/video.mp4"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            required
            disabled={loading}
          />
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={loading || !url}
          className="w-full py-3 px-4 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Processing...' : 'Start Transcription'}
        </button>

        {status === 'processing' && (
          <div className="mt-6">
            <div className="flex justify-between text-sm mb-2">
              <span className="text-gray-600">Processing video...</span>
              <span className="font-medium">{progress}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-indigo-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>
            <p className="text-sm text-gray-500 mt-2 text-center">
              This may take a few minutes depending on video length
            </p>
          </div>
        )}

        {status === 'completed' && (
          <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
            <p className="text-green-700 font-medium">Transcription completed!</p>
            <p className="text-sm text-green-600 mt-1">Navigate to "Create Clips" or "Viral Suggestions" tabs</p>
          </div>
        )}
      </form>

      <div className="mt-8 text-center text-sm text-gray-500">
        <p>Supported: YouTube, Vimeo, direct video links (MP4, WebM, etc.)</p>
      </div>
    </div>
  );
};

export default VideoInput;
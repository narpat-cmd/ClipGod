import React, { useState } from 'react';

interface ClipPlayerProps {
  transcriptionJob: any;
  onComplete: (job: any) => void;
}

const ClipPlayer: React.FC<ClipPlayerProps> = ({ transcriptionJob, onComplete }) => {
  const [startTime, setStartTime] = useState(0);
  const [endTime, setEndTime] = useState(30);
  const [template, setTemplate] = useState('vertical');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [clipJob, setClipJob] = useState<any>(null);

  const duration = transcriptionJob.duration || 60;
  const maxEndTime = Math.min(startTime + 60, duration);

  const handleCreateClip = async () => {
    if (startTime >= endTime) {
      setError('End time must be after start time');
      return;
    }
    if (endTime - startTime > 60) {
      setError('Clip duration cannot exceed 60 seconds');
      return;
    }

    setError('');
    setLoading(true);

    try {
      const response = await fetch('/api/clips', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          transcription_job_id: transcriptionJob.job_id,
          start_time: startTime,
          end_time: endTime,
          template: template,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to create clip');
      }

      setClipJob(data);
      pollClipStatus(data.job_id);
    } catch (err: any) {
      setError(err.message);
      setLoading(false);
    }
  };

  const pollClipStatus = async (jobId: string) => {
    try {
      const response = await fetch(`/api/clips/${jobId}/status`);
      const data = await response.json();

      if (data.status === 'completed') {
        setLoading(false);
        onComplete(data);
      } else if (data.status === 'failed') {
        setLoading(false);
        setError(data.error || 'Clip generation failed');
      } else {
        setTimeout(() => pollClipStatus(jobId), 2000);
      }
    } catch (err) {
      setLoading(false);
      setError('Failed to check clip status');
    }
  };

  const handleSegmentClick = (segment: any) => {
    setStartTime(Math.max(0, segment.start - 1));
    setEndTime(Math.min(duration, segment.end + 1));
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900">Create Clip</h3>
      </div>

      <div className="p-6 space-y-6">
        {/* Timeline Selector */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Select Time Range (Max 60s)
          </label>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>Start: {formatTime(startTime)}</span>
                <span>End: {formatTime(endTime)}</span>
                <span>Duration: {formatTime(endTime - startTime)}</span>
              </div>
              <input
                type="range"
                min={0}
                max={duration}
                step={0.5}
                value={startTime}
                onChange={(e) => {
                  const val = parseFloat(e.target.value);
                  setStartTime(val);
                  if (val >= endTime) setEndTime(Math.min(val + 5, duration));
                }}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
              />
            </div>
            <div>
              <input
                type="range"
                min={0}
                max={duration}
                step={0.5}
                value={endTime}
                onChange={(e) => {
                  const val = parseFloat(e.target.value);
                  setEndTime(val);
                  if (val <= startTime) setStartTime(Math.max(0, val - 5));
                }}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
              />
            </div>
          </div>
        </div>

        {/* Template Selector */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Template
          </label>
          <div className="grid grid-cols-3 gap-3">
            {['vertical', 'square', 'landscape'].map((t) => (
              <button
                key={t}
                onClick={() => setTemplate(t)}
                className={`p-3 rounded-lg border-2 text-center transition-all ${
                  template === t
                    ? 'border-indigo-500 bg-indigo-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="text-sm font-medium capitalize">{t}</div>
                <div className="text-xs text-gray-500 mt-1">
                  {t === 'vertical' && '9:16 (Reels/Shorts/TikTok)'}
                  {t === 'square' && '1:1 (Instagram Feed)'}
                  {t === 'landscape' && '16:9 (YouTube)'}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Quick Select from Transcription */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Quick Select from Transcription
          </label>
          <div className="max-h-40 overflow-y-auto divide-y divide-gray-100">
            {transcriptionJob.segments?.slice(0, 10).map((segment: any, index: number) => (
              <button
                key={index}
                onClick={() => handleSegmentClick(segment)}
                className="w-full px-3 py-2 text-left hover:bg-gray-50 transition-colors flex justify-between items-center"
              >
                <span className="text-sm text-gray-900 truncate pr-2">{segment.text}</span>
                <span className="text-xs text-gray-500 font-mono shrink-0">
                  {formatTime(segment.start)}-{formatTime(segment.end)}
                </span>
              </button>
            ))}
          </div>
        </div>

        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}

        <button
          onClick={handleCreateClip}
          disabled={loading}
          className="w-full py-3 px-4 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Generating Clip...' : 'Create Clip'}
        </button>

        {clipJob && clipJob.status === 'completed' && (
          <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
            <p className="text-green-700 font-medium">Clip created successfully!</p>
            <a
              href={clipJob.output_path}
              target="_blank"
              rel="noopener noreferrer"
              className="text-green-600 text-sm underline mt-1 inline-block"
            >
              Download Clip
            </a>
          </div>
        )}
      </div>
    </div>
  );
};

const formatTime = (seconds: number): string => {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};

export default ClipPlayer;
import React from 'react';

interface TranscriptionViewProps {
  job: any;
}

const TranscriptionView: React.FC<TranscriptionViewProps> = ({ job }) => {
  const segments = job.segments || [];

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900">Transcription</h3>
        <p className="text-sm text-gray-500 mt-1">
          Video ID: {job.video_id} • Duration: {job.duration?.toFixed(1)}s • Language: {job.language}
        </p>
      </div>

      <div className="divide-y divide-gray-100 max-h-96 overflow-y-auto">
        {segments.map((segment: any, index: number) => (
          <div
            key={index}
            className="px-6 py-3 hover:bg-gray-50 transition-colors cursor-pointer"
            onClick={() => console.log('Seek to:', segment.start)}
          >
            <div className="flex gap-4">
              <span className="text-sm text-gray-500 font-mono w-20 shrink-0">
                {formatTime(segment.start)} - {formatTime(segment.end)}
              </span>
              <span className="flex-1 text-gray-900">{segment.text}</span>
            </div>
          </div>
        ))}

        {segments.length === 0 && (
          <div className="px-6 py-12 text-center text-gray-500">
            No transcription segments available
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

export default TranscriptionView;
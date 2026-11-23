import React, { useState } from 'react';
import VideoInput from './components/VideoInput';
import TranscriptionView from './components/TranscriptionView';
import ClipPlayer from './components/ClipPlayer';
import ViralSuggestions from './components/ViralSuggestions';
import ProgressBar from './components/ProgressBar';

function App() {
  const [transcriptionJob, setTranscriptionJob] = useState<any>(null);
  const [clipJob, setClipJob] = useState<any>(null);
  const [viralSuggestions, setViralSuggestions] = useState<any[]>([]);
  const [activeTab, setActiveTab] = useState<'transcribe' | 'clips' | 'viral'>('transcribe');

  const handleTranscriptionComplete = (job: any) => {
    setTranscriptionJob(job);
    setActiveTab('clips');
  };

  const handleClipComplete = (job: any) => {
    setClipJob(job);
  };

  const handleViralSuggestions = (suggestions: any[]) => {
    setViralSuggestions(suggestions);
    setActiveTab('viral');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <h1 className="text-2xl font-bold text-gray-900">ClipGod</h1>
            <nav className="flex space-x-4">
              <button
                onClick={() => setActiveTab('transcribe')}
                className={`px-3 py-2 rounded-md text-sm font-medium ${
                  activeTab === 'transcribe'
                    ? 'bg-indigo-100 text-indigo-700'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                Transcribe
              </button>
              <button
                onClick={() => setActiveTab('clips')}
                className={`px-3 py-2 rounded-md text-sm font-medium ${
                  activeTab === 'clips'
                    ? 'bg-indigo-100 text-indigo-700'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
                disabled={!transcriptionJob}
              >
                Create Clips
              </button>
              <button
                onClick={() => setActiveTab('viral')}
                className={`px-3 py-2 rounded-md text-sm font-medium ${
                  activeTab === 'viral'
                    ? 'bg-indigo-100 text-indigo-700'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
                disabled={!transcriptionJob}
              >
                Viral Suggestions
              </button>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'transcribe' && (
          <VideoInput onComplete={handleTranscriptionComplete} />
        )}

        {activeTab === 'clips' && transcriptionJob && (
          <div className="space-y-8">
            <TranscriptionView job={transcriptionJob} />
            <ClipPlayer
              transcriptionJob={transcriptionJob}
              onComplete={handleClipComplete}
            />
          </div>
        )}

        {activeTab === 'viral' && transcriptionJob && (
          <ViralSuggestions
            transcriptionJob={transcriptionJob}
            suggestions={viralSuggestions}
            onSuggestions={handleViralSuggestions}
          />
        )}

        {!transcriptionJob && activeTab !== 'transcribe' && (
          <div className="text-center py-12">
            <p className="text-gray-500">Please transcribe a video first</p>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <p className="text-center text-sm text-gray-500">
            ClipGod - AI-powered video clipping made simple
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
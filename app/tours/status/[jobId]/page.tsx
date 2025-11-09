'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { CheckCircle2, Circle, Loader2, XCircle, Home } from 'lucide-react';

interface AgentStatus {
  name: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  icon: string;
  description: string;
  progress?: number;
}

export default function TourStatusPage() {
  const params = useParams();
  const router = useRouter();
  const jobId = params.jobId as string;

  const [agents, setAgents] = useState<AgentStatus[]>([
    { name: 'Tour Curator', status: 'pending', icon: '🎯', description: 'Selecting perfect locations for you' },
    { name: 'Route Optimizer', status: 'pending', icon: '🗺️', description: 'Calculating optimal walking route' },
    { name: 'Storyteller', status: 'pending', icon: '📖', description: 'Crafting engaging stories' },
    { name: 'Content Moderator', status: 'pending', icon: '✨', description: 'Ensuring quality content' },
    { name: 'Voice Synthesis', status: 'pending', icon: '🎙️', description: 'Generating audio narration' },
  ]);

  const [overallStatus, setOverallStatus] = useState<'processing' | 'completed' | 'failed'>('processing');
  const [tourId, setTourId] = useState<string | null>(null);
  const [estimatedTime, setEstimatedTime] = useState(60);

  useEffect(() => {
    const pollStatus = async () => {
      try {
        const response = await fetch(
          `https://tour-orchestrator-168041541697.europe-west1.run.app/tour-status/${jobId}`
        );
        const data = await response.json();

        if (data.success) {
          // Update agent statuses based on API response
          const updatedAgents = [...agents];

          const statusMapping: { [key: string]: number } = {
            'curator_running': 0,
            'optimizer_running': 1,
            'storyteller_running': 2,
            'moderator_running': 3,
            'voice_synthesis_running': 4,
          };

          // Mark all previous agents as completed
          const currentAgentIndex = statusMapping[data.status];
          if (currentAgentIndex !== undefined) {
            for (let i = 0; i < currentAgentIndex; i++) {
              updatedAgents[i].status = 'completed';
            }
            updatedAgents[currentAgentIndex].status = 'running';
          }

          if (data.status === 'completed') {
            updatedAgents.forEach((agent) => (agent.status = 'completed'));
            setOverallStatus('completed');
            setTourId(data.tour_id);
            setTimeout(() => {
              router.push(`/tours/${data.tour_id}`);
            }, 2000);
          } else if (data.status === 'failed') {
            if (currentAgentIndex !== undefined) {
              updatedAgents[currentAgentIndex].status = 'failed';
            }
            setOverallStatus('failed');
          }

          setAgents(updatedAgents);

          // Update estimated time
          const completed = updatedAgents.filter((a) => a.status === 'completed').length;
          const remaining = agents.length - completed;
          setEstimatedTime(remaining * 12);
        }
      } catch (error) {
        console.error('Error polling status:', error);
      }
    };

    const interval = setInterval(pollStatus, 2000);

    // Initial poll
    pollStatus();

    return () => clearInterval(interval);
  }, [jobId, router]);

  const getStatusIcon = (status: AgentStatus['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="h-6 w-6 text-green-600" />;
      case 'running':
        return <Loader2 className="h-6 w-6 text-orange-500 animate-spin" />;
      case 'failed':
        return <XCircle className="h-6 w-6 text-red-600" />;
      default:
        return <Circle className="h-6 w-6 text-gray-300" />;
    }
  };

  const completedCount = agents.filter((a) => a.status === 'completed').length;
  const overallProgress = (completedCount / agents.length) * 100;

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-amber-50 to-yellow-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-orange-500 to-rose-500 text-white py-8">
        <div className="max-w-4xl mx-auto px-4">
          <button
            onClick={() => router.push('/')}
            className="flex items-center gap-2 text-white/80 hover:text-white mb-4 transition-colors"
          >
            <Home className="h-5 w-5" />
            Back to Home
          </button>
          <h1 className="text-4xl font-bold mb-2">Creating Your Tour</h1>
          <p className="text-white/90 text-lg">
            Our AI agents are working together to craft your perfect tour experience
          </p>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Overall Progress Card */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold text-gray-900">
              {overallStatus === 'processing' && 'Processing...'}
              {overallStatus === 'completed' && '🎉 Tour Created Successfully!'}
              {overallStatus === 'failed' && '❌ Tour Creation Failed'}
            </h2>
            {overallStatus === 'processing' && (
              <div className="text-right">
                <div className="text-3xl font-bold text-orange-500">{completedCount}/{agents.length}</div>
                <div className="text-sm text-gray-500">Agents Complete</div>
              </div>
            )}
          </div>

          {/* Progress Bar */}
          <div className="mb-6">
            <div className="bg-gray-200 rounded-full h-4 overflow-hidden">
              <div
                className="bg-gradient-to-r from-orange-500 to-rose-500 h-full transition-all duration-500 ease-out"
                style={{ width: `${overallProgress}%` }}
              ></div>
            </div>
            <div className="flex justify-between mt-2 text-sm text-gray-600">
              <span>{Math.round(overallProgress)}% Complete</span>
              {overallStatus === 'processing' && (
                <span>Est. {estimatedTime}s remaining</span>
              )}
            </div>
          </div>

          {overallStatus === 'completed' && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <p className="text-green-800 font-medium">
                Redirecting to your tour in 2 seconds...
              </p>
            </div>
          )}

          {overallStatus === 'failed' && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-red-800 font-medium mb-2">
                Something went wrong during tour creation. Please try again.
              </p>
              <button
                onClick={() => router.push('/')}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                Go Back Home
              </button>
            </div>
          )}
        </div>

        {/* Agent Status Cards */}
        <div className="space-y-4">
          {agents.map((agent, index) => (
            <div
              key={index}
              className={`bg-white rounded-xl shadow-lg p-6 transition-all ${
                agent.status === 'running' ? 'ring-2 ring-orange-600 ring-offset-2' : ''
              }`}
            >
              <div className="flex items-start gap-4">
                {/* Icon */}
                <div className="flex-shrink-0">
                  <div className="w-16 h-16 bg-gradient-to-br from-orange-100 to-amber-100 rounded-xl flex items-center justify-center text-3xl">
                    {agent.icon}
                  </div>
                </div>

                {/* Content */}
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-xl font-bold text-gray-900">{agent.name}</h3>
                    {getStatusIcon(agent.status)}
                  </div>
                  <p className="text-gray-600 mb-2">{agent.description}</p>

                  {/* Status Message */}
                  <div className="flex items-center gap-2">
                    {agent.status === 'completed' && (
                      <span className="text-sm text-green-600 font-medium">✓ Completed</span>
                    )}
                    {agent.status === 'running' && (
                      <span className="text-sm text-orange-500 font-medium animate-pulse">
                        ● Working now...
                      </span>
                    )}
                    {agent.status === 'pending' && (
                      <span className="text-sm text-gray-400 font-medium">○ Waiting</span>
                    )}
                    {agent.status === 'failed' && (
                      <span className="text-sm text-red-600 font-medium">✗ Failed</span>
                    )}
                  </div>
                </div>

                {/* Step Number */}
                <div className="text-right">
                  <div className="text-gray-400 text-sm">Step</div>
                  <div className="text-2xl font-bold text-gray-300">{index + 1}</div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Fun Facts Section */}
        {overallStatus === 'processing' && (
          <div className="mt-8 bg-gradient-to-r from-orange-500 to-rose-500 rounded-2xl p-6 text-white">
            <h3 className="font-bold text-xl mb-2">💡 Did you know?</h3>
            <p className="text-white/90">
              Our AI agents process over 50+ data points per location to create personalized tours
              just for you. Each story is crafted to be exactly 90 seconds long!
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

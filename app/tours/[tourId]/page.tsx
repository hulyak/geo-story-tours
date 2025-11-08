'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { MapPin, Clock, Music, ChevronLeft, ChevronRight, Play, Pause, Download, Navigation } from 'lucide-react';
import dynamic from 'next/dynamic';
import { exportTour } from '../../utils/tourExport';
import { optimizeRoute, calculateTotalDistance, formatDistance, estimateWalkingTime } from '../../utils/routeOptimization';

// Dynamically import the map component (client-side only)
const TourMap = dynamic(() => import('../../components/TourMap'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-full flex items-center justify-center bg-gray-100 rounded-xl">
      <div className="text-center">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-purple-600 border-t-transparent"></div>
        <p className="mt-2 text-gray-600 text-sm">Loading map...</p>
      </div>
    </div>
  ),
});

export default function TourDetailPage() {
  const params = useParams();
  const router = useRouter();
  const tourId = params.tourId as string;

  const [tour, setTour] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [currentStop, setCurrentStop] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isOptimized, setIsOptimized] = useState(false);
  const [originalLocations, setOriginalLocations] = useState<any[]>([]);

  useEffect(() => {
    fetchTour();
  }, [tourId]);

  const fetchTour = async () => {
    try {
      const response = await fetch(`https://tour-orchestrator-168041541697.europe-west1.run.app/tours/${tourId}`);
      const data = await response.json();

      if (data.success) {
        setTour(data.tour);
        // Save original locations for restoration
        if (data.tour.locations) {
          setOriginalLocations([...data.tour.locations]);
        }
      }
    } catch (error) {
      console.error('Error fetching tour:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePlayAudio = () => {
    // Toggle audio playback
    setIsPlaying(!isPlaying);
    // TODO: Implement actual audio playback when audio URLs are available
  };

  const handleExport = (format: 'gpx' | 'kml') => {
    if (tour && tour.locations) {
      exportTour(tour.locations, `Tour ${tourId}`, format);
    }
  };

  const handleOptimizeRoute = () => {
    if (!tour || !tour.locations) return;

    if (isOptimized) {
      // Restore original route
      setTour({ ...tour, locations: [...originalLocations] });
      setIsOptimized(false);
      setCurrentStop(0);
    } else {
      // Optimize route
      const optimizedLocations = optimizeRoute(tour.locations);
      setTour({ ...tour, locations: optimizedLocations });
      setIsOptimized(true);
      setCurrentStop(0);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-16 w-16 border-4 border-purple-600 border-t-transparent"></div>
          <p className="mt-4 text-gray-600 text-lg">Loading your tour...</p>
        </div>
      </div>
    );
  }

  if (!tour) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Tour not found</h1>
          <button
            onClick={() => router.push('/')}
            className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
          >
            Back to Home
          </button>
        </div>
      </div>
    );
  }

  const currentLocation = tour.locations?.[currentStop];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white py-6">
        <div className="max-w-7xl mx-auto px-4">
          <button
            onClick={() => router.push('/')}
            className="flex items-center gap-2 text-white/80 hover:text-white mb-4"
          >
            <ChevronLeft className="h-5 w-5" />
            Back to Home
          </button>
          <h1 className="text-3xl font-bold mb-2">Your Personalized Tour</h1>
          <div className="flex gap-6 text-white/90">
            <div className="flex items-center gap-2">
              <Clock className="h-5 w-5" />
              <span>{tour.duration} minutes</span>
            </div>
            <div className="flex items-center gap-2">
              <MapPin className="h-5 w-5" />
              <span>{tour.locations?.length || 0} stops</span>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-2 gap-8">
          {/* Map Section */}
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-2xl font-bold text-gray-900">Tour Map</h2>

              {/* Action Buttons */}
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={handleOptimizeRoute}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors flex items-center gap-2 ${
                    isOptimized
                      ? 'bg-orange-600 text-white hover:bg-orange-700'
                      : 'bg-purple-600 text-white hover:bg-purple-700'
                  }`}
                  title={isOptimized ? 'Restore original route' : 'Optimize route for shortest distance'}
                >
                  <Navigation className="h-4 w-4" />
                  <span className="hidden sm:inline">{isOptimized ? 'Restore' : 'Optimize'}</span>
                </button>
                <button
                  type="button"
                  onClick={() => handleExport('gpx')}
                  className="px-3 py-1.5 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700 transition-colors flex items-center gap-2"
                  title="Export as GPX for GPS devices"
                >
                  <Download className="h-4 w-4" />
                  <span className="hidden sm:inline">GPX</span>
                </button>
                <button
                  type="button"
                  onClick={() => handleExport('kml')}
                  className="px-3 py-1.5 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors flex items-center gap-2"
                  title="Export as KML for Google Earth"
                >
                  <Download className="h-4 w-4" />
                  <span className="hidden sm:inline">KML</span>
                </button>
              </div>
            </div>

            {/* Route Distance Info */}
            {tour.locations && tour.locations.length > 1 && (
              <div className={`mb-4 p-3 rounded-lg ${isOptimized ? 'bg-green-50 border border-green-200' : 'bg-blue-50 border border-blue-200'}`}>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      Total Walking Distance: {formatDistance(calculateTotalDistance(tour.locations))}
                    </p>
                    <p className="text-xs text-gray-600 mt-1">
                      Estimated time: {estimateWalkingTime(calculateTotalDistance(tour.locations))} (walking only)
                    </p>
                  </div>
                  {isOptimized && (
                    <span className="text-green-700 text-xs font-medium bg-green-100 px-2 py-1 rounded">
                      Optimized
                    </span>
                  )}
                </div>
              </div>
            )}

            <div className="rounded-xl h-96 overflow-hidden">
              <TourMap
                locations={tour.locations || []}
                currentStop={currentStop}
                onMarkerClick={(index) => setCurrentStop(index)}
              />
            </div>

            {/* Location List */}
            <div className="mt-6">
              <h3 className="font-bold text-gray-900 mb-3">All Stops</h3>
              <div className="space-y-2">
                {tour.locations?.map((location: any, index: number) => (
                  <button
                    key={location.id}
                    type="button"
                    onClick={() => setCurrentStop(index)}
                    className={`w-full text-left p-3 rounded-lg transition-all ${
                      currentStop === index
                        ? 'bg-purple-100 border-2 border-purple-600'
                        : 'bg-gray-50 hover:bg-gray-100'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                        currentStop === index ? 'bg-purple-600 text-white' : 'bg-gray-300 text-gray-600'
                      }`}>
                        {index + 1}
                      </div>
                      <div className="flex-1">
                        <p className="font-medium text-gray-900">{location.name}</p>
                        <p className="text-sm text-gray-500">{location.average_visit_minutes} min</p>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Current Stop Details */}
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-2xl font-bold text-gray-900">
                Stop {currentStop + 1} of {tour.locations?.length || 0}
              </h2>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => setCurrentStop(Math.max(0, currentStop - 1))}
                  disabled={currentStop === 0}
                  className="p-2 rounded-lg bg-gray-100 hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
                  title="Previous stop"
                >
                  <ChevronLeft className="h-5 w-5" />
                </button>
                <button
                  type="button"
                  onClick={() => setCurrentStop(Math.min((tour.locations?.length || 1) - 1, currentStop + 1))}
                  disabled={currentStop === (tour.locations?.length || 1) - 1}
                  className="p-2 rounded-lg bg-gray-100 hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
                  title="Next stop"
                >
                  <ChevronRight className="h-5 w-5" />
                </button>
              </div>
            </div>

            {currentLocation && (
              <>
                <h3 className="text-2xl font-bold text-purple-600 mb-4">
                  {currentLocation.name}
                </h3>

                <div className="mb-6">
                  <div className="flex gap-2 flex-wrap mb-4">
                    {currentLocation.categories?.map((cat: string) => (
                      <span
                        key={cat}
                        className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm font-medium"
                      >
                        {cat}
                      </span>
                    ))}
                  </div>

                  <div className="flex gap-4 text-gray-600 mb-4">
                    <div className="flex items-center gap-2">
                      <Clock className="h-5 w-5 text-blue-600" />
                      <span>{currentLocation.average_visit_minutes} min visit</span>
                    </div>
                    {currentLocation.coordinates && (
                      <div className="flex items-center gap-2">
                        <MapPin className="h-5 w-5 text-purple-600" />
                        <span className="text-sm">
                          {currentLocation.city || 'New York'}, {currentLocation.country || 'USA'}
                        </span>
                      </div>
                    )}
                  </div>
                </div>

                <div className="mb-6">
                  <h4 className="font-bold text-gray-900 mb-2">Description</h4>
                  <p className="text-gray-700 leading-relaxed">
                    {currentLocation.description}
                  </p>
                </div>

                {currentLocation.story && (
                  <div className="mb-6">
                    <h4 className="font-bold text-gray-900 mb-2">Story</h4>
                    <div className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-lg p-4">
                      <p className="text-gray-700 leading-relaxed">
                        {currentLocation.story}
                      </p>
                    </div>
                  </div>
                )}

                {/* Audio Player */}
                <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg p-6 text-white">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <Music className="h-6 w-6" />
                      <div>
                        <p className="font-bold">Audio Guide</p>
                        <p className="text-sm text-white/80">AI-generated narration</p>
                      </div>
                    </div>
                    <button
                      type="button"
                      onClick={handlePlayAudio}
                      className="w-12 h-12 rounded-full bg-white/20 hover:bg-white/30 flex items-center justify-center transition-all"
                    >
                      {isPlaying ? (
                        <Pause className="h-6 w-6" />
                      ) : (
                        <Play className="h-6 w-6 ml-1" />
                      )}
                    </button>
                  </div>
                  <div className="bg-white/20 rounded-full h-2">
                    <div className="bg-white rounded-full h-2 w-0"></div>
                  </div>
                  <p className="text-sm text-white/80 mt-2">
                    {currentLocation.audio_url ? 'Ready to play' : 'Audio processing...'}
                  </p>
                </div>

                {/* Directions */}
                {currentLocation.coordinates && (
                  <div className="mt-6">
                    <a
                      href={`https://www.google.com/maps/search/?api=1&query=${currentLocation.coordinates.lat},${currentLocation.coordinates.lng}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="w-full px-6 py-3 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 transition-all flex items-center justify-center gap-2"
                    >
                      <MapPin className="h-5 w-5" />
                      Get Directions
                    </a>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

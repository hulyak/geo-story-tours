'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { MapPin, Clock, Star, TrendingUp, X } from 'lucide-react';
import AnalyticsDashboard from './components/AnalyticsDashboard';

export default function Home() {
  const router = useRouter();
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [locations, setLocations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedLocation, setSelectedLocation] = useState<any>(null);

  const categories = ['all', 'history', 'food', 'art', 'hidden gems'];

  useEffect(() => {
    fetchLocations();
  }, []);

  const fetchLocations = async () => {
    try {
      const response = await fetch('/api/locations');
      const data = await response.json();

      if (data.locations) {
        setLocations(data.locations);
      }
    } catch (error) {
      console.error('Error fetching locations:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleExplore = () => {
    const element = document.getElementById('locations');
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  const [creatingTour, setCreatingTour] = useState(false);

  const handleCreateTour = async () => {
    setCreatingTour(true);

    try {
      // Call async endpoint
      const response = await fetch('https://tour-orchestrator-168041541697.europe-west1.run.app/create-tour-async', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          interests: [selectedCategory === 'all' ? 'history' : selectedCategory],
          duration: 30
        })
      });

      const data = await response.json();

      if (data.success && data.job_id) {
        // Redirect to status page (it handles all polling)
        router.push(`/tours/status/${data.job_id}`);
      } else {
        setCreatingTour(false);
        alert('Error creating tour. Please try again.');
      }
    } catch (error) {
      console.error('Error creating tour:', error);
      setCreatingTour(false);
      alert('Error creating tour. Please try again.');
    }
  };

  const filteredLocations = selectedCategory === 'all'
    ? locations
    : locations.filter((loc: any) => loc.categories.includes(selectedCategory));

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <div className="relative bg-gradient-to-br from-purple-600 via-blue-600 to-cyan-500 overflow-hidden">
        <div className="absolute inset-0 bg-black opacity-10"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 md:py-32">
          <div className="text-center text-white">
            <div className="inline-flex items-center px-4 py-2 bg-white/20 backdrop-blur-sm rounded-full mb-6">
              <TrendingUp className="h-4 w-4 mr-2" />
              <span className="text-sm font-medium">AI-Powered Tour Platform</span>
            </div>
            <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
              Discover Cities Through<br />
              <span className="text-yellow-300">90-Second Stories</span>
            </h1>
            <p className="text-xl md:text-2xl mb-10 text-blue-100 max-w-3xl mx-auto">
              Explore hidden gems with AI-generated micro-tours. Each location comes alive with personalized storytelling.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button
                onClick={handleExplore}
                className="px-8 py-4 bg-white text-purple-600 rounded-xl font-semibold text-lg hover:bg-gray-100 transition-all transform hover:scale-105 shadow-xl"
              >
                Explore {locations.length} Locations
              </button>
              <button
                onClick={handleCreateTour}
                disabled={creatingTour}
                className="px-8 py-4 bg-purple-500/30 backdrop-blur-sm text-white rounded-xl font-semibold text-lg hover:bg-purple-500/50 transition-all transform hover:scale-105 border-2 border-white/50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {creatingTour ? '🤖 AI Agents Working...' : 'Create Your Tour'}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 -mt-16 relative z-10">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-2xl p-8 shadow-xl text-center">
            <div className="text-5xl font-bold text-purple-600 mb-2">{locations.length}</div>
            <div className="text-gray-600 font-medium">Curated Locations</div>
          </div>
          <div className="bg-white rounded-2xl p-8 shadow-xl text-center">
            <div className="text-5xl font-bold text-blue-600 mb-2">5</div>
            <div className="text-gray-600 font-medium">AI Agents Working</div>
          </div>
          <div className="bg-white rounded-2xl p-8 shadow-xl text-center">
            <div className="flex justify-center items-baseline mb-2">
              <div className="text-5xl font-bold text-cyan-600">90</div>
              <div className="text-2xl font-bold text-gray-400 ml-1">sec</div>
            </div>
            <div className="text-gray-600 font-medium">Story Duration</div>
          </div>
        </div>
      </div>

      {/* Category Filter */}
      <div id="locations" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center mb-10">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">Browse Locations</h2>
          <p className="text-xl text-gray-600">Filter by what interests you most</p>
        </div>
        <div className="flex gap-3 justify-center flex-wrap mb-12">
          {categories.map((category) => (
            <button
              key={category}
              onClick={() => setSelectedCategory(category)}
              className={`px-6 py-3 rounded-xl font-medium transition-all transform hover:scale-105 ${
                selectedCategory === category
                  ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-lg'
                  : 'bg-white text-gray-700 hover:bg-gray-100 shadow'
              }`}
            >
              {category.charAt(0).toUpperCase() + category.slice(1)}
            </button>
          ))}
        </div>

        {/* Locations Grid */}
        {loading ? (
          <div className="text-center py-20">
            <div className="inline-block animate-spin rounded-full h-16 w-16 border-4 border-purple-600 border-t-transparent"></div>
            <p className="mt-6 text-gray-600 text-lg">Loading amazing locations...</p>
          </div>
        ) : filteredLocations.length === 0 ? (
          <div className="text-center py-20">
            <p className="text-gray-600 text-xl">No locations found for this category.</p>
          </div>
        ) : (
          <>
            <div className="mb-6 text-gray-600">
              Showing <span className="font-bold text-purple-600">{filteredLocations.length}</span> location{filteredLocations.length !== 1 ? 's' : ''}
            </div>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
              {filteredLocations.map((location: any) => (
                <div
                  key={location.id}
                  onClick={() => setSelectedLocation(location)}
                  className="bg-white rounded-2xl shadow-lg overflow-hidden hover:shadow-2xl transition-all transform hover:-translate-y-2 cursor-pointer group"
                >
                  <div className="relative h-56 overflow-hidden">
                    <div
                      className="h-full bg-cover bg-center transform group-hover:scale-110 transition-transform duration-500"
                      style={{ backgroundImage: `url(${location.image_url})` }}
                    />
                    <div className="absolute top-4 left-4">
                      <span className="px-3 py-1.5 bg-white/95 backdrop-blur-sm text-purple-600 rounded-full text-sm font-semibold shadow-lg">
                        {location.categories[0]}
                      </span>
                    </div>
                    <div className="absolute top-4 right-4">
                      <div className="flex items-center gap-1 px-3 py-1.5 bg-white/95 backdrop-blur-sm rounded-full text-sm font-medium shadow-lg">
                        <Clock className="h-4 w-4 text-blue-600" />
                        <span className="text-gray-700">{location.average_visit_minutes} min</span>
                      </div>
                    </div>
                  </div>
                  <div className="p-6">
                    <h3 className="text-2xl font-bold mb-3 text-gray-900 group-hover:text-purple-600 transition-colors">
                      {location.name}
                    </h3>
                    <p className="text-gray-600 mb-4 line-clamp-3 leading-relaxed">
                      {location.description}
                    </p>
                    <div className="flex gap-2 flex-wrap">
                      {location.categories.slice(0, 3).map((cat: string) => (
                        <span
                          key={cat}
                          className="text-xs px-3 py-1 bg-gradient-to-r from-purple-100 to-blue-100 text-purple-700 rounded-full font-medium"
                        >
                          {cat}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
      </div>

      {/* Location Detail Modal */}
      {selectedLocation && (
        <div
          className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          onClick={() => setSelectedLocation(null)}
        >
          <div
            className="bg-white rounded-3xl max-w-3xl w-full max-h-[90vh] overflow-y-auto shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header with Image */}
            <div className="relative h-80 overflow-hidden rounded-t-3xl">
              <div
                className="h-full bg-cover bg-center"
                style={{ backgroundImage: `url(${selectedLocation.image_url})` }}
              />
              <button
                onClick={() => setSelectedLocation(null)}
                className="absolute top-4 right-4 p-2 bg-white/95 backdrop-blur-sm rounded-full hover:bg-white transition-all shadow-lg"
              >
                <X className="h-6 w-6 text-gray-700" />
              </button>
              <div className="absolute top-4 left-4">
                <span className="px-4 py-2 bg-white/95 backdrop-blur-sm text-purple-600 rounded-full text-sm font-bold shadow-lg">
                  {selectedLocation.categories[0]}
                </span>
              </div>
            </div>

            {/* Modal Content */}
            <div className="p-8">
              <h2 className="text-4xl font-bold text-gray-900 mb-4">
                {selectedLocation.name}
              </h2>

              {/* Location Info Grid */}
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="flex items-center gap-2 text-gray-600">
                  <Clock className="h-5 w-5 text-blue-600" />
                  <span className="font-medium">{selectedLocation.average_visit_minutes} min visit</span>
                </div>
                {(selectedLocation.city || selectedLocation.country) && (
                  <div className="flex items-center gap-2 text-gray-600">
                    <MapPin className="h-5 w-5 text-purple-600" />
                    <span className="font-medium">
                      {selectedLocation.city || 'New York'}, {selectedLocation.country || 'USA'}
                    </span>
                  </div>
                )}
              </div>

              {/* Description */}
              <div className="mb-6">
                <h3 className="text-xl font-bold text-gray-900 mb-3">About This Location</h3>
                <p className="text-gray-700 leading-relaxed text-lg">
                  {selectedLocation.description}
                </p>
              </div>

              {/* Categories */}
              <div className="mb-6">
                <h3 className="text-xl font-bold text-gray-900 mb-3">Categories</h3>
                <div className="flex gap-2 flex-wrap">
                  {selectedLocation.categories.map((cat: string) => (
                    <span
                      key={cat}
                      className="px-4 py-2 bg-gradient-to-r from-purple-100 to-blue-100 text-purple-700 rounded-full font-medium"
                    >
                      {cat}
                    </span>
                  ))}
                </div>
              </div>

              {/* Map Link */}
              {selectedLocation.coordinates && (
                <div className="border-t pt-6">
                  <a
                    href={`https://www.google.com/maps/search/?api=1&query=${selectedLocation.coordinates.lat},${selectedLocation.coordinates.lng}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-xl font-semibold hover:shadow-lg transition-all transform hover:scale-105"
                  >
                    <MapPin className="h-5 w-5" />
                    View on Google Maps
                  </a>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Analytics Dashboard */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <AnalyticsDashboard />
      </div>

      {/* AI Features Section */}
      <div className="bg-gradient-to-br from-gray-900 via-purple-900 to-blue-900 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-5xl font-bold mb-4">Powered by Multi-Agent AI</h2>
            <p className="text-xl text-purple-200">Five intelligent agents collaborate to create your perfect tour</p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-5 gap-6">
            {[
              { title: 'Tour Curator', desc: 'Selects locations based on your interests', icon: '🎯' },
              { title: 'Route Optimizer', desc: 'Calculates the most efficient walking path', icon: '🗺️' },
              { title: 'Storyteller', desc: 'Generates engaging 90-second narratives', icon: '📖' },
              { title: 'Content Moderator', desc: 'Ensures quality and accuracy', icon: '✨' },
              { title: 'Voice Synthesis', desc: 'Creates high-quality audio with GPU', icon: '🎙️' }
            ].map((agent, idx) => (
              <div key={idx} className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 text-center hover:bg-white/20 transition-all">
                <div className="text-5xl mb-4">{agent.icon}</div>
                <h3 className="font-bold text-xl mb-2">{agent.title}</h3>
                <p className="text-purple-200">{agent.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-gray-400">
            Built with Google ADK, Gemini 2.0 Flash, Cloud Run & Firestore
          </p>
          <p className="text-gray-500 mt-2">Cloud Run Hackathon 2025 - AI Agents Category</p>
        </div>
      </div>
    </div>
  );
}

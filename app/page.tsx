'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { MapPin, Clock, Star, TrendingUp, X, Search, Users, Award, Heart, Share2 } from 'lucide-react';
import AnalyticsDashboard from './components/AnalyticsDashboard';

export default function Home() {
  const router = useRouter();
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [locations, setLocations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedLocation, setSelectedLocation] = useState<any>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [favorites, setFavorites] = useState<string[]>([]);
  const [selectedForTour, setSelectedForTour] = useState<any[]>([]);
  const [selectedCity, setSelectedCity] = useState<'paris' | 'newyork'>('paris');

  const categories = ['all', 'history', 'food', 'art', 'hidden gems', 'architecture', 'landmarks'];

  // Helper function to determine if coordinates are in Paris or New York
  const getLocationCity = (coords: any): 'paris' | 'newyork' | null => {
    if (!coords || !coords.lat || !coords.lng) return null;
    const lat = coords.lat;
    const lng = coords.lng;

    // Paris bounds (approximate)
    if (lat >= 48.8 && lat <= 48.9 && lng >= 2.2 && lng <= 2.5) {
      return 'paris';
    }
    // New York bounds (approximate)
    if (lat >= 40.6 && lat <= 40.9 && lng >= -74.1 && lng <= -73.9) {
      return 'newyork';
    }
    return null;
  };

  useEffect(() => {
    fetchLocations();
    // Load favorites from localStorage
    const savedFavorites = localStorage.getItem('favorites');
    if (savedFavorites) {
      setFavorites(JSON.parse(savedFavorites));
    }
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

  const toggleFavorite = (locationId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    const newFavorites = favorites.includes(locationId)
      ? favorites.filter(id => id !== locationId)
      : [...favorites, locationId];
    setFavorites(newFavorites);
    localStorage.setItem('favorites', JSON.stringify(newFavorites));
  };

  const handleShare = async (location: any, e: React.MouseEvent) => {
    e.stopPropagation();
    const shareData = {
      title: location.name,
      text: location.description,
      url: window.location.href
    };

    try {
      if (navigator.share) {
        await navigator.share(shareData);
      } else {
        // Fallback: copy to clipboard
        await navigator.clipboard.writeText(`${location.name}\n${location.description}\n${window.location.href}`);
        alert('Link copied to clipboard!');
      }
    } catch (err) {
      console.error('Error sharing:', err);
    }
  };

  const handleSearch = (value: string) => {
    setSearchQuery(value);
    // Only auto-scroll once when user starts typing (3+ characters)
    if (value.length === 3 && searchQuery.length === 2) {
      setTimeout(() => {
        const element = document.getElementById('locations');
        if (element) {
          element.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }, 100);
    }
  };

  const [creatingTour, setCreatingTour] = useState(false);
  const [userLocation, setUserLocation] = useState<{lat: number, lng: number} | null>(null);

  // Set user location based on selected city
  useEffect(() => {
    if (selectedCity === 'paris') {
      setUserLocation({ lat: 48.8566, lng: 2.3522 }); // Paris center
    } else {
      setUserLocation({ lat: 40.7589, lng: -73.9851 }); // Times Square, NYC
    }
  }, [selectedCity]);

  const addToTour = (location: any) => {
    if (!selectedForTour.find(loc => loc.id === location.id)) {
      setSelectedForTour([...selectedForTour, location]);
    }
  };

  const removeFromTour = (locationId: string) => {
    setSelectedForTour(selectedForTour.filter(loc => loc.id !== locationId));
  };

  const handleCreateTour = async (interests?: string[], useSelectedLocations: boolean = false) => {
    setCreatingTour(true);

    try {
      // Ensure we have user location
      if (!userLocation) {
        alert('Please enable location services to create a personalized tour in your area.');
        setCreatingTour(false);
        return;
      }

      // Build request body
      const requestBody: any = {
        interests: interests || [selectedCategory === 'all' ? 'history' : selectedCategory],
        duration: 30,
        latitude: userLocation.lat,
        longitude: userLocation.lng
      };

      // If using selected locations, include their IDs
      if (useSelectedLocations && selectedForTour.length > 0) {
        requestBody.location_ids = selectedForTour.map(loc => loc.id);
      }

      // Create AbortController for timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 60000); // 60 second timeout

      const response = await fetch('https://tour-orchestrator-168041541697.europe-west1.run.app/create-tour-async', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();

      if (data.success && data.job_id) {
        // Clear selected locations
        if (useSelectedLocations) {
          setSelectedForTour([]);
        }
        router.push(`/tours/status/${data.job_id}`);
      } else {
        setCreatingTour(false);
        alert('Error creating tour: ' + (data.message || 'Unknown error. Please try again.'));
      }
    } catch (error) {
      console.error('Error creating tour:', error);
      setCreatingTour(false);

      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          alert('Request timed out. The service might be starting up. Please try again in a moment.');
        } else {
          alert('Error creating tour: ' + error.message + '. Please try again.');
        }
      } else {
        alert('Error creating tour. Please try again.');
      }
    }
  };

  const filteredLocations = locations.filter((loc: any) => {
    const matchesCategory = selectedCategory === 'all' || loc.categories.includes(selectedCategory);
    const matchesSearch = !searchQuery ||
      loc.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      loc.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation Bar */}
      <nav className="sticky top-0 z-40 bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <div className="w-10 h-10 bg-gradient-to-br from-orange-500 to-rose-500 rounded-xl flex items-center justify-center shadow-lg">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-6 w-6 text-white">
                  <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/>
                  <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>
                </svg>
              </div>
              <span className="text-2xl font-bold bg-gradient-to-r from-orange-500 to-rose-500 bg-clip-text text-transparent">
                PocketGuide
              </span>
            </div>
            <div className="hidden md:flex items-center gap-6">
              <a href="#locations" className="text-gray-700 hover:text-orange-500 font-medium transition">Explore</a>
              <a href="#how-it-works" className="text-gray-700 hover:text-orange-500 font-medium transition">How it Works</a>
              <button
                onClick={() => handleCreateTour()}
                className="px-6 py-2.5 bg-gradient-to-r from-orange-500 to-rose-500 text-white rounded-lg font-semibold hover:shadow-lg transition-all"
              >
                Create Tour
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section with Search */}
      <div className="relative bg-gradient-to-br from-orange-50 via-amber-50 to-yellow-50 overflow-hidden min-h-screen flex items-center">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiM1YjIxYjYiIGZpbGwtb3BhY2l0eT0iMC4wNSI+PHBhdGggZD0iTTM2IDE2YzAtMyAzLTYgNi02czYgMyA2IDYtMyA2LTYgNi02LTMtNi02em0wIDI4YzAtMyAzLTYgNi02czYgMyA2IDYtMyA2LTYgNi02LTMtNi02ek0xNiA0NGMtMy0wLTYtMy02LTZzMy02IDYtNiA2IDMgNiA2LTMgNi02IDZ6bTAtMjhjLTMtMC02LTMtNi02czMtNiA2LTYgNiAzIDYgNi0zIDYtNiA2eiIvPjwvZz48L2c+PC9zdmc+')] opacity-40"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 w-full">
          <div className="text-center mb-12">
            <div className="inline-flex items-center px-4 py-2 bg-orange-100 text-orange-700 rounded-full mb-6">
              <Award className="h-4 w-4 mr-2" />
              <span className="text-sm font-semibold">Powered by 5 AI Agents</span>
            </div>
            <h1 className="text-5xl md:text-7xl font-bold mb-6 text-gray-900 leading-tight">
              Discover Cities Through
              <br />
              <span className="bg-gradient-to-r from-orange-500 via-rose-500 to-pink-500 bg-clip-text text-transparent">
                90-Second Stories
              </span>
            </h1>
            <p className="text-xl md:text-2xl mb-12 text-gray-600 max-w-3xl mx-auto leading-relaxed">
              AI-powered micro-tours that bring every location to life with personalized storytelling
            </p>

            {/* Search Bar */}
            <div className="max-w-3xl mx-auto mb-8">
              <div className="relative">
                <Search className="absolute left-6 top-1/2 transform -translate-y-1/2 h-6 w-6 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search our curated locations..."
                  value={searchQuery}
                  onChange={(e) => handleSearch(e.target.value)}
                  className="w-full pl-16 pr-6 py-5 text-lg text-gray-900 placeholder-gray-400 rounded-2xl border-2 border-gray-200 focus:border-orange-400 focus:ring-4 focus:ring-orange-100 transition-all outline-none shadow-lg bg-white"
                />
              </div>
              <p className="text-center text-sm text-gray-500 mt-3">
                {locations.length} handpicked Paris locations with AI-generated stories
              </p>
            </div>

            {/* Quick Stats */}
            <div className="flex flex-wrap justify-center gap-8 text-sm">
              <div className="flex items-center gap-2 text-gray-600">
                <Users className="h-5 w-5 text-orange-500" />
                <span className="font-medium">10,000+ Tours Created</span>
              </div>
              <div className="flex items-center gap-2 text-gray-600">
                <Star className="h-5 w-5 text-yellow-500 fill-yellow-500" />
                <span className="font-medium">4.9/5 Average Rating</span>
              </div>
              <div className="flex items-center gap-2 text-gray-600">
                <MapPin className="h-5 w-5 text-blue-600" />
                <span className="font-medium">{locations.length} Locations</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Featured Tours Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h2 className="text-3xl font-bold text-gray-900 mb-2">Popular Tours</h2>
            <p className="text-gray-600">Hand-picked by our AI curator</p>
          </div>
          <button
            onClick={() => handleCreateTour(['history', 'art'])}
            disabled={creatingTour}
            className="px-6 py-3 bg-orange-500 text-white rounded-xl font-semibold hover:bg-orange-600 transition-all disabled:opacity-50"
          >
            {creatingTour ? 'Creating...' : 'Create Custom Tour'}
          </button>
        </div>
        <div className="grid md:grid-cols-3 gap-6">
          {[
            { title: 'Historic Paris', duration: '2-3 hours', locations: 8, icon: '🏛️', interests: ['history', 'architecture'] },
            { title: 'Art & Culture', duration: '1-2 hours', locations: 6, icon: '🎨', interests: ['art', 'museums'] },
            { title: 'Hidden Gems', duration: '2 hours', locations: 7, icon: '💎', interests: ['hidden gems', 'neighborhoods'] }
          ].map((tour, idx) => (
            <button
              key={idx}
              onClick={() => handleCreateTour(tour.interests)}
              disabled={creatingTour}
              className="text-left bg-gradient-to-br from-orange-50 to-amber-50 p-6 rounded-2xl border-2 border-orange-100 hover:border-orange-300 transition-all hover:shadow-lg group disabled:opacity-50"
            >
              <div className="text-4xl mb-3">{tour.icon}</div>
              <h3 className="text-xl font-bold text-gray-900 mb-2 group-hover:text-orange-500 transition">
                {tour.title}
              </h3>
              <div className="flex gap-4 text-sm text-gray-600 mb-3">
                <span className="flex items-center gap-1">
                  <Clock className="h-4 w-4" />
                  {tour.duration}
                </span>
                <span className="flex items-center gap-1">
                  <MapPin className="h-4 w-4" />
                  {tour.locations} stops
                </span>
              </div>
              <div className="flex items-center gap-1 text-sm">
                <Star className="h-4 w-4 text-yellow-500 fill-yellow-500" />
                <span className="font-semibold text-gray-900">4.9</span>
                <span className="text-gray-500">(234 reviews)</span>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Category Filter */}
      <div id="locations" className="bg-gray-50 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-10">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">Browse All Locations</h2>
            <p className="text-xl text-gray-600">Explore by category</p>
          </div>

          {/* City Badge - Paris Only */}
          <div className="flex gap-4 justify-center mb-8">
            <div className="px-8 py-4 rounded-2xl font-bold text-lg bg-gradient-to-r from-blue-500 to-indigo-600 text-white shadow-xl">
              🇫🇷 Paris, France
            </div>
          </div>

          <div className="flex gap-3 justify-center flex-wrap mb-12">
            {categories.map((category) => (
              <button
                key={category}
                onClick={() => setSelectedCategory(category)}
                className={`px-6 py-3 rounded-xl font-medium transition-all ${
                  selectedCategory === category
                    ? 'bg-gradient-to-r from-orange-500 to-rose-500 text-white shadow-lg scale-105'
                    : 'bg-white text-gray-700 hover:bg-gray-100 shadow border border-gray-200'
                }`}
              >
                {category.charAt(0).toUpperCase() + category.slice(1)}
              </button>
            ))}
          </div>

          {/* Locations Grid */}
          {loading ? (
            <div className="text-center py-20">
              <div className="inline-block animate-spin rounded-full h-16 w-16 border-4 border-orange-500 border-t-transparent"></div>
              <p className="mt-6 text-gray-600 text-lg">Loading locations...</p>
            </div>
          ) : filteredLocations.length === 0 ? (
            <div className="text-center py-20">
              <p className="text-gray-600 text-xl">No locations found.</p>
            </div>
          ) : (
            <>
              <div className="mb-6 text-gray-600 text-center">
                <span className="font-bold text-orange-500">{filteredLocations.length}</span> location{filteredLocations.length !== 1 ? 's' : ''} found
              </div>
              <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
                {filteredLocations.map((location: any) => (
                  <div
                    key={location.id}
                    onClick={() => setSelectedLocation(location)}
                    className="bg-white rounded-2xl shadow-md overflow-hidden hover:shadow-xl transition-all transform hover:-translate-y-1 cursor-pointer group"
                  >
                    {/* Image */}
                    <div className="relative h-64 overflow-hidden">
                      <div
                        className="h-full bg-cover bg-center transform group-hover:scale-110 transition-transform duration-700"
                        style={{ backgroundImage: `url(${location.image_url})` }}
                      />
                      <button
                        onClick={(e) => toggleFavorite(location.id, e)}
                        className="absolute top-4 right-4 p-2 bg-white/90 backdrop-blur-sm rounded-full hover:bg-white transition-all shadow-lg"
                      >
                        <Heart className={`h-5 w-5 transition ${favorites.includes(location.id) ? 'text-red-500 fill-red-500' : 'text-gray-600 hover:text-red-500'}`} />
                      </button>
                      <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/60 to-transparent p-4">
                        <div className="flex items-center gap-2 text-white text-sm">
                          <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                          <span className="font-semibold">4.8</span>
                          <span className="text-white/80">(127)</span>
                        </div>
                      </div>
                    </div>

                    {/* Content */}
                    <div className="p-5">
                      <div className="flex items-start justify-between mb-2">
                        <h3 className="text-lg font-bold text-gray-900 group-hover:text-orange-500 transition-colors line-clamp-2">
                          {location.name}
                        </h3>
                      </div>
                      <p className="text-gray-600 text-sm mb-3 line-clamp-2">
                        {location.description}
                      </p>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-1 text-sm text-gray-600">
                          <Clock className="h-4 w-4" />
                          <span>{location.average_visit_minutes || location.duration || 15} min</span>
                        </div>
                        <span className="text-xs px-3 py-1 bg-orange-100 text-orange-700 rounded-full font-medium">
                          {location.categories[0]}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      </div>

      {/* Location Detail Modal */}
      {selectedLocation && (
        <div
          className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-fade-in"
          onClick={() => setSelectedLocation(null)}
        >
          <div
            className="bg-white rounded-3xl max-w-4xl w-full max-h-[90vh] overflow-y-auto shadow-2xl animate-slide-up"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="relative h-96 overflow-hidden rounded-t-3xl">
              <div
                className="h-full bg-cover bg-center"
                style={{ backgroundImage: `url(${selectedLocation.image_url})` }}
              />
              <button
                onClick={() => setSelectedLocation(null)}
                className="absolute top-4 right-4 p-3 bg-white/95 backdrop-blur-sm rounded-full hover:bg-white transition-all shadow-xl"
              >
                <X className="h-6 w-6 text-gray-700" />
              </button>
              <div className="absolute top-4 left-4 flex gap-2">
                <button
                  onClick={(e) => toggleFavorite(selectedLocation.id, e)}
                  className="p-3 bg-white/95 backdrop-blur-sm rounded-full hover:bg-white transition-all shadow-xl"
                >
                  <Heart className={`h-6 w-6 transition ${favorites.includes(selectedLocation.id) ? 'text-red-500 fill-red-500' : 'text-gray-700'}`} />
                </button>
                <button
                  onClick={(e) => handleShare(selectedLocation, e)}
                  className="p-3 bg-white/95 backdrop-blur-sm rounded-full hover:bg-white transition-all shadow-xl"
                >
                  <Share2 className="h-6 w-6 text-gray-700" />
                </button>
              </div>
            </div>

            <div className="p-8">
              <div className="flex items-start justify-between mb-6">
                <div>
                  <h2 className="text-4xl font-bold text-gray-900 mb-3">
                    {selectedLocation.name}
                  </h2>
                  <div className="flex items-center gap-4 text-gray-600">
                    <div className="flex items-center gap-1">
                      <Star className="h-5 w-5 fill-yellow-400 text-yellow-400" />
                      <span className="font-bold text-gray-900">4.8</span>
                      <span>(127 reviews)</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <MapPin className="h-5 w-5" />
                      <span>Paris, France</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="border-t border-b border-gray-200 py-6 mb-6">
                <div className="grid grid-cols-3 gap-4">
                  <div className="text-center">
                    <Clock className="h-8 w-8 mx-auto text-orange-500 mb-2" />
                    <div className="text-sm text-gray-500">Visit Duration</div>
                    <div className="font-bold text-gray-900">{selectedLocation.average_visit_minutes || 15} min</div>
                  </div>
                  <div className="text-center">
                    <Users className="h-8 w-8 mx-auto text-blue-600 mb-2" />
                    <div className="text-sm text-gray-500">Best For</div>
                    <div className="font-bold text-gray-900">All Ages</div>
                  </div>
                  <div className="text-center">
                    <Award className="h-8 w-8 mx-auto text-yellow-600 mb-2" />
                    <div className="text-sm text-gray-500">Rating</div>
                    <div className="font-bold text-gray-900">Top Rated</div>
                  </div>
                </div>
              </div>

              <div className="mb-6">
                <h3 className="text-2xl font-bold text-gray-900 mb-4">About</h3>
                <p className="text-gray-700 leading-relaxed text-lg">
                  {selectedLocation.description}
                </p>
              </div>

              <div className="mb-6">
                <h3 className="text-2xl font-bold text-gray-900 mb-4">Categories</h3>
                <div className="flex gap-2 flex-wrap">
                  {selectedLocation.categories.map((cat: string) => (
                    <span
                      key={cat}
                      className="px-4 py-2 bg-gradient-to-r from-orange-100 to-amber-100 text-orange-700 rounded-full font-medium"
                    >
                      {cat}
                    </span>
                  ))}
                </div>
              </div>

              <div className="flex gap-4">
                {selectedLocation.coordinates && (
                  <a
                    href={`https://www.google.com/maps/search/?api=1&query=${selectedLocation.coordinates.lat},${selectedLocation.coordinates.lng}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex-1 flex items-center justify-center gap-2 px-6 py-4 bg-gradient-to-r from-orange-500 to-rose-500 text-white rounded-xl font-semibold hover:shadow-lg transition-all"
                  >
                    <MapPin className="h-5 w-5" />
                    View on Map
                  </a>
                )}
                <button
                  onClick={() => {
                    addToTour(selectedLocation);
                    setSelectedLocation(null);
                  }}
                  disabled={selectedForTour.find(loc => loc.id === selectedLocation.id)}
                  className="flex-1 px-6 py-4 border-2 border-orange-500 text-orange-500 rounded-xl font-semibold hover:bg-orange-50 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {selectedForTour.find(loc => loc.id === selectedLocation.id) ? 'Already Added' : 'Add to Tour'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Selected Locations Floating Panel */}
      {selectedForTour.length > 0 && (
        <div className="fixed bottom-0 left-0 right-0 bg-white border-t-4 border-orange-500 shadow-2xl z-40 animate-slide-up">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-2xl font-bold text-gray-900">
                  Selected Locations ({selectedForTour.length})
                </h3>
                <p className="text-gray-600">Add more or create your tour</p>
              </div>
              <button
                onClick={() => handleCreateTour(undefined, true)}
                disabled={creatingTour}
                className="px-8 py-4 bg-gradient-to-r from-orange-500 to-rose-500 text-white rounded-xl font-bold text-lg hover:shadow-lg transition-all disabled:opacity-50 flex items-center gap-2"
              >
                {creatingTour ? 'Creating...' : `Create Tour with ${selectedForTour.length} Location${selectedForTour.length !== 1 ? 's' : ''}`}
              </button>
            </div>
            <div className="flex gap-4 overflow-x-auto pb-2">
              {selectedForTour.map((location) => (
                <div
                  key={location.id}
                  className="flex-shrink-0 w-64 bg-gray-50 rounded-xl p-4 border-2 border-orange-200 relative group"
                >
                  <button
                    onClick={() => removeFromTour(location.id)}
                    className="absolute -top-2 -right-2 p-2 bg-red-500 text-white rounded-full hover:bg-red-600 transition-all shadow-lg"
                  >
                    <X className="h-4 w-4" />
                  </button>
                  <div
                    className="h-32 bg-cover bg-center rounded-lg mb-3"
                    style={{ backgroundImage: `url(${location.image_url})` }}
                  />
                  <h4 className="font-bold text-gray-900 mb-1 line-clamp-1">{location.name}</h4>
                  <p className="text-sm text-gray-600 line-clamp-2">{location.description}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* How It Works */}
      <div id="how-it-works" className="bg-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">How It Works</h2>
            <p className="text-xl text-gray-600">AI-powered tours in 3 simple steps</p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { step: '1', title: 'Choose Interests', desc: 'Select what you love: history, art, food, or hidden gems', icon: '🎯' },
              { step: '2', title: 'AI Creates Tour', desc: '5 specialized agents work together to curate your perfect route', icon: '🤖' },
              { step: '3', title: 'Start Exploring', desc: 'Follow your custom tour with 90-second audio stories', icon: '🚶' }
            ].map((item, idx) => (
              <div key={idx} className="text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-orange-500 to-rose-500 text-white rounded-2xl text-2xl font-bold mb-6 shadow-lg">
                  {item.step}
                </div>
                <div className="text-5xl mb-4">{item.icon}</div>
                <h3 className="text-2xl font-bold text-gray-900 mb-3">{item.title}</h3>
                <p className="text-gray-600 leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Analytics Dashboard */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <AnalyticsDashboard />
      </div>

      {/* Footer */}
      <div className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-gray-400">
            Built with Google ADK, Gemini 2.5 Flash, Cloud Run & Firestore
          </p>
          <p className="text-gray-500 mt-2">Cloud Run Hackathon 2025 - AI Agents Category</p>
        </div>
      </div>

      <style jsx>{`
        @keyframes fade-in {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        @keyframes slide-up {
          from { transform: translateY(20px); opacity: 0; }
          to { transform: translateY(0); opacity: 1; }
        }
        .animate-fade-in {
          animation: fade-in 0.2s ease-out;
        }
        .animate-slide-up {
          animation: slide-up 0.3s ease-out;
        }
      `}</style>
    </div>
  );
}

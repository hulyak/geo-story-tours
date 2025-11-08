'use client';

import { useState, useEffect } from 'react';
import { TrendingUp, MapPin, Clock, Star } from 'lucide-react';

interface PopularLocation {
  id: string;
  name: string;
  count: number;
  categories: string[];
  image_url?: string;
  average_visit_minutes?: number;
}

interface AnalyticsData {
  totalTours: number;
  totalLocations: number;
  averageTourDuration: number;
  popularLocations: PopularLocation[];
}

export default function AnalyticsDashboard() {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      // Fetch analytics data from API
      const response = await fetch('/api/analytics');
      const data = await response.json();

      if (data.success) {
        setAnalytics(data.analytics);
      }
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-2xl shadow-xl p-8">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-purple-600 border-t-transparent"></div>
          <p className="mt-4 text-gray-600">Loading analytics...</p>
        </div>
      </div>
    );
  }

  if (!analytics) {
    return null;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <div className="p-3 bg-gradient-to-br from-purple-600 to-blue-600 rounded-xl">
          <TrendingUp className="h-6 w-6 text-white" />
        </div>
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Tour Analytics</h2>
          <p className="text-gray-600">Real-time insights from our community</p>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid md:grid-cols-3 gap-6">
        <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-2xl p-6 border border-purple-200">
          <div className="flex items-center justify-between mb-2">
            <div className="text-purple-600 font-semibold text-sm uppercase tracking-wide">
              Total Tours
            </div>
            <div className="p-2 bg-purple-600 rounded-lg">
              <MapPin className="h-5 w-5 text-white" />
            </div>
          </div>
          <div className="text-4xl font-bold text-purple-900">{analytics.totalTours}</div>
          <div className="text-sm text-purple-700 mt-1">Created by users</div>
        </div>

        <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-2xl p-6 border border-blue-200">
          <div className="flex items-center justify-between mb-2">
            <div className="text-blue-600 font-semibold text-sm uppercase tracking-wide">
              Unique Locations
            </div>
            <div className="p-2 bg-blue-600 rounded-lg">
              <Star className="h-5 w-5 text-white" />
            </div>
          </div>
          <div className="text-4xl font-bold text-blue-900">{analytics.totalLocations}</div>
          <div className="text-sm text-blue-700 mt-1">In our database</div>
        </div>

        <div className="bg-gradient-to-br from-cyan-50 to-cyan-100 rounded-2xl p-6 border border-cyan-200">
          <div className="flex items-center justify-between mb-2">
            <div className="text-cyan-600 font-semibold text-sm uppercase tracking-wide">
              Avg Duration
            </div>
            <div className="p-2 bg-cyan-600 rounded-lg">
              <Clock className="h-5 w-5 text-white" />
            </div>
          </div>
          <div className="text-4xl font-bold text-cyan-900">{analytics.averageTourDuration}m</div>
          <div className="text-sm text-cyan-700 mt-1">Per tour</div>
        </div>
      </div>

      {/* Popular Locations */}
      <div className="bg-white rounded-2xl shadow-xl p-8">
        <h3 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
          <span className="text-2xl">🔥</span>
          Most Popular Locations
        </h3>
        <div className="space-y-4">
          {analytics.popularLocations.map((location, index) => (
            <div
              key={location.id}
              className="flex items-center gap-4 p-4 bg-gradient-to-r from-gray-50 to-white rounded-xl hover:shadow-md transition-all"
            >
              {/* Rank */}
              <div className="flex-shrink-0">
                <div
                  className={`w-12 h-12 rounded-xl flex items-center justify-center font-bold text-lg ${
                    index === 0
                      ? 'bg-gradient-to-br from-yellow-400 to-yellow-600 text-white'
                      : index === 1
                      ? 'bg-gradient-to-br from-gray-300 to-gray-500 text-white'
                      : index === 2
                      ? 'bg-gradient-to-br from-orange-400 to-orange-600 text-white'
                      : 'bg-gray-200 text-gray-600'
                  }`}
                >
                  #{index + 1}
                </div>
              </div>

              {/* Image */}
              {location.image_url && (
                <div className="flex-shrink-0 w-20 h-20 rounded-xl overflow-hidden">
                  <div
                    className="w-full h-full bg-cover bg-center"
                    style={{ backgroundImage: `url(${location.image_url})` }}
                  />
                </div>
              )}

              {/* Content */}
              <div className="flex-1">
                <h4 className="font-bold text-gray-900 text-lg">{location.name}</h4>
                <div className="flex items-center gap-3 mt-1">
                  {location.categories && location.categories.length > 0 && (
                    <span className="text-sm text-purple-600 font-medium">
                      {location.categories[0]}
                    </span>
                  )}
                  {location.average_visit_minutes && (
                    <span className="text-sm text-gray-500 flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {location.average_visit_minutes} min
                    </span>
                  )}
                </div>
              </div>

              {/* Count */}
              <div className="text-right">
                <div className="text-3xl font-bold text-purple-600">{location.count}</div>
                <div className="text-xs text-gray-500">tours</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

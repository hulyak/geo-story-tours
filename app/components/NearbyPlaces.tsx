'use client';

import { useEffect, useState } from 'react';

interface Place {
  place_id: string;
  name: string;
  vicinity: string;
  rating?: number;
  types: string[];
}

interface NearbyPlacesProps {
  lat: number;
  lng: number;
}

export default function NearbyPlaces({ lat, lng }: NearbyPlacesProps) {
  const [places, setPlaces] = useState<Place[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedType, setSelectedType] = useState<'restaurant' | 'cafe' | 'store'>('restaurant');

  useEffect(() => {
    if (!lat || !lng) return;

    const fetchNearbyPlaces = async () => {
      setLoading(true);
      try {
        const response = await fetch(
          `/api/places?lat=${lat}&lng=${lng}&type=${selectedType}&radius=500`
        );
        const data = await response.json();

        if (data.results) {
          setPlaces(data.results.slice(0, 5)); // Get top 5 results
        }
      } catch (error) {
        console.error('Error fetching nearby places:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchNearbyPlaces();
  }, [lat, lng, selectedType]);

  const getTypeEmoji = (type: string) => {
    switch (type) {
      case 'restaurant':
        return '🍽️';
      case 'cafe':
        return '☕';
      case 'store':
        return '🛍️';
      default:
        return '📍';
    }
  };

  return (
    <div className="mt-3 border-t pt-3">
      <h4 className="font-bold text-gray-900 text-sm mb-2">Nearby Places</h4>

      {/* Type selector */}
      <div className="flex gap-2 mb-3">
        {(['restaurant', 'cafe', 'store'] as const).map((type) => (
          <button
            key={type}
            type="button"
            onClick={() => setSelectedType(type)}
            className={`flex-1 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
              selectedType === type
                ? 'bg-purple-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {getTypeEmoji(type)} {type.charAt(0).toUpperCase() + type.slice(1)}s
          </button>
        ))}
      </div>

      {/* Places list */}
      {loading ? (
        <div className="text-center py-3">
          <div className="inline-block animate-spin rounded-full h-6 w-6 border-2 border-purple-600 border-t-transparent"></div>
        </div>
      ) : places.length > 0 ? (
        <div className="space-y-2">
          {places.map((place) => (
            <div
              key={place.place_id}
              className="bg-gray-50 rounded-lg p-2 hover:bg-gray-100 transition-colors"
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <p className="font-medium text-gray-900 text-xs leading-tight">
                    {place.name}
                  </p>
                  <p className="text-xs text-gray-500 mt-0.5">{place.vicinity}</p>
                </div>
                {place.rating && (
                  <div className="ml-2 flex items-center gap-1 bg-yellow-100 px-2 py-0.5 rounded">
                    <span className="text-xs">⭐</span>
                    <span className="text-xs font-medium text-gray-900">{place.rating}</span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-xs text-gray-500 text-center py-2">No {selectedType}s found nearby</p>
      )}
    </div>
  );
}

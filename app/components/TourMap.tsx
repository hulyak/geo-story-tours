'use client';

import { useEffect, useRef, useState, useCallback } from 'react';
import { GoogleMap, LoadScript, Marker, Polyline, InfoWindow } from '@react-google-maps/api';
import NearbyPlaces from './NearbyPlaces';
import { calculateDistance, formatDistance, estimateWalkingTime } from '../utils/routeOptimization';

const googleMapsLibraries: ("places" | "geometry")[] = ['places', 'geometry'];

interface Location {
  id: string;
  name: string;
  coordinates: {
    lat: number;
    lng: number;
  };
  description?: string;
  categories?: string[];
}

interface TourMapProps {
  locations: Location[];
  currentStop: number;
  onMarkerClick?: (index: number) => void;
}

const mapContainerStyle = {
  width: '100%',
  height: '100%',
};

const mapOptions = {
  disableDefaultUI: false,
  zoomControl: true,
  streetViewControl: false,
  mapTypeControl: false,
  fullscreenControl: true,
  gestureHandling: 'cooperative',
  styles: [
    {
      featureType: 'poi',
      elementType: 'labels',
      stylers: [{ visibility: 'off' }],
    },
  ],
};

// Get marker icon based on category
function getMarkerIcon(categories?: string[]): string {
  if (!categories || categories.length === 0) return '📍';

  const category = categories[0].toLowerCase();

  // Map categories to emoji icons
  const iconMap: { [key: string]: string } = {
    museum: '🏛️',
    art: '🎨',
    gallery: '🖼️',
    park: '🌳',
    garden: '🌺',
    restaurant: '🍽️',
    cafe: '☕',
    food: '🍴',
    bar: '🍺',
    entertainment: '🎭',
    theater: '🎪',
    music: '🎵',
    shopping: '🛍️',
    market: '🏪',
    historical: '🏰',
    monument: '🗿',
    church: '⛪',
    temple: '🕌',
    landmark: '🏛️',
    beach: '🏖️',
    viewpoint: '👁️',
    photography: '📷',
    architecture: '🏗️',
    library: '📚',
    university: '🎓',
    sports: '⚽',
    stadium: '🏟️',
  };

  for (const [key, icon] of Object.entries(iconMap)) {
    if (category.includes(key)) {
      return icon;
    }
  }

  return '📍';
}

// Create custom marker SVG with emoji
function createCustomMarker(
  emoji: string,
  color: string,
  scale: number = 1
): string {
  const size = 40 * scale;
  const svg = `
    <svg width="${size}" height="${size * 1.3}" viewBox="0 0 40 52" xmlns="http://www.w3.org/2000/svg">
      <path d="M20 0C8.95 0 0 8.95 0 20c0 15 20 32 20 32s20-17 20-32C40 8.95 31.05 0 20 0z"
            fill="${color}" stroke="white" stroke-width="2"/>
      <text x="20" y="22" font-size="18" text-anchor="middle" dominant-baseline="middle">
        ${emoji}
      </text>
    </svg>
  `;
  return 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(svg);
}

export default function TourMap({ locations, currentStop, onMarkerClick }: TourMapProps) {
  const [selectedMarker, setSelectedMarker] = useState<number | null>(null);
  const [center, setCenter] = useState({ lat: 48.8566, lng: 2.3522 }); // Paris coordinates
  const [zoom, setZoom] = useState(14);
  const mapRef = useRef<any>(null);

  // Use a public API key for demo purposes (you should replace this with your own)
  const GOOGLE_MAPS_API_KEY = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY || '';

  // Handle map load
  const onMapLoad = useCallback((map: any) => {
    mapRef.current = map;
  }, []);

  // Auto-fit bounds to show all markers
  useEffect(() => {
    if (mapRef.current && locations && locations.length > 0 && window.google?.maps) {
      const bounds = new window.google.maps.LatLngBounds();

      locations.forEach((location) => {
        if (location.coordinates) {
          bounds.extend({
            lat: location.coordinates.lat,
            lng: location.coordinates.lng,
          });
        }
      });

      // Fit the map to show all markers with padding
      mapRef.current.fitBounds(bounds, {
        top: 50,
        bottom: 50,
        left: 50,
        right: 50,
      });
    }
  }, [locations]);

  // Smooth transition to current stop
  useEffect(() => {
    if (mapRef.current && locations[currentStop]?.coordinates) {
      const currentLocation = locations[currentStop].coordinates;

      mapRef.current.panTo({
        lat: currentLocation.lat,
        lng: currentLocation.lng,
      });

      // Zoom in slightly on the current stop
      const currentZoom = mapRef.current.getZoom() || 14;
      if (currentZoom < 15) {
        mapRef.current.setZoom(15);
      }
    }
  }, [currentStop, locations]);

  if (!locations || locations.length === 0) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-gray-100 rounded-xl">
        <p className="text-gray-500">No locations to display</p>
      </div>
    );
  }

  // Create path for polyline
  const path = locations
    .filter(loc => loc.coordinates)
    .map(loc => ({
      lat: loc.coordinates.lat,
      lng: loc.coordinates.lng,
    }));

  return (
    <LoadScript googleMapsApiKey={GOOGLE_MAPS_API_KEY} libraries={googleMapsLibraries}>
      <GoogleMap
        mapContainerStyle={mapContainerStyle}
        center={center}
        zoom={zoom}
        options={mapOptions}
        onLoad={onMapLoad}
      >
        {/* Draw route line */}
        {path.length > 1 && (
          <Polyline
            path={path}
            options={{
              strokeColor: '#8B5CF6',
              strokeOpacity: 0.8,
              strokeWeight: 4,
              geodesic: true,
              icons: window.google?.maps?.SymbolPath ? [
                {
                  icon: {
                    path: window.google.maps.SymbolPath.FORWARD_CLOSED_ARROW,
                    scale: 3,
                    strokeColor: '#8B5CF6',
                    fillColor: '#8B5CF6',
                    fillOpacity: 1,
                  },
                  offset: '100%',
                  repeat: '150px',
                },
              ] : undefined,
            }}
          />
        )}

        {/* Place markers */}
        {locations.map((location, index) => {
          if (!location.coordinates) return null;

          const isCurrentStop = index === currentStop;
          const isPastStop = index < currentStop;
          const isFutureStop = index > currentStop;

          const emoji = getMarkerIcon(location.categories);
          const markerColor = isCurrentStop ? '#8B5CF6' : isPastStop ? '#10B981' : '#D1D5DB';
          const markerScale = isCurrentStop ? 1.2 : 1;

          return (
            <Marker
              key={location.id}
              position={{
                lat: location.coordinates.lat,
                lng: location.coordinates.lng,
              }}
              label={{
                text: `${index + 1}`,
                color: 'white',
                fontWeight: 'bold',
                fontSize: '12px',
                className: 'marker-label',
              }}
              icon={window.google?.maps ? {
                url: createCustomMarker(emoji, markerColor, markerScale),
                scaledSize: new window.google.maps.Size(40 * markerScale, 52 * markerScale),
                anchor: new window.google.maps.Point(20 * markerScale, 52 * markerScale),
                labelOrigin: new window.google.maps.Point(20 * markerScale, 20 * markerScale),
              } : undefined}
              animation={isCurrentStop ? window.google?.maps?.Animation?.BOUNCE : undefined}
              onClick={() => {
                setSelectedMarker(index);
                if (onMarkerClick) {
                  onMarkerClick(index);
                }
              }}
            />
          );
        })}

        {/* Info window for selected marker */}
        {selectedMarker !== null && locations[selectedMarker]?.coordinates && (
          <InfoWindow
            position={{
              lat: locations[selectedMarker].coordinates.lat,
              lng: locations[selectedMarker].coordinates.lng,
            }}
            onCloseClick={() => setSelectedMarker(null)}
            options={window.google?.maps ? {
              pixelOffset: new window.google.maps.Size(0, -10),
            } : {}}
          >
            <div className="p-3 max-w-xs">
              <div className="flex items-start gap-2 mb-2">
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center text-white font-bold text-sm flex-shrink-0 ${
                    selectedMarker === currentStop
                      ? 'bg-purple-600'
                      : selectedMarker < currentStop
                      ? 'bg-green-600'
                      : 'bg-gray-400'
                  }`}
                >
                  {selectedMarker + 1}
                </div>
                <div>
                  <h3 className="font-bold text-gray-900 text-base leading-tight">
                    {locations[selectedMarker].name}
                  </h3>
                  <p className={`text-xs font-medium mt-1 ${
                    selectedMarker === currentStop
                      ? 'text-purple-600'
                      : selectedMarker < currentStop
                      ? 'text-green-600'
                      : 'text-gray-500'
                  }`}>
                    {selectedMarker === currentStop
                      ? 'Current Stop'
                      : selectedMarker < currentStop
                      ? 'Completed'
                      : 'Upcoming'}
                  </p>
                </div>
              </div>

              {/* Distance from previous stop */}
              {selectedMarker > 0 &&
                locations[selectedMarker - 1]?.coordinates &&
                locations[selectedMarker].coordinates && (
                  <div className="bg-blue-50 rounded-lg px-3 py-2 mb-2">
                    <p className="text-xs text-blue-900 font-medium">
                      {(() => {
                        const prevLoc = locations[selectedMarker - 1].coordinates;
                        const currLoc = locations[selectedMarker].coordinates;
                        const distance = calculateDistance(
                          prevLoc.lat,
                          prevLoc.lng,
                          currLoc.lat,
                          currLoc.lng
                        );
                        return (
                          <>
                            {formatDistance(distance)} from previous stop
                            <span className="text-blue-700 ml-1">
                              ({estimateWalkingTime(distance)})
                            </span>
                          </>
                        );
                      })()}
                    </p>
                  </div>
                )}

              {locations[selectedMarker].description && (
                <p className="text-sm text-gray-600 leading-relaxed">
                  {locations[selectedMarker].description.length > 120
                    ? locations[selectedMarker].description.substring(0, 120) + '...'
                    : locations[selectedMarker].description}
                </p>
              )}

              {/* Street View Link */}
              <a
                href={`https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=${locations[selectedMarker].coordinates.lat},${locations[selectedMarker].coordinates.lng}`}
                target="_blank"
                rel="noopener noreferrer"
                className="mt-3 w-full px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
              >
                <span>👁️ Open Street View</span>
              </a>

              {/* Nearby Places */}
              <NearbyPlaces
                lat={locations[selectedMarker].coordinates.lat}
                lng={locations[selectedMarker].coordinates.lng}
              />
            </div>
          </InfoWindow>
        )}
      </GoogleMap>
    </LoadScript>
  );
}

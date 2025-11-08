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

// Calculate distance between two coordinates using Haversine formula (in km)
function calculateDistance(
  lat1: number,
  lng1: number,
  lat2: number,
  lng2: number
): number {
  const R = 6371; // Earth's radius in km
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLng = ((lng2 - lng1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLng / 2) *
      Math.sin(dLng / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

// Calculate total tour distance
export function calculateTotalDistance(locations: Location[]): number {
  let totalDistance = 0;

  for (let i = 0; i < locations.length - 1; i++) {
    const current = locations[i];
    const next = locations[i + 1];

    if (current.coordinates && next.coordinates) {
      totalDistance += calculateDistance(
        current.coordinates.lat,
        current.coordinates.lng,
        next.coordinates.lat,
        next.coordinates.lng
      );
    }
  }

  return totalDistance;
}

// Optimize tour route using nearest neighbor algorithm
// This keeps the first location fixed as the starting point
export function optimizeRoute(locations: Location[]): Location[] {
  if (locations.length <= 2) {
    return [...locations]; // No optimization needed for 2 or fewer locations
  }

  const optimized: Location[] = [];
  const remaining = [...locations];

  // Keep the first location as the starting point
  const start = remaining.shift()!;
  optimized.push(start);

  let current = start;

  // Use nearest neighbor algorithm
  while (remaining.length > 0) {
    let nearestIndex = 0;
    let nearestDistance = Infinity;

    // Find the nearest unvisited location
    remaining.forEach((location, index) => {
      if (current.coordinates && location.coordinates) {
        const distance = calculateDistance(
          current.coordinates.lat,
          current.coordinates.lng,
          location.coordinates.lat,
          location.coordinates.lng
        );

        if (distance < nearestDistance) {
          nearestDistance = distance;
          nearestIndex = index;
        }
      }
    });

    // Add the nearest location to the optimized route
    const nearest = remaining.splice(nearestIndex, 1)[0];
    optimized.push(nearest);
    current = nearest;
  }

  return optimized;
}

// Format distance for display
export function formatDistance(km: number): string {
  if (km < 1) {
    return `${Math.round(km * 1000)}m`;
  }
  return `${km.toFixed(2)}km`;
}

// Estimate walking time (average walking speed: 5 km/h)
export function estimateWalkingTime(km: number): string {
  const minutes = Math.round((km / 5) * 60);
  if (minutes < 1) return '< 1 min';
  if (minutes === 1) return '1 min';
  if (minutes >= 60) {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours}h ${mins}min`;
  }
  return `${minutes} min`;
}

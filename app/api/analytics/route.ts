import { NextResponse } from 'next/server';

// In production, this would query Firestore/BigQuery for real analytics
// For now, we'll return simulated data
export async function GET() {
  try {
    // Simulated analytics data
    // In production, this would aggregate data from Firestore:
    // - Count tours collection
    // - Aggregate location usage
    // - Calculate average durations

    const analytics = {
      totalTours: 127,
      totalLocations: 45,
      averageTourDuration: 45,
      popularLocations: [
        {
          id: 'brooklyn_bridge',
          name: 'Brooklyn Bridge',
          count: 89,
          categories: ['historical', 'architecture'],
          image_url: 'https://images.unsplash.com/photo-1513026705753-bc3fffca8bf4?w=400',
          average_visit_minutes: 20
        },
        {
          id: 'central_park',
          name: 'Central Park',
          count: 76,
          categories: ['park', 'nature'],
          image_url: 'https://images.unsplash.com/photo-1568515387631-8b650bbcdb90?w=400',
          average_visit_minutes: 60
        },
        {
          id: 'metropolitan_museum',
          name: 'Metropolitan Museum of Art',
          count: 68,
          categories: ['museum', 'art'],
          image_url: 'https://images.unsplash.com/photo-1566127444979-b3d2b654e3d5?w=400',
          average_visit_minutes: 90
        },
        {
          id: 'times_square',
          name: 'Times Square',
          count: 64,
          categories: ['entertainment', 'landmark'],
          image_url: 'https://images.unsplash.com/photo-1564221710304-0b37c8b9d729?w=400',
          average_visit_minutes: 15
        },
        {
          id: 'statue_of_liberty',
          name: 'Statue of Liberty',
          count: 58,
          categories: ['historical', 'monument'],
          image_url: 'https://images.unsplash.com/photo-1541336032412-2048ef7e8c23?w=400',
          average_visit_minutes: 45
        },
      ]
    };

    return NextResponse.json({
      success: true,
      analytics
    });
  } catch (error) {
    console.error('Error fetching analytics:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to fetch analytics' },
      { status: 500 }
    );
  }
}

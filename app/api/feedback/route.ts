import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { tour_id, rating, feedback, helpful_vote, timestamp } = body;

    // Validate required fields
    if (!tour_id || !rating) {
      return NextResponse.json(
        { success: false, error: 'Missing required fields' },
        { status: 400 }
      );
    }

    // In production, this would save to Firestore:
    // const db = firestore.Client()
    // await db.collection('feedback').add({
    //   tour_id,
    //   rating,
    //   feedback,
    //   helpful_vote,
    //   timestamp,
    //   status: 'pending_review'
    // })

    console.log('Feedback received:', {
      tour_id,
      rating,
      feedback,
      helpful_vote,
      timestamp,
    });

    // If rating is low (1-2 stars), could trigger content regeneration
    if (rating <= 2 && feedback) {
      // In production, publish to Pub/Sub topic for story regeneration
      // publisher.publish('story-regeneration', {
      //   tour_id,
      //   reason: feedback,
      //   priority: 'high'
      // })
      console.log('Low rating detected - would trigger content review');
    }

    return NextResponse.json({
      success: true,
      message: 'Feedback submitted successfully',
    });
  } catch (error) {
    console.error('Error submitting feedback:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to submit feedback' },
      { status: 500 }
    );
  }
}

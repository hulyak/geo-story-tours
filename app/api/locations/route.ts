import { NextResponse } from 'next/server';
import { Firestore } from '@google-cloud/firestore';

const PROJECT_ID = process.env.NEXT_PUBLIC_PROJECT_ID || 'durable-torus-477513-g3';

// Initialize Firestore (will use default credentials on Cloud Run)
const db = new Firestore({
  projectId: PROJECT_ID,
});

export async function GET() {
  try {
    const locationsRef = db.collection('locations');
    const snapshot = await locationsRef.get();

    if (snapshot.empty) {
      return NextResponse.json({ locations: [] });
    }

    const locations = snapshot.docs.map((doc) => ({
      id: doc.id,
      ...doc.data(),
    }));

    return NextResponse.json({ locations });
  } catch (error) {
    console.error('Error fetching locations:', error);
    return NextResponse.json(
      { error: 'Internal server error', details: String(error) },
      { status: 500 }
    );
  }
}

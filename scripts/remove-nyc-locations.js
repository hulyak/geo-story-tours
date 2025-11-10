/**
 * Remove all New York City locations from Firestore
 */
const { Firestore } = require('@google-cloud/firestore');
const db = new Firestore({ projectId: 'durable-torus-477513-g3' });

async function removeNYCLocations() {
  console.log('🗑️  Removing NYC locations from Firestore...\n');

  const locationsRef = db.collection('locations');
  const snapshot = await locationsRef.get();

  let removed = 0;
  const batch = db.batch();

  for (const doc of snapshot.docs) {
    const data = doc.data();
    const coords = data.coordinates;

    if (coords && coords.lat && coords.lng) {
      const lat = coords.lat;
      const lng = coords.lng;

      // Check if coordinates are in New York (approximate bounds)
      const isNYC = (lat >= 40.6 && lat <= 40.9 && lng >= -74.1 && lng <= -73.9);

      if (isNYC) {
        console.log(`❌ Removing: ${data.name} (${doc.id})`);
        console.log(`   Coords: ${lat}, ${lng}\n`);
        batch.delete(doc.ref);
        removed++;
      }
    }
  }

  if (removed > 0) {
    await batch.commit();
    console.log(`\n✅ Removed ${removed} NYC locations`);
  } else {
    console.log('✅ No NYC locations found');
  }
}

removeNYCLocations().then(() => process.exit(0)).catch(console.error);

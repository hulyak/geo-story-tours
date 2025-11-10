/**
 * Remove specific NYC locations and test data from Firestore
 */
const { Firestore } = require('@google-cloud/firestore');
const db = new Firestore({ projectId: 'durable-torus-477513-g3' });

const locationsToRemove = [
  'Grand Central Terminal',
  'The High Line',
  'Metropolitan Museum of Art',
  'One World Trade Center',
  'Statue of Liberty',
  'SoHo',
  'Test Location'
];

async function removeLocations() {
  console.log('🔍 Searching for locations to remove...\n');

  const locationsRef = db.collection('locations');
  const snapshot = await locationsRef.get();

  let removed = 0;
  const batch = db.batch();

  for (const doc of snapshot.docs) {
    const data = doc.data();
    const locationName = data.name;

    // Check if this location should be removed
    const shouldRemove = locationsToRemove.some(nameToRemove =>
      locationName.toLowerCase().includes(nameToRemove.toLowerCase()) ||
      nameToRemove.toLowerCase().includes(locationName.toLowerCase())
    );

    if (shouldRemove) {
      console.log(`❌ Removing: ${locationName} (${doc.id})`);
      if (data.coordinates) {
        console.log(`   Coords: ${data.coordinates.lat}, ${data.coordinates.lng}`);
      }
      console.log('');
      batch.delete(doc.ref);
      removed++;
    }
  }

  if (removed > 0) {
    await batch.commit();
    console.log(`\n✅ Removed ${removed} locations`);
  } else {
    console.log('✅ No matching locations found');
  }
}

removeLocations().then(() => process.exit(0)).catch(console.error);

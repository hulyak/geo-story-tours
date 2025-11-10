/**
 * Audit location images to ensure they match the locations
 */
const { Firestore } = require('@google-cloud/firestore');
const db = new Firestore({ projectId: 'durable-torus-477513-g3' });

async function auditImages() {
  console.log('🔍 Auditing Location Images...\n');

  const locationsRef = db.collection('locations');
  const snapshot = await locationsRef.get();

  console.log(`📊 Total locations: ${snapshot.size}\n`);
  console.log('=' .repeat(80));
  console.log('\n');

  let issueCount = 0;

  for (const doc of snapshot.docs) {
    const data = doc.data();

    console.log(`📍 ${data.name}`);
    console.log(`   ID: ${doc.id}`);
    console.log(`   Coordinates: ${data.coordinates?.lat}, ${data.coordinates?.lng}`);
    console.log(`   Categories: ${data.categories?.join(', ')}`);
    console.log(`   Image URL: ${data.image_url || 'MISSING'}`);
    console.log(`   Description: ${data.description?.substring(0, 80)}...`);

    // Check for missing or invalid images
    if (!data.image_url) {
      console.log('   ⚠️  WARNING: Missing image URL');
      issueCount++;
    } else if (!data.image_url.startsWith('http')) {
      console.log('   ⚠️  WARNING: Invalid image URL format');
      issueCount++;
    }

    // Check for missing coordinates
    if (!data.coordinates || !data.coordinates.lat || !data.coordinates.lng) {
      console.log('   ⚠️  WARNING: Missing coordinates');
      issueCount++;
    }

    console.log('');
  }

  console.log('=' .repeat(80));
  if (issueCount === 0) {
    console.log('\n✅ All locations have valid images and coordinates!');
  } else {
    console.log(`\n⚠️  Found ${issueCount} issues`);
  }
}

auditImages().then(() => process.exit(0)).catch(console.error);

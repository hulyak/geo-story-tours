/**
 * Audit Firestore locations collection
 * Check for:
 * - Missing or invalid coordinates
 * - Missing or invalid image URLs
 * - Data consistency
 */

const { Firestore } = require('@google-cloud/firestore');

const PROJECT_ID = 'durable-torus-477513-g3';
const db = new Firestore({ projectId: PROJECT_ID });

async function auditLocations() {
  console.log('🔍 Auditing Firestore locations...\n');

  const locationsRef = db.collection('locations');
  const snapshot = await locationsRef.get();

  if (snapshot.empty) {
    console.log('❌ No locations found in Firestore!');
    return;
  }

  console.log(`📊 Found ${snapshot.size} locations\n`);

  const issues = [];

  snapshot.forEach((doc) => {
    const data = doc.data();
    const locationIssues = [];

    // Check coordinates
    if (!data.coordinates) {
      locationIssues.push('Missing coordinates field');
    } else if (!data.coordinates.lat || !data.coordinates.lng) {
      locationIssues.push('Invalid coordinates (missing lat/lng)');
    } else {
      // Check if coordinates are in Paris (approximate bounds)
      const lat = data.coordinates.lat;
      const lng = data.coordinates.lng;
      const isParis = (lat >= 48.8 && lat <= 48.9 && lng >= 2.2 && lng <= 2.5);
      const isNYC = (lat >= 40.6 && lat <= 40.9 && lng >= -74.1 && lng <= -73.9);

      if (!isParis && !isNYC) {
        locationIssues.push(`Coordinates outside Paris/NYC: ${lat}, ${lng}`);
      }
    }

    // Check image URL
    if (!data.image_url) {
      locationIssues.push('Missing image_url');
    } else if (!data.image_url.startsWith('http')) {
      locationIssues.push('Invalid image_url format');
    }

    // Check required fields
    if (!data.name) locationIssues.push('Missing name');
    if (!data.description) locationIssues.push('Missing description');
    if (!data.categories || data.categories.length === 0) {
      locationIssues.push('Missing or empty categories');
    }

    if (locationIssues.length > 0) {
      issues.push({
        id: doc.id,
        name: data.name || 'Unknown',
        coordinates: data.coordinates,
        image_url: data.image_url,
        issues: locationIssues
      });
    }
  });

  if (issues.length === 0) {
    console.log('✅ No issues found! All locations are valid.');
  } else {
    console.log(`❌ Found ${issues.length} locations with issues:\n`);
    issues.forEach((item, index) => {
      console.log(`${index + 1}. ${item.name} (${item.id})`);
      console.log(`   Coordinates: ${JSON.stringify(item.coordinates)}`);
      console.log(`   Image: ${item.image_url}`);
      item.issues.forEach(issue => {
        console.log(`   - ${issue}`);
      });
      console.log('');
    });
  }

  return issues;
}

// Run audit
auditLocations()
  .then(() => {
    console.log('\n✅ Audit complete');
    process.exit(0);
  })
  .catch((error) => {
    console.error('❌ Error:', error);
    process.exit(1);
  });

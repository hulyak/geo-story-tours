#!/usr/bin/env node
/**
 * Populate Firestore with sample locations
 * Run: node scripts/populate-firestore.js
 */

const { Firestore } = require('@google-cloud/firestore');
const fs = require('fs');
const path = require('path');

const PROJECT_ID = 'durable-torus-477513-g3';

// Read locations data
const locationsData = JSON.parse(
  fs.readFileSync(path.join(__dirname, 'locations-data.json'), 'utf8')
);

async function populateFirestore() {
  console.log(`🚀 Connecting to Firestore (Project: ${PROJECT_ID})`);

  const db = new Firestore({
    projectId: PROJECT_ID,
  });

  console.log(`\n📝 Adding ${locationsData.locations.length} locations to Firestore...\n`);

  let successCount = 0;
  let errorCount = 0;

  for (const location of locationsData.locations) {
    const { id, ...data } = location;

    try {
      await db.collection('locations').doc(id).set(data);
      console.log(`   ✅ ${data.name} (${data.categories.join(', ')})`);
      successCount++;
    } catch (error) {
      console.log(`   ❌ ${data.name} - Error: ${error.message}`);
      errorCount++;
    }
  }

  console.log(`\n✨ Done! Added ${successCount} locations to Firestore`);
  if (errorCount > 0) {
    console.log(`⚠️  ${errorCount} locations failed to add`);
  }

  console.log(`\n🎯 Your tour agents can now select from these locations!`);

  // Show categories
  const categories = new Set();
  locationsData.locations.forEach(loc => {
    loc.categories.forEach(cat => categories.add(cat));
  });

  console.log(`\n📍 Categories available:`);
  Array.from(categories).sort().forEach(cat => {
    const count = locationsData.locations.filter(loc =>
      loc.categories.includes(cat)
    ).length;
    console.log(`   - ${cat}: ${count} locations`);
  });

  process.exit(0);
}

populateFirestore().catch(error => {
  console.error('Error:', error);
  process.exit(1);
});

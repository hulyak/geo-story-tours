/**
 * Fix Firestore locations - Add missing coordinates
 * Paris locations default to approximate Paris center
 */
const { Firestore } = require('@google-cloud/firestore');
const db = new Firestore({ projectId: 'durable-torus-477513-g3' });

const PARIS_COORDS = { lat: 48.8566, lng: 2.3522 };

// Known Paris locations with accurate coordinates
const LOCATION_COORDS = {
  'eiffel_tower': { lat: 48.8584, lng: 2.2945 },
  'louvre_museum': { lat: 48.8606, lng: 2.3376 },
  'notre_dame_cathedral': { lat: 48.8530, lng: 2.3499 },
  'arc_de_triomphe': { lat: 48.8738, lng: 2.2950 },
  'sacre_coeur_basilica': { lat: 48.8867, lng: 2.3431 },
  'champs_elysees': { lat: 48.8698, lng: 2.3076 },
  'montmartre': { lat: 48.8867, lng: 2.3431 },
  'musee_dorsay': { lat: 48.8600, lng: 2.3266 },
  'pantheon': { lat: 48.8462, lng: 2.3464 },
  'luxembourg_gardens': { lat: 48.8462, lng: 2.3371 },
  'sainte_chapelle': { lat: 48.8553, lng: 2.3448 },
  'centre_pompidou': { lat: 48.8606, lng: 2.3522 },
  'tuileries_garden': { lat: 48.8634, lng: 2.3275 },
  'latin_quarter': { lat: 48.8504, lng: 2.3443 },
  'le_marais': { lat: 48.8589, lng: 2.3626 },
  'canal_saint_martin': { lat: 48.8737, lng: 2.3632 },
  'palais_garnier': { lat: 48.8720, lng: 2.3318 },
  'rodin_museum': { lat: 48.8552, lng: 2.3162 },
  'pere_lachaise_cemetery': { lat: 48.8610, lng: 2.3932 },
  'musee_picasso': { lat: 48.8597, lng: 2.3626 },
  'shakespeare_and_company': { lat: 48.8524, lng: 2.3470 },
  'rue_cremieux': { lat: 48.8465, lng: 2.3827 },
  'promenade_plantee': { lat: 48.8477, lng: 2.3707 },
  'marche_des_enfants_rouges': { lat: 48.8635, lng: 2.3638 },
  'galeries_lafayette': { lat: 48.8734, lng: 2.3321 }
};

async function fixLocations() {
  console.log('🔧 Fixing Firestore locations...\n');

  const locationsRef = db.collection('locations');
  const snapshot = await locationsRef.get();

  let fixed = 0;

  for (const doc of snapshot.docs) {
    const data = doc.data();

    if (!data.coordinates || !data.coordinates.lat || !data.coordinates.lng) {
      const coords = LOCATION_COORDS[doc.id] || PARIS_COORDS;

      await doc.ref.update({ coordinates: coords });
      console.log(`✅ Fixed ${doc.id}: ${coords.lat}, ${coords.lng}`);
      fixed++;
    }
  }

  console.log(`\n✅ Fixed ${fixed} locations`);
}

fixLocations().then(() => process.exit(0)).catch(console.error);

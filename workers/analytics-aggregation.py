"""
Analytics Aggregation Worker
Runs daily to calculate tour popularity, rating trends, and other metrics
"""

from google.cloud import firestore
from datetime import datetime
from collections import Counter
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def aggregate_tour_analytics():
    """Calculate and store tour analytics"""
    db = firestore.Client()

    try:
        # Calculate top locations
        tours = db.collection('tours').stream()
        location_counts = Counter()
        total_tours = 0
        total_duration = 0

        for tour in tours:
            tour_data = tour.to_dict()
            total_tours += 1

            # Count duration
            if 'duration' in tour_data:
                total_duration += tour_data['duration']

            # Count location usage
            if 'locations' in tour_data:
                for location in tour_data['locations']:
                    location_id = location.get('id')
                    if location_id:
                        location_counts[location_id] += 1

        # Calculate average duration
        avg_duration = total_duration / total_tours if total_tours > 0 else 0

        # Get top 10 locations
        top_locations = location_counts.most_common(10)

        # Save to aggregated collection
        analytics_data = {
            'total_tours': total_tours,
            'average_duration': round(avg_duration, 1),
            'top_locations': [
                {'location_id': loc_id, 'count': count}
                for loc_id, count in top_locations
            ],
            'updated_at': firestore.SERVER_TIMESTAMP,
            'date': datetime.now().strftime('%Y-%m-%d')
        }

        db.collection('analytics').document('daily_summary').set(analytics_data)

        logger.info(f"Analytics aggregated: {total_tours} tours, {len(top_locations)} top locations")

        return analytics_data

    except Exception as e:
        logger.error(f"Error aggregating analytics: {e}")
        raise


def aggregate_feedback_stats():
    """Aggregate feedback and ratings"""
    db = firestore.Client()

    try:
        feedbacks = db.collection('feedback').stream()

        rating_counts = Counter()
        total_feedback = 0
        helpful_votes = {'up': 0, 'down': 0}

        for feedback in feedbacks:
            feedback_data = feedback.to_dict()
            total_feedback += 1

            # Count ratings
            rating = feedback_data.get('rating')
            if rating:
                rating_counts[rating] += 1

            # Count helpful votes
            helpful_vote = feedback_data.get('helpful_vote')
            if helpful_vote in ['up', 'down']:
                helpful_votes[helpful_vote] += 1

        # Calculate average rating
        total_rating = sum(rating * count for rating, count in rating_counts.items())
        avg_rating = total_rating / total_feedback if total_feedback > 0 else 0

        feedback_stats = {
            'total_feedback': total_feedback,
            'average_rating': round(avg_rating, 2),
            'rating_distribution': dict(rating_counts),
            'helpful_votes': helpful_votes,
            'updated_at': firestore.SERVER_TIMESTAMP
        }

        db.collection('analytics').document('feedback_stats').set(feedback_stats)

        logger.info(f"Feedback stats aggregated: {total_feedback} feedbacks, avg rating: {avg_rating:.2f}")

        return feedback_stats

    except Exception as e:
        logger.error(f"Error aggregating feedback: {e}")
        raise


if __name__ == '__main__':
    logger.info("Starting analytics aggregation...")

    # Run both aggregations
    tour_analytics = aggregate_tour_analytics()
    feedback_stats = aggregate_feedback_stats()

    logger.info("Analytics aggregation completed successfully")
    print(f"Tours: {tour_analytics['total_tours']}, Avg Duration: {tour_analytics['average_duration']}min")
    print(f"Feedback: {feedback_stats['total_feedback']}, Avg Rating: {feedback_stats['average_rating']}/5")

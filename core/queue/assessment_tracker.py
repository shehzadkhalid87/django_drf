import logging
import time  # Import time module
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from assessment.models import AssessmentStatus
from assessment.repositories import AssessmentRepository

# Set up the logger
logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=5)
def track_assessment_time(self, assessment_id: int):
    """
    Background task to track the elapsed time for an assessment.

    Args:
        assessment_id (int): The ID of the assessment to track.
    """
    try:
        logger.info(f"Starting to track time for assessment ID: {assessment_id}")

        assessment = AssessmentRepository.find_by_id(assessment_id)

        # Ensure time_elapsed is initialized
        if assessment.time_elapsed is None:
            assessment.time_elapsed = timedelta(0)  # Initialize to 0 duration
            logger.info(f"Initialized time_elapsed for assessment ID {assessment_id} to 0.")

        # Update the time elapsed every 60 seconds for 25 iterations (total 60 minutes)
        for _ in range(60):
            # Wait for 10 seconds
            self.update_state(state='PROGRESS', meta={'time_elapsed': assessment.time_elapsed.total_seconds()})
            assessment = AssessmentRepository.find_by_id(assessment_id)
            if assessment.status == AssessmentStatus.COMPLETED.value:
                break

            # Increment elapsed time by 10 seconds
            assessment.time_elapsed += timedelta(seconds=60)
            assessment.save()  # Save the updated assessment

            logger.info(
                f"Updated time_elapsed for assessment ID {assessment_id}: {assessment.time_elapsed.total_seconds()} seconds.")

            time.sleep(60)  # Sleep for 60 seconds

        assessment = AssessmentRepository.find_by_id(assessment_id)
        if assessment.status != AssessmentStatus.COMPLETED.value:
            # Mark the assessment as completed after the loop
            AssessmentRepository.update(
                assessment_id=assessment.id,
                is_active=False,
                completed_at=timezone.now(),
                status=AssessmentStatus.COMPLETED.value,
                session_token=None,
                session_expiry=None
            )

        logger.info(f"Completed tracking time for assessment ID: {assessment_id}. Assessment marked as inactive.")

    except Exception as e:
        logger.error(f"Error occurred while tracking assessment time for ID {assessment_id}: {str(e)}")
        raise e


@shared_task(max_retries=5, bind=True)
def track_team_assessment_time(self, team_id: int):
    """
    Once the assessments get expired this will trigger
    Call AI module to get reporting
    """
    print(team_id)
    pass

from django.db import transaction
from django.db.models import F

from users.models import UserProfile

# weights
W_LIKE = 1.0   # adds 1 per like 
W_FOLLOW = 5.0 # adds 5 per follow
W_ATTEND = 2.0 # adds 2 per event attendance
W_POSTS = 4.0  # subtracts 4 per post created


def adjust_credibility(user, delta):
    """Atomically adjust the given user's UserProfile.credibility by delta.

    Ensures credibility doesn't go below 0. Returns the new credibility value.
    """
    if delta == 0:
        try:
            return user.userprofile.credibility
        except UserProfile.DoesNotExist:
            return 0

    with transaction.atomic():
        profile = UserProfile.objects.select_for_update().get(user=user)
        new_score = profile.credibility + delta
        if new_score < 0:
            new_score = 0
        # store as integer
        profile.credibility = int(round(new_score))
        profile.save(update_fields=['credibility'])
        return profile.credibility

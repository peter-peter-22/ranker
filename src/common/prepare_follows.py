from src.common.fetch_data import Follow
from typing import List,Dict,Set,Callable
from uuid import UUID

FollowChecker = (Callable[[UUID,UUID],bool])

def get_follow_checker(follows:List[Follow])->FollowChecker:
    """
    Create a map from the follows and export a function that checks if a user follows another.
    Args:
        follows (List[Follow]): A list of Follow objects to create the map from.
    Returns:
        Callable[[UUID, UUID], bool]: A function that checks if a user follows another.
    """
    # Create the follow map
    follow_map:Dict[UUID,Set[UUID]]={}

    # Get or create a set of followers for a specified
    def get_or_create(follower:UUID):
        """
        Get or create a set of followers for the given user.
        Args:
            follower (UUID): The ID of the user to get or create the set for.
        Returns:
            Set[UUID]: The set of followers for the given user.
        """
        followed_set=follow_map.get(follower)
        if not followed_set:
            followed_set=set()
            follow_map[follower]=followed_set
            return followed_set
        return followed_set

    # Create a map from the follow entries
    for follower,followed in follows:
        get_or_create(follower).add(followed)

    # Create function to check if a user follows another
    def check_follows(follower:UUID,followed:UUID):
        """
        Function to get if a user follows another based on the follow map.
        Args:
            follower (UUID): The ID of the follower.
            followed (UUID): The ID of the followed.
        """
        return followed in get_or_create(follower)

    # Export only the function
    return check_follows
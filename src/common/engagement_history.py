from uuid import UUID
from typing import Dict, NamedTuple
from dataclasses import dataclass

@dataclass
class EngagementHistory:
    likes:int=0
    replies:int=0
    clicks:int=0

def engagement_history_manager():
    """Track the engagement histories between users and return a function to read them."""

    history_map:Dict[UUID,Dict[UUID,EngagementHistory]]={}

    def get_or_create_viewer(viewer:UUID):
        """Get or create the engagement history map of a viewer."""
        viewer_histories=history_map.get(viewer)
        if not viewer_histories:
            viewer_histories={}
            history_map[viewer]=viewer_histories
        return viewer_histories

    def get_history(viewer:UUID,poster:UUID)->EngagementHistory:
        """Get or create the engagement history between two users."""
        viewer_histories=get_or_create_viewer(viewer)
        poster_history=viewer_histories.get(poster)
        if not poster_history:
            poster_history=EngagementHistory()
            viewer_histories[poster]=poster_history
        return poster_history

    return get_history

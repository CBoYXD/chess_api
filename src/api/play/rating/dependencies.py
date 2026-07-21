from .schemas import Rating
from .utils import get_k_factor, get_probality, get_rating
from src.database.models.users import User


def calculate_rating(user: User, opponent_user: User) -> Rating:
    k_factor = get_k_factor(user.rank)
    user_win_probality = get_probality(opponent_user.rank, user.rank)
    # If user win, actual is 1, if lose, actual is 0, if draw actual is 0.5
    rating_on_win = get_rating(user.rank, k_factor, 1, user_win_probality)
    rating_on_lose = get_rating(user.rank, k_factor, 0, user_win_probality)
    rating_on_draw = get_rating(user.rank, k_factor, 0.5, user_win_probality)
    return Rating(
        on_win=rating_on_win,
        on_lose=rating_on_lose,
        on_draw=rating_on_draw
    )

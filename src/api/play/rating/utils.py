def get_k_factor(user_rate: int) -> int:
    # https://chess-elo.com/k-factor-elo-ratings/
    # Such as in the US Chess Federation (USCF) K-Factor Rules
    if user_rate < 2100:
        return 32
    elif 2100 <= user_rate <= 2400:
        return 24
    else:
        return 16
    
def get_probality(rating_1: int, rating_2: int) -> float:
    return (1.0 / (1.0 + pow(10, ((rating_1-rating_2) / 400))))

def get_rating(rating: int, k: int, actual: int, expected: float) -> float:
    return rating + k*(actual - expected)

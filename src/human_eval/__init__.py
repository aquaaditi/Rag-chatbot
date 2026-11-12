"""
Human evaluation stage:  the cached scripts  ->  human ratings  ->  are the automatic metrics right?

    rubric.py    the questions + what every score means (factuality, audience fit, helpfulness)
    items.py     WHAT to rate: 15 scripts + the sentences the checker doubted (+ controls),
                 frozen in eval/human/items.json
    ratings.py   one rater's answers: eval/human/ratings_<rater>.json, saved after every item
    session.py   the blind rating loop in the terminal (resumable)
    analysis.py  means, majority labels, true share vs the checker, rater agreement, correlations
    export.py    eval/human/results.md

The ratings are written by PEOPLE - code never fills them in.
"""

from src.human_eval.export import save_report
from src.human_eval.items import Items, build_items
from src.human_eval.ratings import RaterFile, load_all
from src.human_eval.session import RatingSession

__all__ = ["Items", "RaterFile", "RatingSession", "build_items", "load_all", "save_report"]

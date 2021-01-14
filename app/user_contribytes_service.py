from app.db.database import SessionLocal
from app.db.models import UserContributes
from sqlalchemy import func
from sqlalchemy_filters import apply_filters

db = SessionLocal()


def get_most_active_user(year: int = None, month: int = None, day=None):
    query_params = {
        "year": year,
        "month": month,
        "day": day
    }

    filter_spec = [{'field': k, 'op': '==', 'value': v} for k, v in query_params.items() if v]

    query = db.query(UserContributes.user,
                     func.count(UserContributes.user),
                     func.array_agg(UserContributes.year),
                     func.array_agg(UserContributes.month),
                     func.array_agg(UserContributes.day),
                     ).group_by(
        UserContributes.user,
    ).order_by(
        func.count(UserContributes.user).desc())

    filtered_query = apply_filters(query, filter_spec)
    return filtered_query.first()

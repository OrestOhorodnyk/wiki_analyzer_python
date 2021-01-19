from app.db.database import SessionLocal
from app.db.models import UserContributes, UserContributeByTitle, ArticleTitleCount
from sqlalchemy import func
from sqlalchemy_filters import apply_filters

db = SessionLocal()


async def get_user_list():
    return db.query(UserContributes.user.distinct()).all()


async def topics_by_user(username: str):
    res = db.query(
        UserContributes.user,
        UserContributes.title,
        func.count(UserContributes.id_sk)
    ).filter(
        UserContributes.user.ilike(f'%{username}%')
    ).group_by(
        UserContributes.user,
        UserContributes.title
    ).order_by(
        func.count(UserContributes.id_sk).desc()
    ).all()

    return res


async def topics_by_user_rx(username: str):
    res = db.query(
        UserContributeByTitle
    ).filter(
        UserContributes.user.ilike(f'%{username}%')
    ).order_by(
        UserContributeByTitle.count.desc()
    ).first()

    return res


async def get_topic_typos_count():
    res = db.query(
        ArticleTitleCount
    ).order_by(
        ArticleTitleCount.count.desc()
    ).limit(10).all()

    return res


async def get_most_active_user(year: int = None, month: int = None, day=None):
    query_params = {
        "year": year,
        "month": month,
        "day": day
    }

    filter_spec = [{'field': k, 'op': '==', 'value': v} for k, v in query_params.items() if v]

    query = db.query(
        UserContributes.user,
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

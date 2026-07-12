import re

from sqlalchemy import text
from sqlalchemy.orm import Session


QUERY_STOP_WORDS = {
    "a",
    "an",
    "and",
    "about",
    "can",
    "could",
    "describe",
    "do",
    "does",
    "explain",
    "for",
    "how",
    "in",
    "is",
    "it",
    "me",
    "of",
    "please",
    "tell",
    "the",
    "to",
    "what",
    "why",
}


def normalize_retrieval_query(query: str) -> str:
    tokens = re.findall(r"[a-z0-9]+", query.lower())
    meaningful_tokens = [
        token
        for token in tokens
        if token not in QUERY_STOP_WORDS and len(token) > 1
    ]

    return " OR ".join(meaningful_tokens or tokens)


def retrieve_curriculum(
    db: Session,
    *,
    query: str,
    limit: int = 3,
) -> list[dict[str, str]]:
    normalized_query = normalize_retrieval_query(query)

    rows = db.execute(
        text(
            """
            SELECT
                external_id,
                topic,
                body
            FROM curriculum_content
            WHERE to_tsvector(
                'english',
                coalesce(topic, '') || ' ' || coalesce(body, '')
            ) @@ websearch_to_tsquery('english', :query)
            ORDER BY ts_rank_cd(
                to_tsvector(
                    'english',
                    coalesce(topic, '') || ' ' || coalesce(body, '')
                ),
                websearch_to_tsquery('english', :query)
            ) DESC
            LIMIT :limit
            """
        ),
        {
            "query": normalized_query,
            "limit": limit,
        },
    ).mappings()

    return [dict(row) for row in rows]

from sqlalchemy import text
from sqlalchemy.orm import Session


def retrieve_curriculum(
    db: Session,
    *,
    query: str,
    limit: int = 3,
) -> list[dict[str, str]]:
    rows = db.execute(
        text(
            """
            SELECT external_id, topic, body
            FROM curriculum_content
            WHERE to_tsvector(
                'english',
                topic || ' ' || body
            ) @@ websearch_to_tsquery('english', :query)
            ORDER BY ts_rank(
                to_tsvector('english', topic || ' ' || body),
                websearch_to_tsquery('english', :query)
            ) DESC
            LIMIT :limit
            """
        ),
        {"query": query, "limit": limit},
    ).mappings()

    return [dict(row) for row in rows]

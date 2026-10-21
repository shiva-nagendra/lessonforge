import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "lessonforge.db"


class MemoryStore:
    """Persistent SQLite-backed memory for LessonForge."""

    def __init__(self, db_path: str | Path = DEFAULT_DB_PATH):
        self.db_path = Path(db_path)

        self.db_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._initialize_database()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)

        connection.row_factory = sqlite3.Row

        return connection

    def _initialize_database(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS lesson_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic TEXT NOT NULL,
                    learner_level TEXT NOT NULL,
                    learning_goal TEXT,
                    final_status TEXT NOT NULL,
                    attempts INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS failure_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    criterion TEXT NOT NULL,
                    pattern TEXT NOT NULL,
                    recommended_action TEXT NOT NULL,
                    occurrences INTEGER NOT NULL DEFAULT 1,
                    last_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE (
                        criterion,
                        pattern,
                        recommended_action
                    )
                )
                """
            )

            connection.commit()

    def save_lesson_run(
        self,
        topic: str,
        learner_level: str,
        learning_goal: str | None,
        final_status: str,
        attempts: int,
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO lesson_runs (
                    topic,
                    learner_level,
                    learning_goal,
                    final_status,
                    attempts
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    topic,
                    learner_level,
                    learning_goal,
                    final_status,
                    attempts,
                ),
            )

            connection.commit()

    def save_failure_pattern(
        self,
        criterion: str,
        pattern: str,
        recommended_action: str,
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO failure_patterns (
                    criterion,
                    pattern,
                    recommended_action,
                    occurrences
                )
                VALUES (?, ?, ?, 1)

                ON CONFLICT (
                    criterion,
                    pattern,
                    recommended_action
                )
                DO UPDATE SET
                    occurrences = occurrences + 1,
                    last_seen_at = CURRENT_TIMESTAMP
                """,
                (
                    criterion,
                    pattern,
                    recommended_action,
                ),
            )

            connection.commit()

    def get_failure_patterns(
        self,
        criterion: str | None = None,
        limit: int = 5,
    ) -> list[dict]:
        query = """
            SELECT
                criterion,
                pattern,
                recommended_action,
                occurrences,
                last_seen_at
            FROM failure_patterns
        """

        parameters: tuple = ()

        if criterion:
            query += """
                WHERE criterion = ?
            """

            parameters = (criterion,)

        query += """
            ORDER BY occurrences DESC, last_seen_at DESC
            LIMIT ?
        """

        parameters = (*parameters, limit)

        with self._connect() as connection:
            rows = connection.execute(
                query,
                parameters,
            ).fetchall()

        return [dict(row) for row in rows]

    def get_recent_runs(
        self,
        limit: int = 10,
    ) -> list[dict]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    id,
                    topic,
                    learner_level,
                    learning_goal,
                    final_status,
                    attempts,
                    created_at
                FROM lesson_runs
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [dict(row) for row in rows]
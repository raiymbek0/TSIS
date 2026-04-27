import psycopg2
import sys

class Database:
    def __init__(self, config):
        try:
            self.conn = psycopg2.connect(**config)
            self.create_tables()
            print("Successfully connected to PostgreSQL")
        except psycopg2.OperationalError as e:
            print(f"Database connection error: {e}")
            print("\nCheck your password in config.py!")
            sys.exit()

    def create_tables(self):
        with self.conn.cursor() as cur:
            # Создаем таблицы для игроков и сессий
            cur.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL
                );
                CREATE TABLE IF NOT EXISTS game_sessions (
                    id SERIAL PRIMARY KEY,
                    player_id INTEGER REFERENCES players(id),
                    score INTEGER NOT NULL,
                    level_reached INTEGER NOT NULL,
                    played_at TIMESTAMP DEFAULT NOW()
                );
            """)
        self.conn.commit()

    def save_result(self, username, score, level):
        with self.conn.cursor() as cur:
            # Сохраняем игрока, если его нет
            cur.execute("INSERT INTO players (username) VALUES (%s) ON CONFLICT (username) DO NOTHING", (username,))
            # Получаем ID игрока
            cur.execute("SELECT id FROM players WHERE username = %s", (username,))
            player_id = cur.fetchone()[0]
            # Записываем результат игры
            cur.execute("INSERT INTO game_sessions (player_id, score, level_reached) VALUES (%s, %s, %s)",
                        (player_id, score, level))
        self.conn.commit()
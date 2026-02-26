import sqlite3
import json
from google.genai.types import Content

DB_FILE = "convo.db"


def init_db():
  conn = sqlite3.connect(DB_FILE)
  cursor = conn.cursor()
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS convos (
            channel_id TEXT,
            guild_id TEXT,
            context TEXT,
            history TEXT,
            PRIMARY KEY (channel_id, guild_id)
        )
    """)
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS ignored_users (
            channel_id TEXT,
            guild_id TEXT,
            user_id TEXT,
            PRIMARY KEY (channel_id, guild_id, user_id)
        )
    """)
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id TEXT,
            target_user TEXT,
            message TEXT,
            trigger_time REAL
        )
    """)
  conn.commit()
  conn.close()


def add_reminder(channel_id, target_user, message, trigger_time):
  conn = sqlite3.connect(DB_FILE)
  cursor = conn.cursor()
  cursor.execute(
      "INSERT INTO reminders (channel_id, target_user, message, trigger_time) VALUES (?, ?, ?, ?)",
      (str(channel_id), str(target_user), str(message), float(trigger_time))
  )
  conn.commit()
  conn.close()


def get_due_reminders(current_time):
  conn = sqlite3.connect(DB_FILE)
  cursor = conn.cursor()
  cursor.execute(
    "SELECT id, channel_id, target_user, message FROM reminders WHERE trigger_time <= ?", (float(current_time),))
  rows = cursor.fetchall()
  conn.close()
  return rows


def remove_reminder(reminder_id):
  conn = sqlite3.connect(DB_FILE)
  cursor = conn.cursor()
  cursor.execute("DELETE FROM reminders WHERE id = ?", (int(reminder_id),))
  conn.commit()
  conn.close()


def add_ignored_user(channel_id, guild_id, user_id):
  conn = sqlite3.connect(DB_FILE)
  cursor = conn.cursor()
  cursor.execute(
      "INSERT OR IGNORE INTO ignored_users (channel_id, guild_id, user_id) VALUES (?, ?, ?)",
      (str(channel_id), str(guild_id) if guild_id else "", str(user_id))
  )
  conn.commit()
  conn.close()


def remove_ignored_user(channel_id, guild_id, user_id):
  conn = sqlite3.connect(DB_FILE)
  cursor = conn.cursor()
  cursor.execute(
      "DELETE FROM ignored_users WHERE channel_id = ? AND guild_id = ? AND user_id = ?",
      (str(channel_id), str(guild_id) if guild_id else "", str(user_id))
  )
  conn.commit()
  conn.close()


def get_ignored_users(channel_id, guild_id):
  conn = sqlite3.connect(DB_FILE)
  cursor = conn.cursor()
  cursor.execute(
      "SELECT user_id FROM ignored_users WHERE channel_id = ? AND guild_id = ?",
      (str(channel_id), str(guild_id) if guild_id else "")
  )
  rows = cursor.fetchall()
  conn.close()
  return {int(row[0]) for row in rows}


def save_convo(channel_id, guild_id, context, history_objects):
  conn = sqlite3.connect(DB_FILE)
  cursor = conn.cursor()

  # Serialize the list of Content objects to JSON
  history_json = json.dumps([c.model_dump(mode="json")
                            for c in history_objects])

  cursor.execute("""
        INSERT OR REPLACE INTO convos (channel_id, guild_id, context, history)
        VALUES (?, ?, ?, ?)
    """, (str(channel_id), str(guild_id) if guild_id else "", context, history_json))

  conn.commit()
  conn.close()


def load_convo(channel_id, guild_id):
  conn = sqlite3.connect(DB_FILE)
  cursor = conn.cursor()
  cursor.execute("SELECT context, history FROM convos WHERE channel_id = ? AND guild_id = ?",
                 (str(channel_id), str(guild_id) if guild_id else ""))
  row = cursor.fetchone()
  conn.close()

  if row:
    context, history_json = row
    try:
      history_data = json.loads(history_json)
      # Deserialize the JSON back into Content objects
      history_objects = [Content.model_validate(c) for c in history_data]
      return context, history_objects
    except json.JSONDecodeError:
      return context, []
  return None, None

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
    conn.commit()
    conn.close()

def save_convo(channel_id, guild_id, context, history_objects):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Serialize the list of Content objects to JSON
    history_json = json.dumps([c.model_dump(mode="json") for c in history_objects])
    
    cursor.execute("""
        INSERT OR REPLACE INTO convos (channel_id, guild_id, context, history)
        VALUES (?, ?, ?, ?)
    """, (str(channel_id), str(guild_id) if guild_id else "None", context, history_json))
    
    conn.commit()
    conn.close()

def load_convo(channel_id, guild_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT context, history FROM convos WHERE channel_id = ? AND guild_id = ?", 
                   (str(channel_id), str(guild_id) if guild_id else "None"))
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

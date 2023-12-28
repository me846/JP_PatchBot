import sqlite3
import shutil
import os
import sys
from datetime import datetime

def delete_old_backups(db_path, max_backups=5):
    backup_folder = os.path.dirname(db_path)
    backup_prefix = os.path.basename(db_path) + '.backup_'

    backups = [f for f in os.listdir(backup_folder) if f.startswith(backup_prefix)]
    backups.sort(reverse=True)

    while len(backups) > max_backups:
        old_backup = backups.pop()
        os.remove(os.path.join(backup_folder, old_backup))
        print(f"Deleted old backup: {old_backup}")

def backup_database(db_path):
    backup_path = db_path + '.backup_' + datetime.now().strftime('%Y%m%d%H%M%S')
    shutil.copyfile(db_path, backup_path)
    print(f"Database backup created at {backup_path}")



def check_and_update_db_schema(conn):
    try:
        c = conn.cursor()

        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='recent_patch_notes'")
        if c.fetchone():
            c.execute('ALTER TABLE recent_patch_notes RENAME TO old_recent_patch_notes')

            c.execute('''
                CREATE TABLE recent_patch_notes (
                    game_type TEXT NOT NULL,
                    patch_number TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    image_url TEXT,
                    PRIMARY KEY (game_type)
                )
            ''')

            c.execute('SELECT * FROM old_recent_patch_notes')
            old_data = c.fetchall()
            for row in old_data:
                c.execute('''
                    INSERT INTO recent_patch_notes (game_type, patch_number, title, content, image_url)
                    VALUES (?, ?, ?, ?, ?)
                ''', row)

            c.execute('DROP TABLE old_recent_patch_notes')
        else:
            c.execute('''
                CREATE TABLE IF NOT EXISTS recent_patch_notes (
                    game_type TEXT NOT NULL,
                    patch_number TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    image_url TEXT,
                    PRIMARY KEY (game_type)
                )
            ''')
            
        c.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                notification_type TEXT NOT NULL,
                UNIQUE(guild_id, channel_id, notification_type)
            )
        ''')
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='old_notifications'")
        if c.fetchone():
            c.execute('''
                INSERT INTO notifications (guild_id, channel_id, notification_type)
                SELECT guild_id, channel_id, 'both' FROM old_notifications
                WHERE NOT EXISTS (
                    SELECT 1 FROM notifications WHERE guild_id = old_notifications.guild_id AND channel_id = old_notifications.channel_id
                )
            ''')
            print("データベースが更新されました。")
            
            c.execute("DROP TABLE old_notifications")
            c.execute('DROP TABLE old_recent_patch_notes')

        else:
            print("データベースの更新は必要ありませんでした。")

        conn.commit()
        
    except sqlite3.Error as e:
        print(f"データベースの更新中にエラーが発生しました: {e}", file=sys.stderr)
        conn.rollback()

def main():
    db_path = 'data/notifications.db'

    delete_old_backups(db_path, max_backups=5)
    if os.path.exists(db_path):
        backup_database(db_path)

    conn = sqlite3.connect(db_path)
    check_and_update_db_schema(conn)
    conn.close()

if __name__ == '__main__':
    main()
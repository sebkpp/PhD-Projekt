import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db_conn import get_db

DATA_FILE = os.path.join(os.path.dirname(__file__), '../data/avatar_visibility.json')

def main():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        visibilities = json.load(f)

    conn = get_db()
    cur = conn.cursor()

    for item in visibilities:
        name = item["name"]
        label = item["label"]

        # Prüfen, ob der Eintrag bereits existiert
        cur.execute("""
            SELECT avatar_visibility_id FROM avatar_visibility
            WHERE avatar_visibility_name = %s
        """, (name,))
        row = cur.fetchone()

        if row:
            # Optional: label aktualisieren, falls gewünscht
            cur.execute("""
                UPDATE avatar_visibility SET label = %s
                WHERE avatar_visibility_name = %s
            """, (label, name))
            print(f"🔄 Aktualisiert: {name} → {label}")
        else:
            # Neuen Eintrag einfügen
            cur.execute("""
                INSERT INTO avatar_visibility (avatar_visibility_name, label)
                VALUES (%s, %s)
            """, (name, label))
            print(f"🆕 Eingefügt: {name} → {label}")

    conn.commit()
    conn.close()
    print("✅ Avatar-Sichtbarkeiten importiert.")

if __name__ == '__main__':
    main()

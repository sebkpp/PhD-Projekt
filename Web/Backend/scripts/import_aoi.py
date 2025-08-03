import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db_conn import get_db

DATA_FILE = os.path.join(os.path.dirname(__file__), '../data/aoi_definitions.json')

def main():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        aois = json.load(f)

    conn = get_db()
    cur = conn.cursor()

    for aoi in aois:
        short_name = aoi['aoi']
        label = aoi['label']

        cur.execute("SELECT aoi_id FROM area_of_interest WHERE aoi = %s", (short_name,))
        exists = cur.fetchone()

        if exists:
            print(f"🔁 Aktualisiere AOI: {short_name}")
            cur.execute("""
                UPDATE area_of_interest SET label = %s
                WHERE aoi = %s
            """, (label, short_name))
        else:
            print(f"➕ Neuer AOI: {short_name}")
            cur.execute("""
                INSERT INTO area_of_interest (aoi, label)
                VALUES (%s, %s)
            """, (short_name, label))

    conn.commit()
    conn.close()
    print("✅ AOIs erfolgreich importiert.")

if __name__ == '__main__':
    main()

import json
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db_conn import get_db

DATA_FILE = os.path.join(os.path.dirname(__file__), '../data/stimuli_definitions.json')

def main():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        stimuli_data = json.load(f)

    conn = get_db()
    cur = conn.cursor()

    type_id_cache = {}

    for stim in stimuli_data:
        stim_type = stim['type']

        # Hole stimulus_type_id (gecached)
        if stim_type not in type_id_cache:
            cur.execute("SELECT stimulus_type_id FROM stimulus_type WHERE type_name = %s", (stim_type,))
            result = cur.fetchone()
            if not result:
                print(f"⚠️  Stimulus-Typ '{stim_type}' nicht gefunden – überspringe.")
                continue
            type_id_cache[stim_type] = result[0]
        type_id = type_id_cache[stim_type]

        name = stim['name']

        # Prüfen, ob Stimulus existiert
        cur.execute("""
            SELECT stimulus_id FROM stimuli
            WHERE name = %s AND stimulus_type_id = %s
        """, (name, type_id))
        row = cur.fetchone()

        if row:
            stimulus_id = row[0]
            print(f"🔄 Aktualisiere Stimulus: {name} (ID {stimulus_id})")
        else:
            # Neuer Stimulus
            cur.execute("""
                INSERT INTO stimuli (name, stimulus_type_id)
                VALUES (%s, %s)
                RETURNING stimulus_id
            """, (name, type_id))
            stimulus_id = cur.fetchone()[0]
            print(f"🆕 Neuer Stimulus: {name} (ID {stimulus_id})")

        # Typ-spezifisch behandeln
        if stim_type == 'auditory':
            # Upsert für stimulus_auditory
            cur.execute("SELECT 1 FROM stimulus_auditiv WHERE stimulus_id = %s", (stimulus_id,))
            if cur.fetchone():
                cur.execute("""
                    UPDATE stimulus_auditiv SET frequency = %s, volume = %s
                    WHERE stimulus_id = %s
                """, (stim['frequency'], stim['volume'], stimulus_id))
            else:
                cur.execute("""
                    INSERT INTO stimulus_auditiv (stimulus_id, frequency, volume)
                    VALUES (%s, %s, %s)
                """, (stimulus_id, stim['frequency'], stim['volume']))

        elif stim_type == 'tactile':
            cur.execute("SELECT 1 FROM stimulus_tactile WHERE stimulus_id = %s", (stimulus_id,))
            if cur.fetchone():
                cur.execute("""
                    UPDATE stimulus_tactile SET pattern = %s, intensity = %s
                    WHERE stimulus_id = %s
                """, (stim['pattern'], stim['intensity'], stimulus_id))
            else:
                cur.execute("""
                    INSERT INTO stimulus_tactile (stimulus_id, pattern, intensity)
                    VALUES (%s, %s, %s)
                """, (stimulus_id, stim['pattern'], stim['intensity']))

        elif stim_type == 'visual':
            cur.execute("SELECT 1 FROM stimulus_visual WHERE stimulus_id = %s", (stimulus_id,))
            if cur.fetchone():
                cur.execute("""
                    UPDATE stimulus_visual SET stimulus_name = %s
                    WHERE stimulus_id = %s
                """, (name, stimulus_id))
            else:
                cur.execute("""
                    INSERT INTO stimulus_visual (stimulus_id, stimulus_name)
                    VALUES (%s, %s)
                """, (stimulus_id, name))


    conn.commit()
    conn.close()
    print("✅ Stimuli-Import abgeschlossen.")

if __name__ == '__main__':
    main()

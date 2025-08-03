from flask import Blueprint, request, jsonify
from db_conn import get_db
import traceback

trials_bp = Blueprint('trials', __name__)
@trials_bp.route('/trials', methods=['POST'])
def save_trial_config():
    data = request.get_json()
    experiment_id = data.get("experiment_id")
    trials = data.get("trials")

    if not experiment_id or not trials:
        return jsonify({"error": "experiment_id und trials sind erforderlich"}), 400

    conn = get_db()
    cur = conn.cursor()

    # Stimuli-Typ Mapping (z.B. stimulus_id 5 → VIS)
    cur.execute("""
                    SELECT s.stimulus_id, st.type_name
                    FROM stimuli s
                    JOIN stimulus_type st ON s.stimulus_type_id = st.stimulus_type_id
                """)

    # Mapping long label → Kurzform
    type_name_to_code = {
        'visual': 'VIS',
        'auditory': 'AUD',
        'tactile': 'TAK'
    }

    stimulus_type_map = {
        row["stimulus_id"]: type_name_to_code.get(row["type_name"].lower())
        for row in cur.fetchall()
    }

    try:
        for trial in trials:
            trial_number = trial["trial_number"]

            cur.execute(
                "INSERT INTO trial (experiment_id, trial_number) VALUES (%s, %s) RETURNING trial_id",
                (experiment_id, trial_number)
            )
            trial_id = cur.fetchone()["trial_id"]


            for _, config in trial["participants"].items():
                avatar_id = config["avatar"]
                participant_id = config["participant_id"]  # von payload
                selected_stimuli_ids = list(config.get("selectedStimuli", {}).values())

                stimulus_combination_id = None
                if selected_stimuli_ids:
                    # Modalitäten-Kürzel erzeugen (z.B. VIS,AUD)
                    type_abbrs = []
                    for sid in selected_stimuli_ids:
                        type_code = stimulus_type_map.get(int(sid))
                        if not type_code:
                            raise ValueError(f"Kein Stimulus-Typ für stimulus_id={sid} gefunden.")
                        type_abbrs.append(type_code)

                    readable_combination = ','.join(sorted(type_abbrs))

                    cur.execute(
                        """
                        INSERT INTO stimuli_combination (combination)
                        VALUES (%s)
                        ON CONFLICT (combination) DO NOTHING
                        RETURNING stimulus_combination_id
                        """,
                        (readable_combination,)
                    )

                    row = cur.fetchone()
                    if row is None:
                        # Kombination existiert schon → ID manuell holen
                        cur.execute(
                            "SELECT stimulus_combination_id FROM stimuli_combination WHERE combination = %s",
                            (readable_combination,)
                        )
                        stimulus_combination_id = cur.fetchone()["stimulus_combination_id"]
                    else:
                        stimulus_combination_id = row["stimulus_combination_id"]

                    for stimulus_id in selected_stimuli_ids:
                        # Prüfen, ob die Kombination schon existiert
                        cur.execute(
                            """
                            SELECT 1 FROM stimulus_combination_item
                            WHERE stimulus_combination_id = %s AND stimulus_id = %s
                            """,
                            (stimulus_combination_id, stimulus_id)
                        )
                        exists = cur.fetchone()

                        # Nur einfügen, wenn sie noch nicht existiert
                        if not exists:
                            cur.execute(
                                """
                                INSERT INTO stimulus_combination_item (stimulus_combination_id, stimulus_id)
                                VALUES (%s, %s)
                                """,
                                (stimulus_combination_id, stimulus_id)
                            )

                cur.execute(
                    """
                    INSERT INTO trial_participant_item (
                        trial_id, participant_id, avatar_visibility_id, stimulus_combination_id
                    ) VALUES (%s, %s, %s, %s)
                    """,
                    (trial_id, int(participant_id), avatar_id, stimulus_combination_id)
                )

        conn.commit()
        return jsonify({"status": "ok", "message": f"{len(trials)} Trials erfolgreich gespeichert."}), 201

    except Exception as e:
        if conn:
            conn.rollback()
        print("❌ Fehler beim Speichern der Trial-Konfiguration:")
        traceback.print_exc()
        return jsonify({"error": "Ein interner Fehler ist aufgetreten.", "details": str(e)}), 500

    finally:
        if conn:
            cur.close()
            conn.close()


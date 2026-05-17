import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from sqlalchemy import text
from Backend.db_session import engine

from Backend.db_session import engine as _engine

import import_stimulus_type
import import_stimuli
import import_avatar_visibility
import import_aoi
import import_questionnaire
import import_participant
import import_study
import import_study_config
import import_experiment
import import_trial
import import_trial_slot
import import_trial_participant_slot
import import_trial_slot_stimulus
import import_study_questionnaire
import import_study_stimuli
import import_handover
import import_eye_tracking
import import_questionnaire_response

# Tables to truncate when resetting mock data (child → parent order).
# Static tables are included so IDs are predictable (start at 1) for mock FK references.
RESET_SQL = """
TRUNCATE TABLE
    questionnaire_response,
    study_questionnaire,
    experiment_questionnaire,
    study_stimuli,
    trial_slot_stimulus,
    trial_participant_slot,
    handover,
    eye_tracking,
    trial_slot,
    trial,
    experiment,
    study_config,
    study,
    participant,
    questionnaire_item,
    questionnaire,
    stimulus_combination_item,
    stimulus_visual,
    stimulus_auditiv,
    stimulus_tactile,
    stimuli,
    stimuli_combination,
    stimulus_type,
    area_of_interest,
    avatar_visibility
RESTART IDENTITY CASCADE;
"""


def reset_tables():
    with engine.connect() as conn:
        conn.execute(text(RESET_SQL))
        conn.commit()
    print("Tables truncated and sequences reset.\n")


def import_static():
    print("Importing stimulus types...")
    import_stimulus_type.main()

    print("Importing stimuli...")
    import_stimuli.main()

    print("Importing avatar visibilities...")
    import_avatar_visibility.main()

    print("Importing areas of interest...")
    import_aoi.main()

    print("Importing questionnaires...")
    import_questionnaire.main()


def import_mock():
    print("Importing participants...")
    import_participant.main()

    print("Importing studies...")
    import_study.main()

    print("Importing study configs...")
    import_study_config.main()

    print("Importing experiments...")
    import_experiment.main()

    print("Importing trials...")
    import_trial.main()

    print("Importing trial slots...")
    import_trial_slot.main()

    print("Importing trial participant slots...")
    import_trial_participant_slot.main()

    print("Importing trial slot stimuli...")
    import_trial_slot_stimulus.main()

    print("Importing study questionnaires...")
    import_study_questionnaire.main()

    print("Importing study stimuli...")
    import_study_stimuli.main()

    print("Importing handovers...")
    import_handover.main()

    print("Importing eye tracking...")
    import_eye_tracking.main()

    print("Importing questionnaire responses...")
    import_questionnaire_response.main()

    _resync_sequences()


SEQUENCE_RESYNC_SQL = """
SELECT setval('experiment_experiment_id_seq',                COALESCE((SELECT MAX(experiment_id)       FROM experiment),        0));
SELECT setval('trial_trial_id_seq',                          COALESCE((SELECT MAX(trial_id)            FROM trial),             0));
SELECT setval('trial_slot_trial_slot_id_seq',                COALESCE((SELECT MAX(trial_slot_id)       FROM trial_slot),        0));
SELECT setval('sudy_study_id_seq',                           COALESCE((SELECT MAX(study_id)            FROM study),             0));
SELECT setval('participant_participant_id_seq',               COALESCE((SELECT MAX(participant_id)      FROM participant),       0));
SELECT setval('questionaire_questionnaire_id_seq',           COALESCE((SELECT MAX(questionnaire_id)    FROM questionnaire),     0));
SELECT setval('questionaire_item_questionnaire_item_id_seq', COALESCE((SELECT MAX(questionnaire_item_id) FROM questionnaire_item), 0));
SELECT setval('questionare_response_qestionnaire_response_id_seq', COALESCE((SELECT MAX(questionnaire_response_id) FROM questionnaire_response), 0));
SELECT setval('handover_handover_id_seq', COALESCE((SELECT MAX(handover_id) FROM handover), 0));
"""


def _resync_sequences():
    with _engine.connect() as conn:
        for stmt in SEQUENCE_RESYNC_SQL.strip().split(';'):
            stmt = stmt.strip()
            if stmt:
                conn.execute(text(stmt))
        conn.commit()
    print("Sequences resynced to table maxima.")


def main():
    print("⚠️  WARNING: This script will DELETE ALL data in the database and reimport.")
    confirm = input("Type 'yes' to continue: ").strip().lower()
    if confirm != 'yes':
        print("Aborted.")
        return

    print("\nResetting all tables...")
    reset_tables()

    print("--- Static data ---")
    import_static()

    answer = input("\nImport mock data? (y/n): ").strip().lower()
    if answer == 'y':
        print("\n--- Mock data ---")
        import_mock()

    print("\n✅ All imports completed successfully.")


if __name__ == '__main__':
    main()

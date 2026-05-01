import import_stimulus_type
import import_stimuli
import import_avatar_visibility
import import_aoi
import import_participant
import import_questionnaire
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


def main():
    # --- No dependencies ---
    print("Importing stimulus types...")
    import_stimulus_type.main()

    print("Importing avatar visibilities...")
    import_avatar_visibility.main()

    print("Importing areas of interest...")
    import_aoi.main()

    print("Importing participants...")
    import_participant.main()

    print("Importing questionnaires and items...")
    import_questionnaire.main()

    # --- Depends on stimulus_type ---
    print("Importing stimuli...")
    import_stimuli.main()

    # --- Study layer ---
    print("Importing study...")
    import_study.main()

    print("Importing study configs...")
    import_study_config.main()

    print("Importing experiments...")
    import_experiment.main()

    print("Importing trials...")
    import_trial.main()

    # --- Trial linking tables ---
    print("Importing trial slots...")
    import_trial_slot.main()

    print("Importing trial participant slots...")
    import_trial_participant_slot.main()

    print("Importing trial slot stimuli...")
    import_trial_slot_stimulus.main()

    # --- Study associations ---
    print("Importing study questionnaires...")
    import_study_questionnaire.main()

    print("Importing study stimuli...")
    import_study_stimuli.main()

    # --- Depends on trial + participants ---
    print("Importing handovers...")
    import_handover.main()

    print("Importing eye tracking...")
    import_eye_tracking.main()

    print("Importing questionnaire responses...")
    import_questionnaire_response.main()

    print("\n✅ All imports completed successfully.")


if __name__ == '__main__':
    main()

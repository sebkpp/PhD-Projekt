import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import import_stimulus_type
import import_stimuli
import import_avatar_visibility
import import_aoi
import import_questionnaire


def main():
    print("Importing stimulus types...")
    import_stimulus_type.main()

    print("Importing stimuli...")
    import_stimuli.main()

    print("Importing avatar visibilities...")
    import_avatar_visibility.main()

    print("Importing areas of interest...")
    import_aoi.main()

    print("Importing questionnaires and items...")
    import_questionnaire.main()

    print("\nAll required static data imported successfully.")


if __name__ == '__main__':
    main()

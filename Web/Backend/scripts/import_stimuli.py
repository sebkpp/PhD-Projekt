import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from Backend.db_session import SessionLocal
from Backend.models.stimulus import StimulusType, Stimulus, StimulusVisual, StimulusAuditiv, StimulusTactile

DATA_FILE = os.path.join(os.path.dirname(__file__), '../data/static/stimuli_definitions.json')


def main():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        stimuli_data = json.load(f)

    db = SessionLocal()
    try:
        type_cache = {}

        for s in stimuli_data:
            type_name = s['type']

            if type_name not in type_cache:
                st = db.query(StimulusType).filter_by(type_name=type_name).first()
                if not st:
                    print(f"⚠️  StimulusType '{type_name}' not found – skipping {s['name']}")
                    continue
                type_cache[type_name] = st.stimulus_type_id

            type_id = type_cache[type_name]

            existing = db.query(Stimulus).filter_by(name=s['name'], stimulus_type_id=type_id).first()
            if existing:
                stimulus_id = existing.stimulus_id
                print(f"🔄 Already exists: {s['name']} (DB ID {stimulus_id})")
            else:
                kwargs = dict(name=s['name'], stimulus_type_id=type_id)
                if 'stimulus_id' in s:
                    kwargs['stimulus_id'] = s['stimulus_id']
                new_stim = Stimulus(**kwargs)
                db.add(new_stim)
                db.flush()
                stimulus_id = new_stim.stimulus_id
                print(f"🆕 Inserted: {s['name']} (DB ID {stimulus_id})")

            if type_name == 'visual':
                if not db.query(StimulusVisual).filter_by(stimulus_id=stimulus_id).first():
                    db.add(StimulusVisual(stimulus_id=stimulus_id, stimulus_name=s['name']))
            elif type_name == 'auditory':
                if not db.query(StimulusAuditiv).filter_by(stimulus_id=stimulus_id).first():
                    db.add(StimulusAuditiv(stimulus_id=stimulus_id, frequency=s['frequency'], volume=s['volume']))
            elif type_name == 'tactile':
                if not db.query(StimulusTactile).filter_by(stimulus_id=stimulus_id).first():
                    db.add(StimulusTactile(stimulus_id=stimulus_id, pattern=s['pattern'], intensity=s['intensity']))

        db.commit()
        print("✅ Stimuli imported.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == '__main__':
    main()

import sys
from pathlib import Path

# Add Web/ to sys.path so Backend package is importable.
# __file__ is always the absolute path of this file, so this resolves
# correctly regardless of where Jupyter is started from.
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "Web"))

from Backend.db_session import engine  # already exported at module level in db_session.py
import pandas as pd
from sqlalchemy import text


def load_handover(study_id=None, experiment_id=None) -> pd.DataFrame:
    """Load handover records, optionally filtered by study or experiment."""
    query = "SELECT * FROM handover h JOIN trial t ON h.trial_id = t.trial_id"
    filters = []
    params = {}
    if experiment_id is not None:
        filters.append("t.experiment_id = :experiment_id")
        params["experiment_id"] = experiment_id
    if study_id is not None:
        filters.append(
            "t.experiment_id IN "
            "(SELECT experiment_id FROM experiment WHERE study_id = :study_id)"
        )
        params["study_id"] = study_id
    if filters:
        query += " WHERE " + " AND ".join(filters)
    with engine.connect() as conn:
        return pd.read_sql(text(query), conn, params=params)  # params={} is safe when empty


def load_eyetracking(study_id=None, experiment_id=None) -> pd.DataFrame:
    """Load eye-tracking fixation records from the eye_tracking table."""
    query = (
        "SELECT et.* FROM eye_tracking et "
        "JOIN handover h ON et.handover_id = h.handover_id "
        "JOIN trial t ON h.trial_id = t.trial_id"
    )
    filters = []
    params = {}
    if experiment_id is not None:
        filters.append("t.experiment_id = :experiment_id")
        params["experiment_id"] = experiment_id
    if study_id is not None:
        filters.append(
            "t.experiment_id IN "
            "(SELECT experiment_id FROM experiment WHERE study_id = :study_id)"
        )
        params["study_id"] = study_id
    if filters:
        query += " WHERE " + " AND ".join(filters)
    with engine.connect() as conn:
        return pd.read_sql(text(query), conn, params=params)


def load_participants() -> pd.DataFrame:
    """Load all participant records."""
    with engine.connect() as conn:
        return pd.read_sql(text("SELECT * FROM participant"), conn)


def load_questionnaire_responses(study_id=None) -> pd.DataFrame:
    """Load questionnaire responses joined with item metadata.
    Note: only study_id filtering is supported (no experiment_id filter).
    """
    query = (
        "SELECT qr.*, qi.item_name, qi.item_label, q.name AS questionnaire_name "
        "FROM questionnaire_response qr "
        "JOIN questionnaire_item qi ON qr.questionnaire_item_id = qi.questionnaire_item_id "
        "JOIN questionnaire q ON qi.questionnaire_id = q.questionnaire_id"
    )
    params = {}
    if study_id is not None:
        query += (
            " JOIN trial t ON qr.trial_id = t.trial_id "
            "WHERE t.experiment_id IN "
            "(SELECT experiment_id FROM experiment WHERE study_id = :study_id)"
        )
        params["study_id"] = study_id
    with engine.connect() as conn:
        return pd.read_sql(text(query), conn, params=params)


if __name__ == "__main__":
    # Smoke test — run with: cd Web/ && uv run python ../notebooks/utils/db.py
    # Requires a running PostgreSQL instance and Web/Backend/.env to be present.
    print("Running smoke test...")
    df_p = load_participants()
    print(f"  participants:  {df_p.shape}")
    df_h = load_handover()
    print(f"  handover:      {df_h.shape}")
    df_et = load_eyetracking()
    print(f"  eye_tracking:  {df_et.shape}")
    df_qr = load_questionnaire_responses()
    print(f"  questionnaire: {df_qr.shape}")
    print("OK")

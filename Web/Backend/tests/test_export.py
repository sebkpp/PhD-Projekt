import pytest
from Backend.services.data_analysis.export_service import export_handovers_csv, export_handovers_xlsx


def test_export_csv_basic():
    handovers = [
        {"id": 1, "trial_id": 10, "duration_ms": 320, "is_error": False},
        {"id": 2, "trial_id": 10, "duration_ms": 290, "is_error": False},
    ]
    result = export_handovers_csv(handovers)
    assert isinstance(result, bytes)
    text = result.decode("utf-8")
    assert "id,trial_id,duration_ms,is_error" in text
    assert "320" in text


def test_export_csv_empty():
    result = export_handovers_csv([])
    assert result == b""


def test_export_xlsx_basic():
    handovers = [
        {"id": 1, "trial_id": 10, "duration_ms": 320},
        {"id": 2, "trial_id": 10, "duration_ms": 290},
    ]
    result = export_handovers_xlsx(handovers)
    assert isinstance(result, bytes)
    assert len(result) > 0
    # XLSX Signatur: PK (ZIP-Header)
    assert result[:2] == b"PK"


def test_export_xlsx_empty():
    result = export_handovers_xlsx([])
    assert isinstance(result, bytes)
    assert result[:2] == b"PK"  # Leere XLSX ist trotzdem ein valides ZIP

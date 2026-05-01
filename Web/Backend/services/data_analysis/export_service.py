"""
Datenexport-Service: CSV und XLSX für Handover-Daten.
"""
from __future__ import annotations
import io
import csv
import pandas as pd


def export_handovers_csv(handovers: list[dict]) -> bytes:
    """
    Exportiert Handover-Daten als UTF-8 encoded CSV.
    handovers: Liste von Dicts mit Handover-Feldern
    Returns: bytes (UTF-8 encoded CSV)
    """
    if not handovers:
        return b""

    output = io.StringIO()
    fieldnames = list(handovers[0].keys())
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(handovers)
    return output.getvalue().encode("utf-8")


def export_handovers_xlsx(handovers: list[dict]) -> bytes:
    """
    Exportiert Handover-Daten als XLSX (Excel).
    Returns: bytes (XLSX binary)
    """
    if not handovers:
        df = pd.DataFrame()
    else:
        df = pd.DataFrame(handovers)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Handovers")
    return output.getvalue()

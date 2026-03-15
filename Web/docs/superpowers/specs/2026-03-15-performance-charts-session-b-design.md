# Design-Spec: Performance Charts — Session B

**Datum:** 2026-03-15
**Branch:** 20-web-interface-for-data-collection
**Referenz:** `docs/superpowers/specs/2026-03-15-analysis-ui-integration-design.md` (Session A)
**Status:** Draft

---

## 1. Ziel

Zwei PlaceholderCharts im Performance-Tab der `ExperimentAnalysisPage` ersetzen:

1. **ViolinPlotPlotly** — Verteilung der Handover-Dauern pro Trial als Violinplot
2. **ErrorRateBar** — Fehlerrate (fehlgeschlagene Handovers) pro Trial als Balkendiagramm

Kein neuer Backend-Endpoint, kein neuer Frontend-Hook — beide Komponenten nutzen
die Daten von `usePerformanceMetrics` / `fetchPerformanceMetrics` (bereits vorhanden).

---

## 2. Studiendesign-Kontext

`ExperimentAnalysisPage` zeigt **deskriptive** Analyse eines einzelnen Experiment-Paares.
Trial = Bedingung (within-subject, permutiert). Inferenzielle Tests gehören auf Studienebene.
Beide neuen Charts zeigen Daten **pro Trial** (entspricht einer Bedingung).

---

## 3. Backend-Erweiterung

### 3.1 Datei

`Backend/services/data_analysis/performance_analysis_service.py`

### 3.2 Änderung

In `analyze_experiment_performance` wird pro Trial zusätzlich die Fehlerrate berechnet.
`Handover` hat die Felder `is_error: Boolean` und `error_type: String` (nullable).

Die drei neuen Felder werden am Ende des Trial-Stats-Blocks ergänzt (nach den bestehenden
`total_values`, `phase1_*`, `phase2_*`, `phase3_*` Feldern):

```python
stats["error_count"] = sum(1 for h in handovers if h.is_error)
stats["total_count"] = len(handovers)
stats["error_rate"] = (
    stats["error_count"] / stats["total_count"]
    if stats["total_count"] > 0
    else 0.0
)
```

### 3.3 Auswirkung auf bestehende Consumers

Additiv — keine bestehenden Felder werden verändert. Bestehende Tests und
Frontend-Komponenten sind nicht betroffen.

### 3.4 Test

In `Backend/tests/test_analysis.py` wird ein neuer Smoke-Test ergänzt:

```python
def test_experiment_performance_includes_error_rate(client, experiment_id):
    """Performance response must include error_rate, error_count, total_count per trial."""
    resp = client.get(f"/analysis/experiment/{experiment_id}/performance")
    assert resp.status_code == 200
    data = resp.json()
    for trial_stats in data.get("by_trial", {}).values():
        assert "error_rate" in trial_stats
        assert "error_count" in trial_stats
        assert "total_count" in trial_stats
        assert 0.0 <= trial_stats["error_rate"] <= 1.0
```

---

## 4. ViolinPlotPlotly.jsx

### 4.1 Datei

`src/features/Analysis/components/charts/ViolinPlotPlotly.jsx`

### 4.2 Props

```jsx
ViolinPlotPlotly({ boxplotData, chartRef, buttonRef, onExport })
```

`boxplotData` hat identische Struktur wie bei `BoxplotPlotly`:
```js
[{
    name: string,      // Trial-ID / Label
    y: number[],       // Rohe Handover-Dauern (total_values)
    min: number,
    q1: number,
    median: number,
    q3: number,
    max: number,
}]
```

### 4.3 Plotly-Konfiguration

- `type: "violin"`
- `box: { visible: true }` — eingebetteter Boxplot
- `meanline: { visible: true }` — Mittelwert-Linie
- `points: "outliers"` — nur Ausreißer als Punkte
- Gleiche Farbpalette wie `BoxplotPlotly`: `["#8884d8", "#82ca9d", "#ffc658", "#ff7300", "#00bcd4", "#e91e63"]`
- Dunkles Design: `paper_bgcolor: "#23272f"`, `plot_bgcolor: "#23272f"`, `font: { color: "#fff" }`
- Y-Achse: `title: "Dauer (s)"`
- X-Achse: `title: "Trial"`
- Legende: horizontal, zentriert, unter dem Chart (`y: -0.25`)
- `dragmode: false`, `displayModeBar: false`
- Höhe: `350px`, `width: "100%"`

### 4.4 Export-Button

Identisch zu `BoxplotPlotly`: Button mit `ref={buttonRef}`, `onClick={onExport}`,
Label "⬇️ PNG", Styling `background: "#222"`, `border: "1px solid #555"`.

### 4.5 Container-Styling

Identisch zu `BoxplotPlotly`:
```jsx
style={{
    border: "1px solid #444",
    borderRadius: "12px",
    background: "#23272f",
    boxShadow: "0 2px 8px #0002",
    padding: "1.5rem",
    marginBottom: "2rem",
}}
```

Titel: `<h3>Violinplot pro Trial</h3>` (mit `export-hide` Klasse).

---

## 5. ErrorRateBar.jsx

### 5.1 Datei

`src/features/Analysis/components/experiment/ErrorRateBar.jsx`

### 5.2 Props

```jsx
ErrorRateBar({ chartData })
```

`chartData` ist das gesamte Objekt von `usePerformanceMetrics` (enthält `by_trial`).

### 5.3 Datentransformation

```js
const barData = Object.entries(chartData.by_trial ?? {}).map(([id, m]) => ({
    name: id,
    errorRate: parseFloat(((m.error_rate ?? 0) * 100).toFixed(1)),
    errorCount: m.error_count ?? 0,
    totalCount: m.total_count ?? 0,
}));
```

### 5.4 Recharts-Konfiguration

- `BarChart` mit `ResponsiveContainer width="100%" height={250}`
- `XAxis dataKey="name"` — Trial-Labels
- `YAxis domain={[0, 100]}` — Prozent (0–100%)
- `YAxis label={{ value: "%", angle: -90, position: "insideLeft" }}`
- `CartesianGrid strokeDasharray="3 3"`
- `Bar dataKey="errorRate" fill="#e91e63"` — Pink für Fehler (konsistent mit Farbpalette)
- `Tooltip formatter={(v, n, p) => [`${v}% (${p.payload.errorCount}/${p.payload.totalCount})`, "Fehlerrate"]}`

### 5.5 Leer-Zustand

Wenn alle `error_rate === 0`: kleinen Hinweis-Text anzeigen:
```jsx
{barData.every(d => d.errorRate === 0) && (
    <p className="text-xs text-gray-500 mt-1">Keine Fehler in diesem Experiment.</p>
)}
```

### 5.6 Container-Styling

Kein eigener Rahmen-Container — `PerformanceCharts.jsx` setzt `<h3>` und rendert `ErrorRateBar` direkt.

---

## 6. Integration in PerformanceCharts.jsx

### 6.1 Datei

`src/features/Analysis/components/experiment/PerformanceCharts.jsx`

### 6.2 Neue Imports

```jsx
import ViolinPlotPlotly from "@/features/Analysis/components/charts/ViolinPlotPlotly.jsx";
import ErrorRateBar from "@/features/Analysis/components/experiment/ErrorRateBar.jsx";
```

`PlaceholderChart`-Import kann entfernt werden (wenn keine anderen Platzhalter mehr im File).

### 6.3 Ersetzung der PlaceholderCharts

```jsx
// ALT:
<PlaceholderChart label="Violinplot pro Bedingung (kommt in Session B)" />
<PlaceholderChart label="Fehlerrate pro Bedingung (kommt in Session B)" />

// NEU:
<ViolinPlotPlotly
    boxplotData={boxplotData}
    chartRef={violinRef}
    buttonRef={violinBtnRef}
    onExport={() => exportChart(violinRef, violinBtnRef, "violinplot")}
/>
<h3 className="mt-6 mb-2 text-base font-medium">Fehlerrate pro Handover</h3>
<ErrorRateBar chartData={chartData} />
```

### 6.4 Neue Refs

`PerformanceCharts.jsx` nutzt bereits `useChartExport` für den Boxplot. Gleiche Logik
für den Violinplot:

```jsx
const { chartRef: violinRef, buttonRef: violinBtnRef, exportChart } = useChartExport();
```

Prüfen ob `useChartExport` mehrfach aufrufbar ist oder ob Refs manuell angelegt werden
müssen — falls letzeres, `useRef` direkt verwenden.

---

## 7. Dateistruktur nach Session B (Performance)

```
Backend/
└── services/data_analysis/performance_analysis_service.py   MODIFY (+3 Felder)
    tests/test_analysis.py                                    MODIFY (+1 Test)

src/features/Analysis/
├── components/
│   ├── charts/
│   │   └── ViolinPlotPlotly.jsx                             CREATE
│   └── experiment/
│       ├── ErrorRateBar.jsx                                  CREATE
│       └── PerformanceCharts.jsx                             MODIFY
```

---

## 8. Nicht in diesem Spec

- Gaze-Timeline, PhaseAOIHeatmap, TransitionSankey, SaccadeRateBar, PPIBar → Session B ET-Charts
- NASA-TLX, SUS, AttrakDiff → Session B UX-Charts
- CorrelationMatrix → Session B Vergleich-Charts
- PosthocHeatmap → Session B Vergleich-Charts

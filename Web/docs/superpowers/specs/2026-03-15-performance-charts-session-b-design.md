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

In `analyze_experiment_performance` wird pro Trial die Fehlerrate berechnet.
`Handover` hat die Felder `is_error: Boolean` und `error_type: String` (nullable).

**Wichtig:** Der bestehende Timestamp-Filter (`if not all([...]) continue`) überspringt
Handovers ohne vollständige Phasen-Zeitstempel. Da fehlerhafte Handovers oft genau diese
Zeitstempel nicht haben, darf die Fehlerrate **nicht** aus `grouped_by_trial` abgeleitet
werden — sondern aus den **rohen, ungefilterten** Handovers pro Trial.

**Schritt 1:** Vor dem Timestamp-Filter-Loop eine separate Gruppierung anlegen:

```python
# NACH Zeile 96 (handovers = h_repo.get_handovers_by_experiment(experiment_id)):
handovers_by_trial: dict[int, list] = defaultdict(list)
for h in handovers:
    handovers_by_trial[h.trial_id].append(h)
```

**Schritt 2:** Im `stats_by_trial`-Loop (nach Zeile 143, `stats["total_values"] = ...`)
die drei Felder ergänzen:

```python
for trial_id, data in grouped_by_trial.items():
    stats = calc_stats(data)
    stats["total_values"] = [d["total"] for d in data]
    # Fehlerrate aus ALLEN Handovers des Trials (inkl. gefilterter)
    trial_handovers = handovers_by_trial[trial_id]
    stats["error_count"] = sum(1 for h in trial_handovers if h.is_error)
    stats["total_count"] = len(trial_handovers)
    stats["error_rate"] = (
        stats["error_count"] / stats["total_count"]
        if stats["total_count"] > 0
        else 0.0
    )
    stats_by_trial[trial_id] = sanitize_stats(stats)
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
    by_trial = data.get("by_trial", {})
    assert len(by_trial) > 0, "Test requires at least one trial with complete handover data"
    for trial_stats in by_trial.values():
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
    y: number[],       // Rohe Handover-Dauern (total_values) — EINZIGES Feld das Plotly nutzt
    min: number,       // Nur für Konsistenz mit BoxplotPlotly, vom Violin-Trace ignoriert
    q1: number,
    median: number,
    q3: number,
    max: number,
}]
```

**Hinweis:** Plotly `type: "violin"` berechnet alle Verteilungsstatistiken intern aus `y`.
Die Felder `min`, `q1`, `median`, `q3`, `max` werden vom Violin-Trace **nicht** genutzt —
sie sind nur für Props-Konsistenz mit `BoxplotPlotly` vorhanden und dürfen nicht als
Plotly-Trace-Properties übergeben werden.

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
- Container: `minWidth: 0` (identisch zu `BoxplotPlotly`, notwendig für flex-Layout)

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

Wenn Daten vorhanden aber alle `errorRate === 0`: kleinen Hinweis-Text anzeigen.
Guard gegen leeres Array (`[].every(...)` gibt `true` zurück in JavaScript):
```jsx
{barData.length > 0 && barData.every(d => d.errorRate === 0) && (
    <p className="text-xs text-gray-500 mt-1">Keine Fehler in diesem Experiment.</p>
)}
```

### 5.6 Container-Styling

Kein eigener Rahmen-Container — `PerformanceCharts.jsx` setzt `<h2>Fehlerrate pro Trial</h2>`
und rendert `ErrorRateBar` direkt darunter.

### 5.7 PNG-Export

`ErrorRateBar` hat **keinen** PNG-Export-Button. Recharts unterstützt kein natives
PNG-Export analog zu Plotly. Diese Einschränkung ist akzeptiert.

---

## 6. Integration

### 6.1 Änderungen in PerformanceCharts.jsx

**Datei:** `src/features/Analysis/components/experiment/PerformanceCharts.jsx`

`PerformanceCharts.jsx` nutzt bereits das folgende Ref-Dictionary-Pattern für PNG-Export:

```jsx
const chartRefs = useRef({});
const buttonRefs = useRef({});
const exportChart = useChartExport();  // gibt eine Funktion zurück, KEIN Objekt

const handleExport = (key, filename) => {
    exportChart(chartRefs.current[key], buttonRefs.current[key], filename);
};
```

**Neue Imports:**
```jsx
import ViolinPlotPlotly from "@/features/Analysis/components/charts/ViolinPlotPlotly.jsx";
import ErrorRateBar from "@/features/Analysis/components/experiment/ErrorRateBar.jsx";
```

**ViolinPlotPlotly** wird nach dem bestehenden `<BoxplotPlotly>` eingefügt, mit
Callback-Refs in die bestehenden `chartRefs`/`buttonRefs` Dictionaries:

```jsx
<ViolinPlotPlotly
    boxplotData={boxplotData}
    chartRef={el => chartRefs.current["violin"] = el}
    buttonRef={el => buttonRefs.current["violin"] = el}
    onExport={() => handleExport("violin", "violinplot.png")}
/>
```

**ErrorRateBar** wird danach eingefügt (kein PNG-Export — Recharts unterstützt kein
natives PNG-Export wie Plotly):

```jsx
<h2 className="mt-8 mb-4">Fehlerrate pro Trial</h2>
<ErrorRateBar chartData={chartData} />
```

### 6.2 Entfernung der PlaceholderCharts aus ExperimentAnalysisPage.jsx

Die PlaceholderCharts befinden sich in `ExperimentAnalysisPage.jsx` (Performance-Tab),
NICHT in `PerformanceCharts.jsx`. Sie müssen dort entfernt werden:

```jsx
// ENTFERNEN aus ExperimentAnalysisPage.jsx (Performance-Tab):
{/* SESSION B: PerformanceViolin */}
<PlaceholderChart label="Violinplot pro Bedingung (kommt in Session B)" />
{/* SESSION B: ErrorRateBar */}
<PlaceholderChart label="Fehlerrate pro Bedingung (kommt in Session B)" />
```

Die neuen Charts werden von `PerformanceCharts.jsx` gerendert (das weiterhin als
`<PerformanceCharts chartData={performanceMetrics} />` eingebunden bleibt).
`PlaceholderChart`-Import aus `ExperimentAnalysisPage.jsx` entfernen wenn
danach keine weiteren Platzhalter mehr im Performance-Tab verbleiben — es verbleiben
jedoch noch Platzhalter für andere Session-B-Bereiche (ET, UX), daher bleibt der
Import erhalten.

---

## 7. Dateistruktur nach Session B (Performance)

```
Backend/
└── services/data_analysis/performance_analysis_service.py   MODIFY (+3 Felder pro Trial)
    tests/test_analysis.py                                    MODIFY (+1 Test)

src/features/Analysis/
├── ExperimentAnalysisPage.jsx                                MODIFY (2 PlaceholderCharts entfernen)
├── components/
│   ├── charts/
│   │   └── ViolinPlotPlotly.jsx                             CREATE
│   └── experiment/
│       ├── ErrorRateBar.jsx                                  CREATE
│       └── PerformanceCharts.jsx                             MODIFY (+ViolinPlot, +ErrorRateBar)
```

---

## 8. Nicht in diesem Spec

- Gaze-Timeline, PhaseAOIHeatmap, TransitionSankey, SaccadeRateBar, PPIBar → Session B ET-Charts
- NASA-TLX, SUS, AttrakDiff → Session B UX-Charts
- CorrelationMatrix → Session B Vergleich-Charts
- PosthocHeatmap → Session B Vergleich-Charts

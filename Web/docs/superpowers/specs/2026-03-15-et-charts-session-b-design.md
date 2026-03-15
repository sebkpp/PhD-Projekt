# Design-Spec: Eye-Tracking Charts — Session B

**Datum:** 2026-03-15
**Branch:** 20-web-interface-for-data-collection
**Referenz:** `docs/superpowers/specs/2026-03-15-performance-charts-session-b-design.md` (Performance Session B)
**Status:** Draft

---

## 1. Ziel

Fünf PlaceholderCharts im Eye-Tracking-Tab der `ExperimentAnalysisPage` ersetzen:

1. **PhaseHeatmapPlotly** — AOI × Phasen-Heatmap (Small Multiples, ein Subplot pro Trial)
2. **TransitionMatrixPlotly** — AOI-Übergangs-Matrix (Small Multiples, ein Subplot pro Trial)
3. **PPIBar** — PPI-Balkendiagramm (Recharts, Geber/Empfänger pro Trial, 30%-Referenzlinie)
4. **SaccadeRateBar** — Sakkaden-Rate pro Trial (Recharts, Geber/Empfänger)

Hinweis: PhaseHeatmapPlotly ersetzt **beide** Placeholders `AOI × Phasen-Heatmap` und `Gaze-Timeline` (beide zeigen phasenbasierte AOI-Anteile; ein Chart reicht).
TransitionMatrixPlotly ersetzt den `Blickpfad-Sankey` Placeholder.

Das vorhandene PPI-Text-Widget in `ExperimentAnalysisPage.jsx` (Zeilen ~118–135) wird
durch `PPIBar` in `EyeTrackingCharts.jsx` ersetzt.

---

## 2. Studiendesign-Kontext

`ExperimentAnalysisPage` zeigt **deskriptive** Analyse eines einzelnen Experiment-Paares.
Trial = Bedingung (within-subject, permutiert). Alle neuen Charts zeigen Daten **pro Trial**.
Small-Multiples-Ansatz: alle Trials gleichzeitig sichtbar mit synchronisierter Farbskala
für vollständige Vergleichbarkeit.

---

## 3. Backend-Erweiterung: Sakkaden-Rate

### 3.1 Datei

`Backend/services/data_analysis/eye_tracking_analysis_service.py`

### 3.2 Neue Funktion `analyze_experiment_saccade_rate`

Folgt dem exakten Muster von `analyze_experiment_ppi` (Rollenaufteilung über
`et.participant_id == handover.giver`). Saccade-Count = Summe aller Werte in
`calc_transitions(aoi_sequence)`. Duration = Summe aller `et.duration` Werte pro Rolle.

```python
def analyze_experiment_saccade_rate(session, experiment_id: int) -> dict:
    """
    Sakkaden-Rate (Sakkaden/Sekunde) pro Trial, aufgeteilt nach Geber/Empfänger.

    Sakkaden werden als AOI-Übergänge gezählt (aufeinanderfolgende verschiedene AOIs).
    Gesamtdauer = Summe aller et.duration-Werte pro Rolle und Trial.

    Returns: {
      "experiment_id": int,
      "by_trial": {
        trial_id: {
          "trial_number": int,
          "stimuli_conditions": [...],
          "saccade_rate_giver": float | None,    # Sakkaden/Sekunde
          "saccade_rate_receiver": float | None
        }
      }
    }
    """
    t_repo = TrialRepository(session)
    h_repo = HandoverRepository(session)
    s_repo = StimuliRepository(session)

    trials = t_repo.get_by_experiment_id(experiment_id)
    if not trials:
        return {}

    trial_ids = [t.trial_id for t in trials]
    trial_stimuli_map = s_repo.get_stimuli_for_trials(trial_ids)

    by_trial = {}
    for trial in trials:
        handovers = h_repo.get_handovers_for_trial(trial.trial_id)

        giver_et: list[tuple[object, str]] = []   # (starttime, aoi_name)
        receiver_et: list[tuple[object, str]] = []
        giver_duration_ms: int = 0
        receiver_duration_ms: int = 0

        for handover in handovers:
            for et in handover.eye_trackings:
                aoi_name = et.aoi.aoi if et.aoi else str(et.aoi_id)
                dur = et.duration if et.duration is not None else 0
                if et.participant_id == handover.giver:
                    giver_et.append((et.starttime, aoi_name))
                    giver_duration_ms += dur
                else:
                    receiver_et.append((et.starttime, aoi_name))
                    receiver_duration_ms += dur

        giver_et.sort(key=lambda x: x[0] if x[0] is not None else datetime.min)
        receiver_et.sort(key=lambda x: x[0] if x[0] is not None else datetime.min)

        giver_seq = [aoi for _, aoi in giver_et]
        receiver_seq = [aoi for _, aoi in receiver_et]

        giver_saccades = sum(calc_transitions(giver_seq).values())
        receiver_saccades = sum(calc_transitions(receiver_seq).values())

        stimuli = trial_stimuli_map.get(trial.trial_id, [])
        by_trial[trial.trial_id] = {
            "trial_number": trial.trial_number,
            "stimuli_conditions": [
                {"name": s["name"], "type": s.get("stimulus_type", "stimulus")}
                for s in stimuli
            ],
            "saccade_rate_giver": calc_saccade_rate(giver_saccades, giver_duration_ms),
            "saccade_rate_receiver": calc_saccade_rate(receiver_saccades, receiver_duration_ms),
        }

    return {"experiment_id": experiment_id, "by_trial": by_trial}
```

### 3.3 Neuer Endpoint

In `Backend/routes/analysis.py`:

```python
@router.get("/experiment/{experiment_id}/eyetracking/saccade-rate")
def get_experiment_saccade_rate(experiment_id: int, session: Session = Depends(get_session)):
    from Backend.services.data_analysis.eye_tracking_analysis_service import analyze_experiment_saccade_rate
    return analyze_experiment_saccade_rate(session, experiment_id)
```

### 3.4 Test

In `Backend/tests/test_analysis.py`:

```python
def test_analysis_saccade_rate_experiment(client, experiment_id):
    resp = client.get(f"/analysis/experiment/{experiment_id}/eyetracking/saccade-rate")
    assert resp.status_code < 500
```

---

## 4. Frontend-Service und Hook

### 4.1 eyeTrackingService.js

In `src/features/Analysis/services/eyeTrackingService.js` ergänzen:

```js
export async function fetchExperimentSaccadeRate(experimentId) {
    const resp = await fetch(`/api/analysis/experiment/${experimentId}/eyetracking/saccade-rate`);
    if (!resp.ok) throw new Error(`Saccade rate fetch failed: ${resp.status}`);
    return resp.json();
}
```

### 4.2 useSaccadeRate.js

Neue Datei `src/features/Analysis/hooks/useSaccadeRate.js` — identisches Muster
wie `usePPI.js`:

```js
import { useState, useEffect } from "react";
import { fetchExperimentSaccadeRate } from "@/features/Analysis/services/eyeTrackingService.js";

export function useSaccadeRate(experimentId, enabled = true) {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!experimentId || !enabled) return;
        setLoading(true);
        fetchExperimentSaccadeRate(experimentId)
            .then(setData)
            .catch(setError)
            .finally(() => setLoading(false));
    }, [experimentId, enabled]);

    return { data, loading, error };
}
```

---

## 5. PPIBar.jsx

### 5.1 Datei

`src/features/Analysis/components/experiment/PPIBar.jsx`

### 5.2 Props

```jsx
PPIBar({ ppiData })
```

`ppiData` = gesamtes Objekt von `usePPI` (enthält `by_trial`).

### 5.3 Datentransformation

```js
const barData = Object.entries(ppiData.by_trial ?? {}).map(([id, m]) => ({
    name: `Trial ${m.trial_number ?? id}`,
    giver: m.ppi_giver !== null ? parseFloat(m.ppi_giver.toFixed(1)) : null,
    receiver: m.ppi_receiver !== null ? parseFloat(m.ppi_receiver.toFixed(1)) : null,
}));
```

### 5.4 Recharts-Konfiguration

- `BarChart` mit `ResponsiveContainer width="100%" height={280}`
- `XAxis dataKey="name"`
- `YAxis domain={[0, 100]}` mit Label `"%"`
- `CartesianGrid strokeDasharray="3 3"`
- `Bar dataKey="giver" fill="#8884d8" name="Geber"`
- `Bar dataKey="receiver" fill="#82ca9d" name="Empfänger"`
- `ReferenceLine y={30} stroke="#ffc658" strokeDasharray="4 4" label={{ value: "30% (auto-haptisch)", fill: "#ffc658", fontSize: 11 }}`
- `Legend` (horizontal, unten)
- `Tooltip` standard

### 5.5 Null-Behandlung

Recharts ignoriert `null`-Werte in Balken automatisch — kein spezieller Guard nötig.
Guard gegen leere Daten: `if (!ppiData?.by_trial || Object.keys(ppiData.by_trial).length === 0) return null;`

---

## 6. SaccadeRateBar.jsx

### 6.1 Datei

`src/features/Analysis/components/experiment/SaccadeRateBar.jsx`

### 6.2 Props

```jsx
SaccadeRateBar({ saccadeData })
```

`saccadeData` = gesamtes Objekt von `useSaccadeRate` (enthält `by_trial`).

### 6.3 Datentransformation

```js
const barData = Object.entries(saccadeData.by_trial ?? {}).map(([id, m]) => ({
    name: `Trial ${m.trial_number ?? id}`,
    giver: m.saccade_rate_giver !== null ? parseFloat(m.saccade_rate_giver.toFixed(2)) : null,
    receiver: m.saccade_rate_receiver !== null ? parseFloat(m.saccade_rate_receiver.toFixed(2)) : null,
}));
```

### 6.4 Recharts-Konfiguration

Identisches Muster wie `PPIBar`, aber:
- `YAxis` Label `"Sakk./s"` (kein festes `domain` — Werte können variieren)
- Keine `ReferenceLine`
- Gleiche Farben: `"#8884d8"` (Geber), `"#82ca9d"` (Empfänger)

### 6.5 Guard

`if (!saccadeData?.by_trial || Object.keys(saccadeData.by_trial).length === 0) return null;`

---

## 7. PhaseHeatmapPlotly.jsx

### 7.1 Datei

`src/features/Analysis/components/charts/PhaseHeatmapPlotly.jsx`

### 7.2 Props

```jsx
PhaseHeatmapPlotly({ phasesData, chartRef, buttonRef, onExport })
```

`phasesData` = gesamtes Objekt von `useEyeTrackingPhases` (enthält `by_trial`).

### 7.3 Datentransformation

```js
// Pro Trial: X = ["Phase 1", "Phase 2", "Phase 3"]
// Y = sortierte AOI-Labels (aus phasesData.by_trial[id].phases[phase][aoi_name].label)
// Z = percentage-Werte als Matrix [aoi_index][phase_index]

const trials = Object.entries(phasesData.by_trial ?? {});

// Alle AOI-Namen über alle Trials und Phasen sammeln (für einheitliche Y-Achse)
const allAois = [...new Set(
    trials.flatMap(([, t]) =>
        [1, 2, 3].flatMap(p => Object.keys(t.phases?.[p] ?? {}))
    )
)].sort();

// Pro Trial: z-Matrix aufbauen
// z[aoi_index][phase_index] = percentage
const xLabels = ["Phase 1", "Phase 2", "Phase 3"];
```

### 7.4 Plotly-Konfiguration (Small Multiples)

- `make_subplots(rows=trials.length, cols=1)` — ein Subplot pro Trial
- Jeder Subplot: `type: "heatmap"`, `x: xLabels`, `y: allAois`, `z: zMatrix`
- `colorscale: "Blues"`, `zmin: 0`, `zmax: 100` (synchronisiert über alle Subplots)
- `showscale: true` nur beim letzten Subplot (einheitliche Legende)
- Dunkles Design: `paper_bgcolor: "#23272f"`, `plot_bgcolor: "#23272f"`, `font: { color: "#fff" }`
- Subplot-Titel: `Trial {trial_number}` (als `annotations` über `make_subplots`)
- Gesamthöhe: `Math.max(300, trials.length * 220)` px
- `dragmode: false`, `displayModeBar: false`
- Container: identisch zu `ViolinPlotPlotly` (border, borderRadius, minWidth: 0 etc.)
- Titel: `<h3 className="export-hide">AOI-Verteilung pro Phase</h3>`
- PNG-Export-Button: identisch zu `ViolinPlotPlotly`

### 7.5 Wichtig: Plotly `make_subplots` in React

`make_subplots` kommt aus `plotly.js` nicht aus `react-plotly.js`. Import:
```js
import Plotly from "plotly.js-dist-min";
// oder aus dem bereits gebündelten react-plotly.js Paket:
import { default as PlotlyLib } from "plotly.js/dist/plotly";
```

Einfacherer Ansatz ohne `make_subplots`: mehrere `<Plot>`-Instanzen in einer Schleife
rendern (eine pro Trial). Jede Instanz ist ein eigenständiger Plotly-Chart mit identischen
`zmin`/`zmax`-Werten. Weniger komplex, gleiche Vergleichbarkeit.

**Gewählter Ansatz:** Mehrere `<Plot>`-Instanzen (eine pro Trial) — kein `make_subplots`
Import nötig, konsistent mit dem restlichen Plotly-Pattern im Projekt.

---

## 8. TransitionMatrixPlotly.jsx

### 8.1 Datei

`src/features/Analysis/components/charts/TransitionMatrixPlotly.jsx`

### 8.2 Props

```jsx
TransitionMatrixPlotly({ transitionsData, chartRef, buttonRef, onExport })
```

`transitionsData` = gesamtes Objekt von `useEyeTrackingTransitions`.

### 8.3 Datentransformation

```js
// transitions: { "aoi_from->aoi_to": count }
// Alle eindeutigen AOIs sammeln (Union aus from und to)
const trials = Object.entries(transitionsData.by_trial ?? {});

// Pro Trial:
const parseTransitions = (transitions) => {
    const aois = new Set();
    Object.keys(transitions).forEach(key => {
        const [from, to] = key.split("->");
        aois.add(from);
        aois.add(to);
    });
    const aoiList = [...aois].sort();
    // z-Matrix: z[from_index][to_index] = count
    const z = aoiList.map(from =>
        aoiList.map(to => transitions[`${from}->${to}`] ?? 0)
    );
    return { aoiList, z };
};
```

### 8.4 Plotly-Konfiguration

Mehrere `<Plot>`-Instanzen (eine pro Trial), identischer Ansatz wie `PhaseHeatmapPlotly`:
- `type: "heatmap"`, X = AOI-to-Labels, Y = AOI-from-Labels, Z = count-Matrix
- `colorscale: "Oranges"`, `zmin: 0`
- Achsenbeschriftung: X-Titel `"nach AOI"`, Y-Titel `"von AOI"`
- Dunkles Design (identisch zu anderen Plotly-Charts)
- `dragmode: false`, `displayModeBar: false`
- Höhe pro Instanz: `Math.max(250, aoiList.length * 60)` px
- Container: identisch zu `PhaseHeatmapPlotly`
- Titel: `<h3 className="export-hide">AOI-Übergangs-Matrix</h3>`
- PNG-Export-Button

---

## 9. Integration

### 9.1 EyeTrackingCharts.jsx

**Datei:** `src/features/Analysis/components/experiment/EyeTrackingCharts.jsx`

Neue Props:

```jsx
EyeTrackingCharts({ chartData, phasesData, transitionsData, ppiData, saccadeData })
```

Neue Imports:
```jsx
import PhaseHeatmapPlotly from "@/features/Analysis/components/charts/PhaseHeatmapPlotly.jsx";
import TransitionMatrixPlotly from "@/features/Analysis/components/charts/TransitionMatrixPlotly.jsx";
import PPIBar from "@/features/Analysis/components/experiment/PPIBar.jsx";
import SaccadeRateBar from "@/features/Analysis/components/experiment/SaccadeRateBar.jsx";
```

PNG-Export-Pattern: identisch zu `PerformanceCharts.jsx` —
`chartRefs = useRef({})`, `buttonRefs = useRef({})`, `exportChart = useChartExport()`.
Keys: `"phaseHeatmap"`, `"transitionMatrix"`.

Render-Reihenfolge (nach bestehendem AOI-Stacked-Bar):
1. `<PhaseHeatmapPlotly phasesData={phasesData} chartRef=... buttonRef=... onExport=... />`
2. `<TransitionMatrixPlotly transitionsData={transitionsData} chartRef=... buttonRef=... onExport=... />`
3. `<h2 className="mt-8 mb-4">PPI pro Trial</h2><PPIBar ppiData={ppiData} />`
4. `<h2 className="mt-8 mb-4">Sakkaden-Rate pro Trial</h2><SaccadeRateBar saccadeData={saccadeData} />`

Jeder neue Chart: Guard `if (!prop) return null` — kein Crash wenn Daten fehlen.

### 9.2 ExperimentAnalysisPage.jsx

**Änderungen:**

1. `_etPhasesData` → `etPhasesData` umbenennen (Underscore entfernen)
2. `_etTransitionsData` → `etTransitionsData` umbenennen
3. `useSaccadeRate` Hook hinzufügen:
   ```jsx
   import { useSaccadeRate } from "@/features/Analysis/hooks/useSaccadeRate.js";
   // ...
   const { data: saccadeData, loading: saccadeLoading, error: saccadeError } =
       useSaccadeRate(experimentId, loadedTabs.has("eyetracking"));
   ```
4. Loading/Error-States für Saccade Rate im ET-Tab ergänzen
5. `<EyeTrackingCharts>` Props erweitern:
   ```jsx
   <EyeTrackingCharts
       chartData={eyeTrackingData}
       phasesData={etPhasesData}
       transitionsData={etTransitionsData}
       ppiData={ppiData}
       saccadeData={saccadeData}
   />
   ```
6. PPI-Text-Widget (Zeilen ~118–135) **entfernen** — durch `PPIBar` in `EyeTrackingCharts` ersetzt
7. Alle 5 PlaceholderCharts im ET-Tab **entfernen**
8. `PlaceholderChart`-Import in `ExperimentAnalysisPage.jsx` **behalten** — noch in UX- und Compare-Tab verwendet

---

## 10. Dateistruktur nach dieser Session

```
Backend/
├── services/data_analysis/eye_tracking_analysis_service.py   MODIFY (+analyze_experiment_saccade_rate)
├── routes/analysis.py                                         MODIFY (+1 Endpoint)
└── tests/test_analysis.py                                     MODIFY (+1 Smoke-Test)

src/features/Analysis/
├── ExperimentAnalysisPage.jsx                                 MODIFY (rename _ vars, +useSaccadeRate, -PPI widget, -5 placeholders)
├── services/eyeTrackingService.js                             MODIFY (+fetchExperimentSaccadeRate)
├── hooks/useSaccadeRate.js                                    CREATE
└── components/
    ├── charts/
    │   ├── PhaseHeatmapPlotly.jsx                             CREATE
    │   └── TransitionMatrixPlotly.jsx                         CREATE
    └── experiment/
        ├── PPIBar.jsx                                         CREATE
        ├── SaccadeRateBar.jsx                                 CREATE
        └── EyeTrackingCharts.jsx                              MODIFY (+4 neue Komponenten als Props)
```

---

## 11. Nicht in diesem Spec

- NASA-TLX, SUS, AttrakDiff → Session B UX-Charts
- CorrelationMatrix, PosthocHeatmap → Session B Vergleich-Charts

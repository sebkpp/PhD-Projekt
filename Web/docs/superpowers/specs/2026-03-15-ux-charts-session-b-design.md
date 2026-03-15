# Design-Spec: UX-Charts — Session B

**Datum:** 2026-03-15
**Branch:** 20-web-interface-for-data-collection
**Referenz:** `docs/superpowers/specs/2026-03-15-et-charts-session-b-design.md` (Session B ET)
**Status:** Draft

---

## 1. Ziel

Vier PlaceholderCharts im UX/Fragebögen-Tab der `ExperimentAnalysisPage` ersetzen:

1. **NasaTlxBar** — NASA-TLX Subskalen-Mittelwerte pro Trial als gruppiertes Balkendiagramm
2. **SusScoreBar** — SUS-Gesamtscore pro Trial als Balkendiagramm mit Grade-Referenzlinien
3. **AttrakDiffPortfolio** — AttrakDiff2 Portfolio-Matrix (PQ vs. ATT) als Scatter-Diagramm
4. **AttrakDiffRadar** — AttrakDiff2 Subskalen-Radar (PQ, HQS, HQI, ATT)

Kein neuer Hook, kein neuer Service — alle Daten stammen aus dem bereits vorhandenen
`useUxMetrics`-Hook. **Eine minimale Backend-Änderung** ist notwendig: `trial_number` wird
in `trial_item_stats` ergänzt (derzeit fehlt dieses Feld).

---

## 2. Studiendesign-Kontext

`ExperimentAnalysisPage` zeigt **deskriptive** Analyse eines einzelnen Experiment-Paares.
Trial = Bedingung (within-subject, permutiert). Jeder Trial entspricht einer Stimulus-Bedingung.
Die neuen Charts zeigen Daten **pro Trial** (entspricht einer Bedingung).

---

## 3. Backend-Erweiterung

### 3.1 Datei

`Backend/services/data_analysis/questionnaire_analysis_service.py`

### 3.2 Problem

`compute_trial_item_stats` schreibt pro Trial-Eintrag nur `stimuli_conditions` und `questionnaires`.
Das Feld `trial_number` fehlt — alle Frontend-Komponenten benötigen es für Sortierung und Labels.

### 3.3 Änderung

**Schritt 1:** In `analyze_experiment_questionnaires` eine `trial_number_map` aufbauen.
Die Funktion hat bereits `trials = t_repo.get_by_experiment_id(experiment_id)`.

Direkt nach dieser Zeile ergänzen:
```python
trial_number_map = {t.trial_id: t.trial_number for t in trials}
```

Dann `trial_number_map` an `compute_trial_item_stats` übergeben:
```python
stats = compute_trial_item_stats(df, trial_stimuli_map, trial_number_map)
```

**Schritt 2:** Signatur von `compute_trial_item_stats` anpassen:
```python
def compute_trial_item_stats(df, trial_stimuli_map, trial_number_map=None):
```

**Schritt 3:** Im bestehenden `stats.setdefault(t_id, {...})` das Feld `trial_number` ergänzen:

Aktuell:
```python
stats.setdefault(t_id, {
    "stimuli_conditions": stimuli_conditions
}).setdefault("questionnaires", {}) ...
```

Ändern zu:
```python
stats.setdefault(t_id, {
    "stimuli_conditions": stimuli_conditions,
    "trial_number": trial_number_map.get(t_id) if trial_number_map else None,
}).setdefault("questionnaires", {}) ...
```

### 3.4 Test

In `Backend/tests/test_analysis.py` einen Smoke-Test ergänzen:

```python
def test_questionnaire_trial_item_stats_has_trial_number(client, experiment_id):
    resp = client.get(f"/analysis/experiment/{experiment_id}/questionnaires")
    assert resp.status_code == 200
    data = resp.json()
    trial_item_stats = data.get("trial_item_stats", {})
    for trial_stats in trial_item_stats.values():
        assert "trial_number" in trial_stats
```

### 3.5 Auswirkung

Additiv — kein bestehendes Feld wird verändert. Bestehende Tests und Frontend-Komponenten
sind nicht betroffen.

---

## 4. Datenstruktur (nach Backend-Erweiterung)

```js
chartData.trial_item_stats = {
    [trial_id]: {
        trial_number: number,          // NEU
        stimuli_conditions: [{name, type}, ...],
        questionnaires: {
            "NASA-TLX":    { items: [{item_name, mean, std}, ...] },
            "SUS":         { items: [{item_name, mean, std}, ...] },
            "AttrakDiff2": { items: [{item_name, mean, std}, ...] },
        }
    }
}
```

---

## 5. Frontend-Berechnungen (gemeinsame Hilfsfunktionen)

Die Berechnungen werden als reine Funktionen **innerhalb der jeweiligen Komponente** definiert
(kein shared util-File nötig — jede Komponente braucht nur ihre eigene Funktion).

### 5.1 NASA-TLX

Item-Namen sind direkt die Subskalennamen (`mental_demand`, `physical_demand`,
`temporal_demand`, `performance`, `effort`, `frustration`). Skala: 0–100.
Keine Transformation — Item-Means direkt verwenden.

### 5.2 SUS-Gesamtscore

SUS-Items: `sus_01`–`sus_10`, Skala 1–5.

Formel (Brooke 1996) auf Item-Means angewendet:
- **Ungerade Items** (`sus_01`, `sus_03`, `sus_05`, `sus_07`, `sus_09`): Beitrag = `mean − 1`
- **Gerade Items** (`sus_02`, `sus_04`, `sus_06`, `sus_08`, `sus_10`): Beitrag = `5 − mean`
- Gesamtscore = Summe aller 10 Beiträge × 2.5 → Wertebereich 0–100

```js
function calcSusScore(items) {
    const odd = ["sus_01", "sus_03", "sus_05", "sus_07", "sus_09"];
    const even = ["sus_02", "sus_04", "sus_06", "sus_08", "sus_10"];
    const itemMap = Object.fromEntries(items.map(i => [i.item_name, i.mean]));
    const sumOdd = odd.reduce((s, k) => s + ((itemMap[k] ?? 0) - 1), 0);
    const sumEven = even.reduce((s, k) => s + (5 - (itemMap[k] ?? 0)), 0);
    return parseFloat(((sumOdd + sumEven) * 2.5).toFixed(1));
}
```

SUS-Grade (Sauro 2012):
```js
function susGrade(score) {
    if (score >= 85) return "A";
    if (score >= 77) return "B";   // >= 77 (Sauro-Tabelle)
    if (score >= 65) return "C";
    if (score >= 52) return "D";
    return "F";
}
```

### 5.3 AttrakDiff2-Subskalen

28 Items mit Präfixen: `pq_` (7 Items), `hqs_` (7 Items), `hqi_` (7 Items), `att_` (7 Items).
Skala: 1–7 (bipolar), Skalenmittelpunkt = 4.

```js
function calcAttrakDiffSubscales(items) {
    const groups = { pq: [], hqs: [], hqi: [], att: [] };
    items.forEach(({ item_name, mean }) => {
        for (const key of Object.keys(groups)) {
            if (item_name.startsWith(key + "_")) { groups[key].push(mean); break; }
        }
    });
    const avg = arr => arr.length
        ? parseFloat((arr.reduce((a, b) => a + b, 0) / arr.length).toFixed(2))
        : null;
    return { pq: avg(groups.pq), hqs: avg(groups.hqs), hqi: avg(groups.hqi), att: avg(groups.att) };
}
```

**Hinweis:** `break` nach dem ersten Treffer verhindert mehrfache Zuordnung bei ähnlichen Präfixen.

---

## 6. NasaTlxBar.jsx

### 6.1 Datei

`src/features/Analysis/components/experiment/NasaTlxBar.jsx`

### 6.2 Props

```jsx
NasaTlxBar({ trialItemStats })
```

### 6.3 Guard

```jsx
if (!trialItemStats || Object.keys(trialItemStats).length === 0) return null;
const trials = Object.entries(trialItemStats)
    .filter(([, t]) => t.questionnaires?.["NASA-TLX"]?.items?.length > 0)
    .sort(([, a], [, b]) => (a.trial_number ?? 0) - (b.trial_number ?? 0));
if (trials.length === 0) return null;
```

### 6.4 Datentransformation

```js
const SUBSCALES = ["mental_demand", "physical_demand", "temporal_demand", "performance", "effort", "frustration"];
const LABELS = {
    mental_demand: "Geistig", physical_demand: "Körperlich",
    temporal_demand: "Zeitlich", performance: "Leistung",
    effort: "Anstrengung", frustration: "Frustration",
};
const COLORS = ["#8884d8", "#82ca9d", "#ffc658", "#ff7300"];

const barData = SUBSCALES.map(key => {
    const entry = { name: LABELS[key] };
    trials.forEach(([, t]) => {
        const item = t.questionnaires["NASA-TLX"].items.find(i => i.item_name === key);
        entry[`Trial ${t.trial_number}`] = item ? parseFloat(item.mean.toFixed(1)) : null;
    });
    return entry;
});
```

### 6.5 Recharts-Konfiguration

- `BarChart` mit `ResponsiveContainer width="100%" height={300}`
- `XAxis dataKey="name"`
- `YAxis domain={[0, 100]}` mit `label={{ value: "Score", angle: -90, position: "insideLeft" }}`
- `CartesianGrid strokeDasharray="3 3"`
- Ein `<Bar>` pro Trial: `dataKey={`Trial ${t.trial_number}`}` mit Farbe aus `COLORS`-Array
- `Tooltip` und `Legend verticalAlign="bottom"`

### 6.6 Container

Kein eigener Rahmen. Die Heading-Logik ist in `QuestionnaireCharts.jsx` via `hasQuestionnaire`
geregelt — siehe Section 10.3 für das authoritative Rendering-Pattern.

---

## 7. SusScoreBar.jsx

### 7.1 Datei

`src/features/Analysis/components/experiment/SusScoreBar.jsx`

### 7.2 Props

```jsx
SusScoreBar({ trialItemStats })
```

### 7.3 Guard

```jsx
if (!trialItemStats || Object.keys(trialItemStats).length === 0) return null;
const barData = Object.entries(trialItemStats)
    .filter(([, t]) => t.questionnaires?.["SUS"]?.items?.length > 0)
    .sort(([, a], [, b]) => (a.trial_number ?? 0) - (b.trial_number ?? 0))
    .map(([, t]) => ({
        name: `Trial ${t.trial_number}`,
        score: calcSusScore(t.questionnaires["SUS"].items),
    }));
if (barData.length === 0) return null;
```

### 7.4 Recharts-Konfiguration

- `BarChart` mit `ResponsiveContainer width="100%" height={280}`
- `XAxis dataKey="name"`
- `YAxis domain={[0, 100]}` mit `label={{ value: "SUS-Score", angle: -90, position: "insideLeft" }}`
- `CartesianGrid strokeDasharray="3 3"`
- `Bar dataKey="score" fill="#8884d8"`
- `ReferenceLine y={68} stroke="#ffc658" strokeDasharray="4 4" label={{ value: "Akzeptabel (68)", fill: "#ffc658", fontSize: 11 }}`
- `ReferenceLine y={80.3} stroke="#82ca9d" strokeDasharray="4 4" label={{ value: "Gut (80.3)", fill: "#82ca9d", fontSize: 11 }}`
- Tooltip:
```jsx
<Tooltip formatter={(v) => [`${v} (${susGrade(v)})`, "SUS-Score"]} />
```

### 7.5 Container

Kein eigener Rahmen. Die Heading-Logik ist in `QuestionnaireCharts.jsx` via `hasQuestionnaire`
geregelt — siehe Section 10.3 für das authoritative Rendering-Pattern.

**Hinweis SUS-Referenzlinien:** Die Referenzlinien bei 68 ("Akzeptabel", Brooke 1996) und
80.3 ("Gut", Bangor 2009) weichen bewusst von den `susGrade`-Schwellenwerten (77, 85) ab —
sie repräsentieren die originalen Acceptability-Grenzen aus der SUS-Literatur.

---

## 8. AttrakDiffPortfolio.jsx

### 8.1 Datei

`src/features/Analysis/components/experiment/AttrakDiffPortfolio.jsx`

### 8.2 Props

```jsx
AttrakDiffPortfolio({ trialItemStats })
```

### 8.3 Guard & Datentransformation

```jsx
if (!trialItemStats || Object.keys(trialItemStats).length === 0) return null;
const scatterData = Object.entries(trialItemStats)
    .filter(([, t]) => t.questionnaires?.["AttrakDiff2"]?.items?.length > 0)
    .sort(([, a], [, b]) => (a.trial_number ?? 0) - (b.trial_number ?? 0))
    .map(([, t]) => {
        const { pq, att } = calcAttrakDiffSubscales(t.questionnaires["AttrakDiff2"].items);
        if (pq == null || att == null) return null;   // Subskale nicht berechenbar
        return { x: pq, y: att, label: `Trial ${t.trial_number}` };
    })
    .filter(Boolean);  // null-Einträge entfernen
if (scatterData.length === 0) return null;
```

**Hinweis:** `calcAttrakDiffSubscales` gibt `null` zurück, wenn eine Subskala keine Items hat.
Solche Punkte werden herausgefiltert, damit kein `{x: null, y: null}`-Punkt bei (0,0) landet.

### 8.4 Recharts-Konfiguration

- `ScatterChart` mit `ResponsiveContainer width="100%" height={340}`
- `XAxis type="number" dataKey="x" domain={[1, 7]} name="PQ"` mit `label={{ value: "PQ (Pragmatische Qualität)", position: "insideBottom", offset: -5 }}`
- `YAxis type="number" dataKey="y" domain={[1, 7]} name="ATT"` mit `label={{ value: "ATT (Attraktivität)", angle: -90, position: "insideLeft" }}`
- `ReferenceLine x={4} stroke="#555" strokeDasharray="4 4"` (Skalenmittelpunkt)
- `ReferenceLine y={4} stroke="#555" strokeDasharray="4 4"`
- `Scatter data={scatterData} fill="#8884d8"`
- `Tooltip content={({ payload }) => payload?.[0] ? <div>{payload[0].payload.label}: PQ={payload[0].payload.x}, ATT={payload[0].payload.y}</div> : null}`
- **Kein `LabelList`** — Recharts v3 unterstützt `LabelList` innerhalb von `<Scatter>` nicht stabil.
  Stattdessen werden Trial-Labels im Tooltip angezeigt. Da typischerweise nur 2 Trials vorhanden
  sind, ist die Identifikation per Hover + Legende ausreichend.
- `Legend` (falls mehrere `<Scatter>`-Elemente pro Trial gewünscht — alternativ: alle Punkte in
  einem `<Scatter>`-Element mit `data={scatterData}`, unterschiedliche Farben via `fill` pro Punkt
  durch `Cell`-Komponente)

**Empfohlenes Rendering-Pattern** (alle Punkte in einem `<Scatter>`, `Cell` für Farben):
```jsx
const COLORS = ["#8884d8", "#82ca9d", "#ffc658", "#ff7300"];
<Scatter data={scatterData}>
    {scatterData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
</Scatter>
```

### 8.5 Container

`QuestionnaireCharts.jsx` rendert bedingt (analog zu NasaTlxBar).

---

## 9. AttrakDiffRadar.jsx

### 9.1 Datei

`src/features/Analysis/components/experiment/AttrakDiffRadar.jsx`

### 9.2 Props

```jsx
AttrakDiffRadar({ trialItemStats })
```

### 9.3 Guard & Datentransformation

```jsx
if (!trialItemStats || Object.keys(trialItemStats).length === 0) return null;
const trials = Object.entries(trialItemStats)
    .filter(([, t]) => t.questionnaires?.["AttrakDiff2"]?.items?.length > 0)
    .sort(([, a], [, b]) => (a.trial_number ?? 0) - (b.trial_number ?? 0));
if (trials.length === 0) return null;

// Subskalen einmalig pro Trial berechnen (nicht 4× im map)
const trialSubscales = trials.map(([, t]) => ({
    label: `Trial ${t.trial_number}`,
    subs: calcAttrakDiffSubscales(t.questionnaires["AttrakDiff2"].items),
}));

const SUBSCALES_RADAR = [
    { key: "pq",  subject: "PQ (Pragmatik)" },
    { key: "hqs", subject: "HQS (Stimulation)" },
    { key: "hqi", subject: "HQI (Identität)" },
    { key: "att", subject: "ATT (Attraktivität)" },
];
const radarData = SUBSCALES_RADAR.map(({ key, subject }) => {
    const entry = { subject };
    trialSubscales.forEach(({ label, subs }) => {
        entry[label] = subs[key];
    });
    return entry;
});
```

**Hinweis:** `calcAttrakDiffSubscales` wird einmalig pro Trial aufgerufen (in `trialSubscales`),
nicht 4× innerhalb von `SUBSCALES_RADAR.map`.

### 9.4 Recharts-Konfiguration

- `RadarChart` mit `ResponsiveContainer width="100%" height={340}`, `cx="50%"`, `cy="50%"`, `outerRadius={110}`
- `PolarGrid`
- `PolarAngleAxis dataKey="subject"`
- `PolarRadiusAxis angle={30} domain={[1, 7]}`
- Ein `<Radar>` pro Trial: `dataKey={trialLabel}`, Farben aus `COLORS = ["#8884d8", "#82ca9d", "#ffc658", "#ff7300"]`, `fillOpacity={0.3}`
- `Legend verticalAlign="bottom"` und `Tooltip`

### 9.5 Container

`QuestionnaireCharts.jsx` rendert bedingt (analog zu NasaTlxBar).

---

## 10. Integration in QuestionnaireCharts.jsx

### 10.1 Neue Imports

```jsx
import NasaTlxBar from "@/features/Analysis/components/experiment/NasaTlxBar.jsx";
import SusScoreBar from "@/features/Analysis/components/experiment/SusScoreBar.jsx";
import AttrakDiffPortfolio from "@/features/Analysis/components/experiment/AttrakDiffPortfolio.jsx";
import AttrakDiffRadar from "@/features/Analysis/components/experiment/AttrakDiffRadar.jsx";
```

### 10.2 Hilfsfunktion für bedingte Anzeige

Im Funktionskörper von `QuestionnaireCharts`, nach `const grouped = groupChartData(...)`:

```jsx
const hasQuestionnaire = (name) =>
    Object.values(chartData.trial_item_stats ?? {})
        .some(t => t.questionnaires?.[name]?.items?.length > 0);
```

### 10.3 Neues JSX (am Ende der return-Anweisung, nach den bestehenden QuestionnaireChartGroup-Elementen)

```jsx
{hasQuestionnaire("NASA-TLX") && (
    <>
        <h2 className="mt-8 mb-4 text-xl font-semibold">NASA-TLX Subskalen</h2>
        <NasaTlxBar trialItemStats={chartData.trial_item_stats} />
    </>
)}
{hasQuestionnaire("SUS") && (
    <>
        <h2 className="mt-8 mb-4 text-xl font-semibold">SUS-Score pro Trial</h2>
        <SusScoreBar trialItemStats={chartData.trial_item_stats} />
    </>
)}
{hasQuestionnaire("AttrakDiff2") && (
    <>
        <h2 className="mt-8 mb-4 text-xl font-semibold">AttrakDiff2 Portfolio-Matrix</h2>
        <AttrakDiffPortfolio trialItemStats={chartData.trial_item_stats} />
        <h2 className="mt-8 mb-4 text-xl font-semibold">AttrakDiff2 Subskalen-Radar</h2>
        <AttrakDiffRadar trialItemStats={chartData.trial_item_stats} />
    </>
)}
```

Die `hasQuestionnaire`-Prüfung verhindert schwebende `<h2>`-Elemente ohne Chart.

---

## 11. ExperimentAnalysisPage.jsx — Änderung

Im UX-TabPanel die 4 PlaceholderCharts entfernen:

```jsx
// ENTFERNEN:
<PlaceholderChart label="NASA-TLX Subskalen pro Bedingung (kommt in Session B)" />
<PlaceholderChart label="SUS-Score pro Bedingung (kommt in Session B)" />
<PlaceholderChart label="AttrakDiff2 Portfolio-Matrix (kommt in Session B)" />
<PlaceholderChart label="AttrakDiff2 Subskalen-Radar (kommt in Session B)" />
```

`PlaceholderChart`-Import bleibt erhalten — noch 1 Placeholder im Compare-Tab (Korrelationsmatrix).

---

## 12. Dateistruktur nach Session B (UX)

```
Backend/
└── services/data_analysis/questionnaire_analysis_service.py   MODIFY (+trial_number in trial_item_stats)
    tests/test_analysis.py                                      MODIFY (+1 Smoke-Test)

src/features/Analysis/
├── ExperimentAnalysisPage.jsx                                  MODIFY (4 PlaceholderCharts entfernen)
└── components/experiment/
    ├── NasaTlxBar.jsx                                          CREATE
    ├── SusScoreBar.jsx                                         CREATE
    ├── AttrakDiffPortfolio.jsx                                 CREATE
    ├── AttrakDiffRadar.jsx                                     CREATE
    └── QuestionnaireCharts.jsx                                 MODIFY (+4 Imports, hasQuestionnaire, +4 Renders)
```

---

## 13. Nicht in diesem Spec

- Korrelationsmatrix → Session B Vergleich-Charts
- PosthocHeatmap → Session B Vergleich-Charts
- ISO-Metrics-spezifische Charts (kein Placeholder vorhanden)
- PNG-Export für die neuen Charts (Recharts unterstützt kein natives PNG-Export wie Plotly)

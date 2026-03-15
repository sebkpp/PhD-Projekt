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

Kein neuer Backend-Endpoint, kein neuer Hook, kein neuer Service — alle Daten stammen aus
dem bereits vorhandenen `useUxMetrics`-Hook über `chartData.trial_item_stats`.

---

## 2. Studiendesign-Kontext

`ExperimentAnalysisPage` zeigt **deskriptive** Analyse eines einzelnen Experiment-Paares.
Trial = Bedingung (within-subject, permutiert). Jeder Trial entspricht einer Stimulus-Bedingung.
Die neuen Charts zeigen Daten **pro Trial** (entspricht einer Bedingung).

---

## 3. Datenquelle & Frontend-Berechnungen

### 3.1 Datenstruktur (aus `useUxMetrics`)

```js
chartData.trial_item_stats = {
    [trial_id]: {
        stimuli_conditions: [{name, type}, ...],
        trial_number: number,
        questionnaires: {
            "NASA-TLX": { items: [{item_name, mean, std}, ...] },
            "SUS":       { items: [{item_name, mean, std}, ...] },
            "AttrakDiff2": { items: [{item_name, mean, std}, ...] },
        }
    }
}
```

### 3.2 NASA-TLX

Item-Namen sind direkt die Subskalennamen (`mental_demand`, `physical_demand`,
`temporal_demand`, `performance`, `effort`, `frustration`). Skala: 0–100.
Keine Transformation nötig — Item-Means direkt verwenden.

### 3.3 SUS-Gesamtscore

SUS-Items: `sus_01`–`sus_10`, Skala 1–5.

Formel auf Item-Means angewendet:
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

### 3.4 AttrakDiff2-Subskalen

28 Items mit Präfixen: `pq_` (7 Items), `hqs_` (7 Items), `hqi_` (7 Items), `att_` (7 Items).
Skala: 1–7 (bipolar), Mittelwert = 4.

Subskalen-Mittelwert = Mittelwert aller Items mit dem jeweiligen Präfix:

```js
function calcAttrakDiffSubscales(items) {
    const groups = { pq: [], hqs: [], hqi: [], att: [] };
    items.forEach(({ item_name, mean }) => {
        for (const key of Object.keys(groups)) {
            if (item_name.startsWith(key + "_")) groups[key].push(mean);
        }
    });
    const avg = arr => arr.length ? parseFloat((arr.reduce((a, b) => a + b, 0) / arr.length).toFixed(2)) : null;
    return { pq: avg(groups.pq), hqs: avg(groups.hqs), hqi: avg(groups.hqi), att: avg(groups.att) };
}
```

---

## 4. NasaTlxBar.jsx

### 4.1 Datei

`src/features/Analysis/components/experiment/NasaTlxBar.jsx`

### 4.2 Props

```jsx
NasaTlxBar({ trialItemStats })
```

### 4.3 Datentransformation

```js
// Alle Trials, die NASA-TLX-Daten haben, sortiert nach trial_number
const trials = Object.entries(trialItemStats ?? {})
    .filter(([, t]) => t.questionnaires?.["NASA-TLX"]?.items?.length > 0)
    .sort(([, a], [, b]) => a.trial_number - b.trial_number);

// Pro Subskala ein Datenpunkt mit Wert je Trial
const SUBSCALES = ["mental_demand", "physical_demand", "temporal_demand", "performance", "effort", "frustration"];
const LABELS = {
    mental_demand: "Geistig", physical_demand: "Körperlich",
    temporal_demand: "Zeitlich", performance: "Leistung",
    effort: "Anstrengung", frustration: "Frustration"
};
const barData = SUBSCALES.map(key => {
    const entry = { name: LABELS[key] };
    trials.forEach(([, t]) => {
        const item = t.questionnaires["NASA-TLX"].items.find(i => i.item_name === key);
        entry[`Trial ${t.trial_number}`] = item ? parseFloat(item.mean.toFixed(1)) : null;
    });
    return entry;
});
```

### 4.4 Recharts-Konfiguration

- `BarChart` mit `ResponsiveContainer width="100%" height={300}`
- `XAxis dataKey="name"` — Subskalen-Labels
- `YAxis domain={[0, 100]}` mit `label={{ value: "Score", angle: -90, position: "insideLeft" }}`
- `CartesianGrid strokeDasharray="3 3"`
- Ein `<Bar>` pro Trial, Farben aus Palette `["#8884d8", "#82ca9d", "#ffc658", "#ff7300"]`
- `Tooltip` und `Legend`

### 4.5 Guard

```jsx
if (!trialItemStats || Object.values(trialItemStats).every(t => !t.questionnaires?.["NASA-TLX"])) return null;
```

### 4.6 Container

Kein eigener Rahmen — `QuestionnaireCharts.jsx` setzt `<h2>NASA-TLX Subskalen</h2>` und
rendert `NasaTlxBar` direkt darunter.

---

## 5. SusScoreBar.jsx

### 5.1 Datei

`src/features/Analysis/components/experiment/SusScoreBar.jsx`

### 5.2 Props

```jsx
SusScoreBar({ trialItemStats })
```

### 5.3 Datentransformation

```js
const barData = Object.entries(trialItemStats ?? {})
    .filter(([, t]) => t.questionnaires?.["SUS"]?.items?.length > 0)
    .sort(([, a], [, b]) => a.trial_number - b.trial_number)
    .map(([, t]) => ({
        name: `Trial ${t.trial_number}`,
        score: calcSusScore(t.questionnaires["SUS"].items),
    }));
```

### 5.4 Recharts-Konfiguration

- `BarChart` mit `ResponsiveContainer width="100%" height={280}`
- `XAxis dataKey="name"`
- `YAxis domain={[0, 100]}` mit `label={{ value: "SUS-Score", angle: -90, position: "insideLeft" }}`
- `CartesianGrid strokeDasharray="3 3"`
- `Bar dataKey="score" fill="#8884d8"`
- `ReferenceLine y={68} stroke="#ffc658" strokeDasharray="4 4" label={{ value: "Akzeptabel (68)", fill: "#ffc658", fontSize: 11 }}`
- `ReferenceLine y={80.3} stroke="#82ca9d" strokeDasharray="4 4" label={{ value: "Gut (80.3)", fill: "#82ca9d", fontSize: 11 }}`
- `Tooltip formatter={(v) => [${v} (${susGrade(v)})`, "SUS-Score"]}`

SUS-Grade-Funktion:
```js
function susGrade(score) {
    if (score >= 85) return "A";
    if (score >= 77) return "B";
    if (score >= 65) return "C";
    if (score >= 52) return "D";
    return "F";
}
```

### 5.5 Guard

```jsx
if (!trialItemStats || Object.values(trialItemStats).every(t => !t.questionnaires?.["SUS"])) return null;
```

### 5.6 Container

`QuestionnaireCharts.jsx` setzt `<h2>SUS-Score pro Trial</h2>`.

---

## 6. AttrakDiffPortfolio.jsx

### 6.1 Datei

`src/features/Analysis/components/experiment/AttrakDiffPortfolio.jsx`

### 6.2 Props

```jsx
AttrakDiffPortfolio({ trialItemStats })
```

### 6.3 Datentransformation

```js
const scatterData = Object.entries(trialItemStats ?? {})
    .filter(([, t]) => t.questionnaires?.["AttrakDiff2"]?.items?.length > 0)
    .sort(([, a], [, b]) => a.trial_number - b.trial_number)
    .map(([, t]) => {
        const { pq, att } = calcAttrakDiffSubscales(t.questionnaires["AttrakDiff2"].items);
        return { x: pq, y: att, label: `Trial ${t.trial_number}` };
    });
```

### 6.4 Recharts-Konfiguration

- `ScatterChart` mit `ResponsiveContainer width="100%" height={320}`
- `XAxis type="number" dataKey="x" domain={[1, 7]}` mit `label={{ value: "PQ (Pragmatische Qualität)", position: "insideBottom", offset: -5 }}`
- `YAxis type="number" dataKey="y" domain={[1, 7]}` mit `label={{ value: "ATT (Attraktivität)", angle: -90, position: "insideLeft" }}`
- `ReferenceLine x={4} stroke="#555" strokeDasharray="4 4"` — Skalenmittelpunkt
- `ReferenceLine y={4} stroke="#555" strokeDasharray="4 4"`
- `Scatter data={scatterData} fill="#8884d8"`
- `Tooltip content` zeigt `label`, `PQ: x`, `ATT: y`
- Jeder Punkt bekommt ein `<LabelList dataKey="label" position="top" />` für Trial-Beschriftung

### 6.5 Guard

```jsx
if (!trialItemStats || Object.values(trialItemStats).every(t => !t.questionnaires?.["AttrakDiff2"])) return null;
```

### 6.6 Container

`QuestionnaireCharts.jsx` setzt `<h2>AttrakDiff2 Portfolio-Matrix</h2>`.

---

## 7. AttrakDiffRadar.jsx

### 7.1 Datei

`src/features/Analysis/components/experiment/AttrakDiffRadar.jsx`

### 7.2 Props

```jsx
AttrakDiffRadar({ trialItemStats })
```

### 7.3 Datentransformation

```js
const trials = Object.entries(trialItemStats ?? {})
    .filter(([, t]) => t.questionnaires?.["AttrakDiff2"]?.items?.length > 0)
    .sort(([, a], [, b]) => a.trial_number - b.trial_number);

// Radar-Format: ein Eintrag pro Subskale, Wert pro Trial
const SUBSCALES_RADAR = [
    { key: "pq",  label: "PQ (Pragmatik)" },
    { key: "hqs", label: "HQS (Stimulation)" },
    { key: "hqi", label: "HQI (Identität)" },
    { key: "att", label: "ATT (Attraktivität)" },
];
const radarData = SUBSCALES_RADAR.map(({ key, label }) => {
    const entry = { subject: label };
    trials.forEach(([, t]) => {
        const subs = calcAttrakDiffSubscales(t.questionnaires["AttrakDiff2"].items);
        entry[`Trial ${t.trial_number}`] = subs[key];
    });
    return entry;
});
```

### 7.4 Recharts-Konfiguration

- `RadarChart` mit `ResponsiveContainer width="100%" height={320}`, `cx="50%"`, `cy="50%"`, `outerRadius={100}`
- `PolarGrid`
- `PolarAngleAxis dataKey="subject"`
- `PolarRadiusAxis angle={30} domain={[1, 7]}`
- Ein `<Radar>` pro Trial, Farben aus Palette `["#8884d8", "#82ca9d", "#ffc658", "#ff7300"]`
- `fillOpacity={0.3}`
- `Legend` und `Tooltip`

### 7.5 Guard

```jsx
if (!trialItemStats || Object.values(trialItemStats).every(t => !t.questionnaires?.["AttrakDiff2"])) return null;
```

### 7.6 Container

`QuestionnaireCharts.jsx` setzt `<h2>AttrakDiff2 Subskalen-Radar</h2>`.

---

## 8. Integration in QuestionnaireCharts.jsx

### 8.1 Neue Imports

```jsx
import NasaTlxBar from "@/features/Analysis/components/experiment/NasaTlxBar.jsx";
import SusScoreBar from "@/features/Analysis/components/experiment/SusScoreBar.jsx";
import AttrakDiffPortfolio from "@/features/Analysis/components/experiment/AttrakDiffPortfolio.jsx";
import AttrakDiffRadar from "@/features/Analysis/components/experiment/AttrakDiffRadar.jsx";
```

### 8.2 Neues JSX (am Ende der return-Anweisung, nach den bestehenden `QuestionnaireChartGroup`-Elementen)

```jsx
<h2 className="mt-8 mb-4 text-xl font-semibold">NASA-TLX Subskalen</h2>
<NasaTlxBar trialItemStats={chartData.trial_item_stats} />

<h2 className="mt-8 mb-4 text-xl font-semibold">SUS-Score pro Trial</h2>
<SusScoreBar trialItemStats={chartData.trial_item_stats} />

<h2 className="mt-8 mb-4 text-xl font-semibold">AttrakDiff2 Portfolio-Matrix</h2>
<AttrakDiffPortfolio trialItemStats={chartData.trial_item_stats} />

<h2 className="mt-8 mb-4 text-xl font-semibold">AttrakDiff2 Subskalen-Radar</h2>
<AttrakDiffRadar trialItemStats={chartData.trial_item_stats} />
```

---

## 9. ExperimentAnalysisPage.jsx — Änderung

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

## 10. Dateistruktur nach Session B (UX)

```
src/features/Analysis/
├── ExperimentAnalysisPage.jsx                                MODIFY (4 PlaceholderCharts entfernen)
└── components/experiment/
    ├── NasaTlxBar.jsx                                        CREATE
    ├── SusScoreBar.jsx                                       CREATE
    ├── AttrakDiffPortfolio.jsx                               CREATE
    ├── AttrakDiffRadar.jsx                                   CREATE
    └── QuestionnaireCharts.jsx                               MODIFY (+4 Imports, +4 Renders)
```

---

## 11. Nicht in diesem Spec

- Korrelationsmatrix → Session B Vergleich-Charts
- PosthocHeatmap → Session B Vergleich-Charts
- ISO-Metrics-spezifische Charts
- PNG-Export für die neuen Charts (Recharts unterstützt kein natives PNG-Export wie Plotly)

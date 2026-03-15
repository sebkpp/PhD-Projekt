# Design-Spec: Analysis UI Integration & Performance-Optimierung

**Datum:** 2026-03-15
**Branch:** 20-web-interface-for-data-collection
**Referenz:** `docs/superpowers/specs/2026-03-14-statistische-auswertung-design.md` (Spec v2)
**Status:** Approved

---

## 1. Kontext & Ziel

Die statistischen Analyse-Services (Backend) und viele Frontend-Komponenten sind bereits
implementiert. Drei Probleme verhindern die nutzbare Integration:

1. **`AnalysisPage` (`/analysis`) ist leer** — nur Platzhaltertext, kein Inhalt
2. **`AnalysisDashboard`** (`pages/AnalysisDashboard.jsx`) ist gebaut aber nie geroutet —
   verwaiste Komponente mit paralleler, inkonsistenter Implementierung
3. **Ladezeiten** — `StudyAnalysisPage` und `ExperimentAnalysisPage` starten alle API-Calls
   gleichzeitig beim Mount und blockieren die gesamte Seite bis alle fertig sind

Diese Session schließt die Integration-Lücke. Neue Chart-Kategorien (Spec 5.2–5.5),
Report-Export (Spec 5.8.1) und Signifikanz-Highlighting (Spec 5.8.3) sind separater Scope.

---

## 2. Scope

### In Scope

- `AnalysisPage` als Cross-Study-Übersicht (Spec 5.8.6)
- `ExperimentAnalyseTabs` auf CSS-Visibility umstellen (Voraussetzung für Lazy Loading)
- Lazy Tab Loading für `StudyAnalysisPage` und `ExperimentAnalysisPage`
- Export-Tab in `StudyAnalysisPage` (CSV/XLSX, Spec 5.9)
- Bereinigung verwaister Komponenten

### Nicht in Scope (explizit verschoben)

- **Händigkeit-Filter (Spec 5.7):** Backend-Endpunkte unterstützen `?handedness=` noch nicht
  (kein Query-Parameter in den Route-Signaturen). Wird in separater Session implementiert,
  sobald Backend angepasst ist.
- Neue Chart-Komponenten (Spec 5.2–5.5: Boxplot, Violin, Heatmap, Sankey etc.)
- Report-Generator (Spec 5.8.1)
- Signifikanz-Highlighting in Tabellen (Spec 5.8.3)
- Datenqualitäts-Indikator (Spec 5.8.4)
- Chart-Export (PNG/SVG, Spec 5.9 Visualisierungs-Export)

---

## 3. Zu löschende Dateien (Bereinigung)

| Datei | Grund |
|---|---|
| `src/features/Analysis/pages/AnalysisDashboard.jsx` | Verwaist, nie geroutet; parallele Implementierung zu `StudyAnalysisPage` |
| `src/features/Analysis/components/PerformanceChart.jsx` | Ausschließlich von `AnalysisDashboard` genutzt; self-fetching, inkonsistent mit Hook-Architektur |
| `src/features/Analysis/components/EyeTrackingChart.jsx` | Ausschließlich von `AnalysisDashboard` genutzt; self-fetching, inkonsistent mit Hook-Architektur |

---

## 4. AnalysisPage (`/analysis`) — Cross-Study-Übersicht

### 4.1 Zweck

Dedizierte Seite für studienbübergreifende deskriptive Vergleiche (Spec 5.8.6).
Kein inferenzieller Test — verschiedene Teilnehmer je Studie.

### 4.2 Aufbau

```
AnalysisPage
├── Breadcrumbs: Studienübersicht → Studien-Meta-Analyse
├── Studienauswahl-Panel
│   ├── Ladezustand (LoadingSpinner) während useStudies lädt
│   ├── Liste aller nicht-Entwurf-Studien (status !== "Entwurf")
│   ├── Multi-Select-Checkboxen
│   └── Button "Studien vergleichen" (disabled wenn < 2 gewählt)
├── Baseline-Eingabe (Number Input, default: 300ms, Label: "Realwelt-Baseline (ms)")
└── Ergebnis-Sektion (nur wenn ≥2 Studien gewählt und Vergleich gestartet)
    ├── Hinweis-Banner: "Deskriptiver Vergleich — kein inferenzieller Test (verschiedene Stichproben)"
    ├── Ladezustand während Fetch läuft (LoadingSpinner)
    ├── Fehlerfall (ErrorMessage)
    └── CrossStudyChart (vorhanden: components/CrossStudyChart.jsx)
```

### 4.3 Datenfluss

`fetchStudyPerformance` liefert aggregierte Statistiken (`by_condition[name].total_mean` etc.),
keine Raw-Arrays. `postCrossStudy` erwartet Raw-Arrays. Daher wird `postCrossStudy` **nicht**
für die AnalysisPage genutzt — stattdessen direkter Vergleich auf Basis der aggregierten Daten.

```
useStudies() → Studienliste (nur status !== "Entwurf" anzeigen)
  ↓ User wählt ≥2 Studien + klickt "Vergleichen"
fetchStudyPerformance(studyId) für jede gewählte Studie (parallel via Promise.all)
  ↓ Daten für CrossStudyChart aufbereiten:
    conditions = { [studyName]: { mean: total_mean, ci_lower, ci_upper, n } }
    Quelle: performance.by_condition → über alle Bedingungen mitteln oder beste nehmen
    (Vereinfachung: Gesamtmittelwert über alle Bedingungen pro Studie)
  ↓
<CrossStudyChart
  data={{ conditions, baseline_ms }}
  metric="Transfer Duration (ms)"
/>
```

**Wichtig:** `CrossStudyChart` erwartet einen `data`-Prop (kein Spread), der `conditions`
und `baseline_ms` enthält. Die JSX-Schreibweise muss exakt so sein.

**Feldmapping `fetchStudyPerformance` → `CrossStudyChart`:**

`fetchStudyPerformance` Response-Shape (aus `analyze_study_performance`):
```json
{
  "performance": {
    "by_condition": {
      "Bedingung A": { "total_mean": 850.3, "total_std": 120.1, "n": 18, ... },
      "Bedingung B": { "total_mean": 720.1, "total_std": 98.4,  "n": 17, ... }
    }
  },
  "n_experiments": 20
}
```

`CrossStudyChart` erwartet:
```json
{
  "conditions": {
    "Studie HS1": { "mean": 785.2, "ci_lower": 750.0, "ci_upper": 820.4, "n": 35 },
    "Studie HS2": { "mean": 650.0, "ci_lower": 610.0, "ci_upper": 690.0, "n": 30 }
  },
  "baseline_ms": 300
}
```

Aggregations-Logik im Frontend (pro Studie): Mittelwert der `total_mean`-Werte aller
Bedingungen; CI approximiert als `mean ± 1.96 * (gewichtete Std / sqrt(n_gesamt))`;
n = Summe der n-Werte aller Bedingungen; Label = Studienname aus `study.config.name`.

Fehlerfall: wenn eine Studie keine Performance-Daten hat (leere `by_condition`),
wird sie in der Ergebnis-Sektion mit Hinweis "Keine Daten" markiert, aber andere
Studien werden trotzdem angezeigt (kein vollständiger Abbruch).

### 4.4 Styling

Konsistent mit restlicher App: Tailwind CSS, `bg-gray-900 min-h-screen text-gray-100`.
Studienauswahl-Panel: `bg-gray-800 rounded-xl border border-gray-700`.
Hinweis-Banner: `bg-yellow-900 border-yellow-600 text-yellow-200` (nicht blockierend).

### 4.5 Status-Strings

Studienstatus-Werte aus dem Backend (aus `StudyTile.jsx` verifiziert):
`"Entwurf"`, `"Aktiv"`, `"Abgeschlossen"`. Filter: `status !== "Entwurf"`
schließt sowohl aktive als auch abgeschlossene Studien ein.

---

## 5. Lazy Tab Loading — Mechanismus

### 5.1 Prinzip

Daten werden nur geladen wenn der zugehörige Tab erstmals aktiviert wird.
Bereits geladene Daten bleiben gecacht (kein Re-fetch bei Tab-Wechsel).

### 5.2 ExperimentAnalyseTabs — Umbau auf CSS-Visibility

**Problem:** Das bestehende `ExperimentAnalyseTabs` gibt inaktive Tabs als `null` zurück
(vollständiges Unmounting). Das zerstört bei jedem Tab-Wechsel den Hook-State der
inaktiven Tabs, was die `enabled`-Flag-Strategie nutzlos macht.

**Lösung:** `ExperimentAnalyseTabs` und `TabPanel` werden umgebaut:
- Inaktive `TabPanel`-Instanzen rendern weiterhin, werden aber per CSS versteckt
- `TabPanel` bekommt `isActive`-Prop und rendert mit `hidden`-Klasse wenn inaktiv

```jsx
// ExperimentAnalyseTabs.jsx — geändert
export function ExperimentAnalyseTabs({ tabs, defaultKey, onTabChange, children }) {
    const [activeKey, setActiveKey] = useState(defaultKey ?? tabs[0].key);

    function handleClick(key) {
        setActiveKey(key);
        onTabChange?.(key);   // optional callback für Parent
    }

    return (
        <div>
            <div className="flex gap-2 mb-6">
                {tabs.map(tab => (
                    <button key={tab.key} onClick={() => handleClick(tab.key)}
                        className={`px-4 py-2 rounded ${activeKey === tab.key ? "bg-blue-700 text-white" : "bg-gray-700 text-gray-300"}`}>
                        {tab.label}
                    </button>
                ))}
            </div>
            {React.Children.map(children, child =>
                React.cloneElement(child, { isActive: child.props.tabKey === activeKey })
            )}
        </div>
    );
}

export function TabPanel({ children, isActive }) {
    return <div className={isActive ? '' : 'hidden'}>{children}</div>;
}
```

`onTabChange`-Callback ermöglicht dem Parent (`StudyAnalysisPage`, `ExperimentAnalysisPage`)
den `loadedTabs`-State zu aktualisieren.

### 5.3 Implementierung im Parent-Component

```jsx
const [loadedTabs, setLoadedTabs] = useState(new Set(['performance']));

function handleTabChange(tabKey) {
    setLoadedTabs(prev => new Set([...prev, tabKey]));
}
```

### 5.4 Hooks mit `enabled`-Flag

Alle Study-Hooks (`useStudyPerformanceMetrics`, `useStudyUxMetrics`,
`useStudyEyeTrackingMetrics`) und Experiment-Hooks (`useUxMetrics`, `usePerformanceMetrics`,
`useEyeTrackingMetrics`) erhalten ein optionales `enabled`-Parameter.

**Wichtig:** Initialer `loading`-State muss `false` sein wenn `enabled=false`,
damit inaktive Tabs keinen Spinner anzeigen bevor sie je aktiviert wurden.

```js
export function useStudyPerformanceMetrics(studyId, enabled = true) {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);   // false, nicht true
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!studyId || !enabled) return;
        setLoading(true);
        setError(null);
        fetchStudyPerformance(studyId)
            .then(setData)
            .catch(setError)
            .finally(() => setLoading(false));
    }, [studyId, enabled]);

    return { data, loading, error };
}
```

Hooks werden **nur gefetcht wenn `enabled === true`**. Der Effekt re-triggert automatisch
wenn `enabled` von `false` auf `true` wechselt.

---

## 6. StudyAnalysisPage — Refactoring

### 6.0 Entfernung der kombinierten Lade-Guards

Die aktuelle `StudyAnalysisPage.jsx` enthält folgende Blöcke die **entfernt** werden:

```js
// ENTFERNEN:
const loading = perfLoading || uxLoading || etLoading;
const error = perfError || uxError || etError;

if (loading) return ( <div>...</div> );
if (error)   return ( <div>...</div> );
```

Die Seiten-Shell (`Breadcrumbs`, `<h1>`, `ExperimentAnalyseTabs`) rendert immer.
Jeder Tab-Inhalt zeigt seinen eigenen `<LoadingSpinner>` oder `<ErrorMessage>`.

### 6.1 Tabs (nach Refactoring)

| Tab-Key | Label | Datenquelle | Laden |
|---|---|---|---|
| `performance` | Performance | `useStudyPerformanceMetrics` | sofort (default) |
| `questionnaires` | Fragebögen | `useStudyUxMetrics` | lazy |
| `eyetracking` | Eye-Tracking | `useStudyEyeTrackingMetrics` | lazy |
| `export` | Export | kein API-Call | sofort, kein Hook |

### 6.2 Export-Tab

Inhalt: CSV- und XLSX-Download-Buttons.
Nutzt `downloadStudyCsv(studyId)` und `downloadStudyXlsx(studyId)` aus
`inferentialAnalysisService.js` (vorhanden).
Download-Fehler werden als inline `ErrorMessage`-Komponente angezeigt (kein `alert()`).
Download-Zustand: `downloading`-State, Buttons disabled während Download läuft.
Kein `enabled`-Flag nötig — der Export-Tab hat keinen Hook.

### 6.3 Ladelogik und Tab-Verkabelung

Kein gemeinsamer kombinierter Loading-State mehr. Jeder Tab zeigt seinen eigenen
`LoadingSpinner` (vorhanden: `components/shared/LoadingSpinner.jsx`) und
`ErrorMessage` (vorhanden: `components/shared/ErrorMessage.jsx`).

`onTabChange` muss explizit an `ExperimentAnalyseTabs` weitergegeben werden:

```jsx
// StudyAnalysisPage.jsx
const [loadedTabs, setLoadedTabs] = useState(new Set(['performance']));

function handleTabChange(tabKey) {
    setLoadedTabs(prev => new Set([...prev, tabKey]));
}

// Im JSX:
<ExperimentAnalyseTabs tabs={TABS} defaultKey="performance" onTabChange={handleTabChange}>
    ...
</ExperimentAnalyseTabs>
```

Hooks-Aufruf mit `enabled`:
```js
const { data: studyPerformance, loading: perfLoading, error: perfError } =
    useStudyPerformanceMetrics(studyId, true);                           // sofort
const { data: studyQuestionnaires, loading: uxLoading, error: uxError } =
    useStudyUxMetrics(studyId, loadedTabs.has('questionnaires'));        // lazy
const { data: studyEyeTracking, loading: etLoading, error: etError } =
    useStudyEyeTrackingMetrics(studyId, loadedTabs.has('eyetracking')); // lazy
```

---

## 7. ExperimentAnalysisPage — Refactoring

### 7.1 Tabs (nach Refactoring)

| Tab-Key | Label | Datenquellen | Laden |
|---|---|---|---|
| `details` | Experiment Info | `useExperiment` + `useParticipantsForExperiment` | sofort (default) |
| `ux` | UX | `useUxMetrics` | lazy |
| `performance` | Performance | `usePerformanceMetrics` | lazy |
| `eyetracking` | Eye-Tracking | `useEyeTrackingMetrics` | lazy |
| `compare` | Vergleiche | nutzt UX + Performance Daten (bereits im State) | lazy, kein extra Fetch |

### 7.2 Details-Tab

`useExperiment` und `useParticipantsForExperiment` sind schnelle Calls (Metadaten).
Laden sofort — bilden die sinnvolle Default-Ansicht.

### 7.3 Vergleich-Tab

`ComparisonCharts` bekommt bereits im Parent gecachte `uxMetrics` und `performanceMetrics`.
Kein eigener Fetch nötig. Tab ist aktiv sobald beide Datensätze geladen wurden.
Wenn noch nicht geladen: Hinweis "Bitte zuerst die UX- und Performance-Tabs öffnen"
oder automatisches Triggern beider Fetches beim ersten Aufrufen des Vergleich-Tabs.

**Entscheidung:** Beim Aktivieren des Vergleich-Tabs werden UX und Performance automatisch
mitgetriggert (in `loadedTabs` hinzugefügt), damit kein manueller Umweg nötig ist.

### 7.4 Gemeinsamer Ladeindikator entfällt und Tab-Verkabelung

Der bisherige kombinierte `if (loading || ...) return <div>Lädt...</div>` (Zeile 57 in
`ExperimentAnalysisPage.jsx`) wird entfernt. Die Seiten-Shell rendert immer.

`onTabChange` und `handleTabChange` müssen explizit verdrahtet werden:

```jsx
// ExperimentAnalysisPage.jsx
const [loadedTabs, setLoadedTabs] = useState(new Set(['details']));

function handleTabChange(tabKey) {
    if (tabKey === 'compare') {
        setLoadedTabs(prev => new Set([...prev, tabKey, 'ux', 'performance']));
    } else {
        setLoadedTabs(prev => new Set([...prev, tabKey]));
    }
}

// Im JSX:
<ExperimentAnalyseTabs tabs={TABS} defaultKey="details" onTabChange={handleTabChange}>
    ...
</ExperimentAnalyseTabs>
```

Hooks-Aufruf mit `enabled`:
```js
const { data: uxMetrics, loading: uxLoading }           = useUxMetrics(experimentId, loadedTabs.has('ux'));
const { data: performanceMetrics, loading: perfLoading } = usePerformanceMetrics(experimentId, loadedTabs.has('performance'));
const { data: eyeTrackingData, loading: etLoading }      = useEyeTrackingMetrics(experimentId, loadedTabs.has('eyetracking'));
```

`useHandovers` und `computeMetricsPerTrial` werden vollständig entfernt (`_metricsPerTrial`
war durchgehend unused).

---

## 8. Hook-Änderungen (Zusammenfassung)

Folgende Hooks erhalten ein `enabled`-Parameter (default `true` für Rückwärtskompatibilität).
Initialer `loading`-State: `false` (war bisher `true`).

**Study-Hooks (nur `enabled`, kein `handedness` — Backend unterstützt Parameter noch nicht):**
- `useStudyPerformanceMetrics(studyId, enabled = true)`
- `useStudyUxMetrics(studyId, enabled = true)`
- `useStudyEyeTrackingMetrics(studyId, enabled = true)`

**Experiment-Hooks:**
- `useUxMetrics(experimentId, enabled = true)`
- `usePerformanceMetrics(experimentId, enabled = true)`
- `useEyeTrackingMetrics(experimentId, enabled = true)`

`useExperiment` und `useParticipantsForExperiment` bleiben unverändert (sofortiges Laden erwünscht).

`useHandovers` wird aus `ExperimentAnalysisPage` entfernt (wird dort nur für `computeMetricsPerTrial`
genutzt — `_metricsPerTrial` ist durchgehend unused/prefixed). Der Hook selbst bleibt erhalten
da er möglicherweise von anderen Stellen genutzt wird.

---

## 9. Navigations-Korrektheit (Prüfung)

Folgende Navigationspfade existieren bereits und bleiben unverändert:

| Von | Button/Link | Ziel |
|---|---|---|
| `StudyOverview` | "Statistiken" | `/analysis` ✓ |
| `StudyTile` | "Analyse" | `/study/:id/analysis` ✓ |
| `ExperimentOverview` | "Auswertung" | `/study/:id/analysis` ✓ |
| `ExperimentTile` | "Daten-Übersicht ansehen" | `/study/:id/experiment/:id/analysis` ✓ |

Alle Routen sind in `AppRouter.jsx` registriert. Keine Routing-Änderungen nötig.

---

## 10. Dateistruktur (nach Refactoring)

```
src/features/Analysis/
├── AnalysisPage.jsx                            ÄNDERN (Cross-Study-Inhalt)
├── StudyAnalysisPage.jsx                       ÄNDERN (lazy loading, export tab)
├── ExperimentAnalysisPage.jsx                  ÄNDERN (lazy loading, useHandovers entfernen)
├── pages/
│   └── AnalysisDashboard.jsx                   LÖSCHEN
├── components/
│   ├── PerformanceChart.jsx                    LÖSCHEN (nur von AnalysisDashboard genutzt)
│   ├── EyeTrackingChart.jsx                    LÖSCHEN (nur von AnalysisDashboard genutzt)
│   ├── experiment/PerformanceCharts.jsx        UNVERÄNDERT (anderer Name, anderer Kontext)
│   ├── experiment/EyeTrackingCharts.jsx        UNVERÄNDERT (anderer Name, anderer Kontext)
│   ├── CrossStudyChart.jsx                     UNVERÄNDERT
│   ├── shared/                                 UNVERÄNDERT
│   ├── charts/                                 UNVERÄNDERT
│   └── study/                                  UNVERÄNDERT
├── components/experiment/
│   └── ExperimentAnalyseTabs.jsx               ÄNDERN (CSS-Visibility statt null-return)
├── hooks/
│   ├── useStudyPerformanceMetrics.js           ÄNDERN (enabled, loading init false)
│   ├── useStudyUxMetrics.js                    ÄNDERN (enabled, loading init false)
│   ├── useStudyEyeTrackingMetrics.js           ÄNDERN (enabled, loading init false)
│   ├── useUxMetrics.js                         ÄNDERN (enabled, loading init false)
│   ├── usePerformanceMetrics.js                ÄNDERN (enabled, loading init false)
│   ├── useEyeTrackingMetrics.js                ÄNDERN (enabled, loading init false)
│   ├── useExperiment.js                        UNVERÄNDERT
│   └── useHandovers.js                         UNVERÄNDERT
└── services/                                   UNVERÄNDERT
```

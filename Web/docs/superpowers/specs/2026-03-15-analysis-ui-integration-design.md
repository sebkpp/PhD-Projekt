# Design-Spec: Analysis UI Integration — Session A

**Datum:** 2026-03-15
**Branch:** 20-web-interface-for-data-collection
**Referenz:** `docs/superpowers/specs/2026-03-14-statistische-auswertung-design.md` (Spec v2)
**Status:** Approved (v3 — nach Studiendesign-Review)

---

## 1. Studiendesign & Auswertungsebenen

### 1.1 Struktur

```
Studie
├── Experiment 1 (Teilnehmerpaar A)
│   ├── Trial 1 = Bedingung X → ~25–50 Handover-Interaktionen
│   ├── Trial 2 = Bedingung Y → ~25–50 Handover-Interaktionen
│   └── Trial 3 = Bedingung Z → ~25–50 Handover-Interaktionen
├── Experiment 2 (Teilnehmerpaar B) — gleiche Bedingungen
└── Experiment N (Teilnehmerpaar N) — gleiche Bedingungen
```

**Bedingungen (Trials) sind innerhalb einer Studie konstant.** Jedes Experiment-Paar
durchläuft alle Bedingungen (within-subject, permutiert).

### 1.2 Konsequenzen für Auswertungsebenen

| Ebene | n | Geeignet für |
|---|---|---|
| **Experiment** (1 Paar) | ~25–50 Handovers/Bedingung — vom **selben Paar** | Deskriptive Analyse, ET-Auswertung, Fragebogen-Display |
| **Studie** (N Paare) | n = Anzahl Experiment-Paare | Inferenzielle Tests (RM-ANOVA/Friedman), Effektgrößen, Correlationen, PCA |

**Inferenzielle Tests auf Experiment-Ebene sind Pseudoreplikation** (die 25–50 Handovers
kommen vom selben Paar und sind nicht unabhängig). Die echte statistische Aussagekraft liegt
auf Studienebene wo jedes Paar einen Datenpunkt pro Bedingung liefert.

---

## 2. Session-Aufteilung

### Session A (dieser Spec)
- Alle drei Analysis-Seiten erreichbar und funktional machen
- ExperimentAnalysisPage: vollständig deskriptive Auswertung + Layout-Gerüst mit Platzhaltern
- StudyAnalysisPage: inferenzielle Ergebnisse (die Backend bereits liefert) korrekt anzeigen
- Lazy Tab Loading (Performance-Optimierung)
- Neue Backend-Endpoints für Experiment-Ebene (ET-Phasen, Transitions, PPI)
- Backend-Migration: Questionnaire-Service auf N-Bedingungen aktualisieren
- Bereinigung verwaister Komponenten

### Session B (separater Spec)
- Neue Chart-Komponenten: PosthocHeatmap, PhaseAOIHeatmap, TransitionSankey,
  SaccadeRateBar, PPIBar, AttrakDiffMatrix, AttrakDiffRadar, NASATLXBar (bedingungsbasiert),
  SUSScoreBar (bedingungsbasiert), CorrelationMatrix, CorrelationScatter, PCABiplot
- Diese werden in die in Session A vorbereiteten Platzhalter eingebaut

---

## 3. Statistik-Implementierungsstand (Backend)

### 3.1 Inferenzielle Tests — vollständig implementiert

`inferential_service.py` → `run_inferential_analysis(conditions)`:
- **k=2:** Shapiro-Wilk → gepaarter t-Test oder Wilcoxon
- **k≥3, normal, n≥5:** RM-ANOVA (pingouin) + Bonferroni Post-hoc
- **k≥3, nicht-normal:** Friedman + Dunn-Test (Bonferroni-Korrektur)
- Sphericity: Mauchly-Test via pingouin, Greenhouse-Geisser-Korrektur automatisch

**Zu Tukey vs. Bonferroni:** Tukey war initial diskutiert; Pingouin unterstützt kein Tukey
für Repeated-Measures-Designs. Bonferroni ist für abhängige Stichproben methodisch korrekt
und konservativ. Akzeptiert.

### 3.2 Effektgrößen — vollständig implementiert

| Effektgröße | Berechnung | Wann |
|---|---|---|
| Cohen's d | `stats_utils.cohens_d()` | k=2 (parametrisch), Post-hoc |
| Cliff's Delta | `effect_size_service.cliffs_delta()` | k=2 (non-param.), Post-hoc |
| η²p (eta²p) | pingouin `ng2`-Spalte | RM-ANOVA Haupteffekt |
| ω²p (omega²p) | `effect_size_service.omega2p_from_anova()` | RM-ANOVA Haupteffekt |
| Kendall's W | `effect_size_service.kendalls_w_from_friedman()` | Friedman Haupteffekt |

Interpretationen (vernachlässigbar/klein/mittel/groß) für alle Maße vorhanden.

### 3.3 Wo diese Ergebnisse bereits in API-Responses enthalten sind

- `GET /analysis/study/{id}/performance` → enthält `inferential`-Block mit allen Tests und Effektgrößen ✅
- `GET /analysis/study/{id}/eyetracking` → enthält `analyze_aoi_inferential`-Ergebnisse ✅
- `GET /analysis/study/{id}/questionnaires` → enthält nur alten `run_paired_test` (k=2 only) ⚠️ → Migration nötig

### 3.4 Backend-Migration: Questionnaire-Service (Session A)

`questionnaire_analysis_service.py` nutzt noch `run_paired_test` (nur k=2).
Muss auf `run_inferential_analysis` (N-Bedingungen) migriert werden.

Änderung in `analyze_study_questionnaires`:
```python
# ALT:
inferential[item_name] = run_paired_test(...)

# NEU:
from Backend.services.data_analysis.inferential_service import run_inferential_analysis
# cond_dict = { condition_name: [experiment_means] }
inferential[item_name] = run_inferential_analysis(cond_dict)
```

---

## 4. Zu löschende Dateien (Bereinigung)

| Datei | Grund |
|---|---|
| `src/features/Analysis/pages/AnalysisDashboard.jsx` | Verwaist, nie geroutet |
| `src/features/Analysis/components/PerformanceChart.jsx` | Nur von AnalysisDashboard genutzt (self-fetching) |
| `src/features/Analysis/components/EyeTrackingChart.jsx` | Nur von AnalysisDashboard genutzt (self-fetching) |

`components/experiment/PerformanceCharts.jsx` und `EyeTrackingCharts.jsx` (Plural) bleiben
erhalten — andere Namen, anderer Kontext.

---

## 5. AnalysisPage (`/analysis`) — Cross-Study-Übersicht

### 5.1 Zweck

Deskriptiver Studien-übergreifender Vergleich. Kein inferenzieller Test
(verschiedene Teilnehmer je Studie).

### 5.2 Layout

```
AnalysisPage
├── Breadcrumbs: Studienübersicht → Studien-Meta-Analyse
├── Studienauswahl-Panel (bg-gray-800)
│   ├── LoadingSpinner während useStudies lädt
│   ├── Checkboxen: alle Studien mit status !== "Entwurf"
│   └── Button "Studien vergleichen" (disabled wenn < 2 gewählt)
├── Baseline-Eingabe (Number Input, default: 300ms)
└── Ergebnis-Sektion (erst nach Klick auf "Vergleichen")
    ├── Banner: "Deskriptiver Vergleich — kein inferenzieller Test"
    ├── LoadingSpinner / ErrorMessage
    └── CrossStudyChart (data={{ conditions, baseline_ms }} metric="Transfer Duration (ms)")
```

Status-Strings: `"Entwurf"` | `"Aktiv"` | `"Abgeschlossen"`. Filter: `!== "Entwurf"`.

### 5.3 Datenfluss

`postCrossStudy` wird **nicht** genutzt (erwartet Raw-Arrays). Direktaggregation:

```
useStudies() → Studienliste gefiltert
  ↓ User wählt ≥2 Studien + klickt
Promise.all(studyIds.map(fetchStudyPerformance))
  ↓ Aggregation pro Studie:
    mean   = Mittelwert der total_mean-Werte aller Bedingungen
    ci_low = mean − 1.96 * (gewichtete Std / √n_gesamt)
    ci_up  = mean + 1.96 * (gewichtete Std / √n_gesamt)
    n      = Summe aller n-Werte der Bedingungen
    label  = study.config.name
  ↓
CrossStudyChart({ data: { conditions, baseline_ms }, metric })
```

`CrossStudyChart` erwartet `data`-Prop: `{ conditions: { [label]: {mean, ci_lower, ci_upper, n} }, baseline_ms }`.

Studien ohne Performance-Daten: mit Hinweis markiert, andere weiter anzeigen.

---

## 6. ExperimentAnalyseTabs — Umbau auf CSS-Visibility

**Problem:** Aktuelle Implementierung gibt inaktive Tabs als `null` zurück → Unmounting
zerstört Hook-State, macht Lazy-Loading-Mechanismus nutzlos.

**Lösung:**

```jsx
// components/experiment/ExperimentAnalyseTabs.jsx
export function ExperimentAnalyseTabs({ tabs, defaultKey, onTabChange, children }) {
    const [activeKey, setActiveKey] = useState(defaultKey ?? tabs[0].key);

    function handleClick(key) {
        setActiveKey(key);
        onTabChange?.(key);
    }

    return (
        <div>
            <div className="flex gap-2 mb-6 flex-wrap">
                {tabs.map(tab => (
                    <button key={tab.key} onClick={() => handleClick(tab.key)}
                        className={`px-4 py-2 rounded transition-colors ${
                            activeKey === tab.key
                                ? "bg-blue-700 text-white"
                                : "bg-gray-700 text-gray-300 hover:bg-gray-600"
                        }`}>
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

export function TabPanel({ tabKey, children, isActive }) {
    return <div className={isActive ? '' : 'hidden'}>{children}</div>;
}
```

`isActive` wird von `TabPanel` konsumiert (nie auf DOM-Element weitergereicht → kein React-Warning).

---

## 7. Lazy Tab Loading — Mechanismus

### 7.1 loadedTabs-Pattern

```jsx
const [loadedTabs, setLoadedTabs] = useState(new Set(['<default-tab-key>']));

function handleTabChange(tabKey) {
    setLoadedTabs(prev => new Set([...prev, tabKey]));
}
```

### 7.2 Hooks mit `enabled`-Flag

Alle 6 betroffenen Hooks erhalten `enabled = true` als zweiten Parameter.
**Initialer `loading`-State = `false`** (nicht `true`), damit nie-aktivierte Tabs
keinen Spinner zeigen.

```js
export function useStudyPerformanceMetrics(studyId, enabled = true) {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
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

---

## 8. StudyAnalysisPage — Refactoring

### 8.1 Kombinierte Lade-Guards entfernen

```js
// ENTFERNEN (Zeilen 34–82 der aktuellen Datei):
const loading = perfLoading || uxLoading || etLoading;
const error = perfError || uxError || etError;
if (loading) return (...);
if (error)   return (...);
```

Seiten-Shell rendert immer. Jeder Tab zeigt eigenen `<LoadingSpinner>` / `<ErrorMessage>`.

### 8.2 Tabs

| Tab-Key | Label | Daten | Laden |
|---|---|---|---|
| `performance` | Performance | `useStudyPerformanceMetrics` | sofort (default) |
| `questionnaires` | Fragebögen | `useStudyUxMetrics` | lazy |
| `eyetracking` | Eye-Tracking | `useStudyEyeTrackingMetrics` | lazy |
| `export` | Export | kein Hook | sofort |

### 8.3 Inferenzielle Ergebnisse anzeigen (NEU in Session A)

Das Backend liefert in den Performance- und Eye-Tracking-Responses bereits vollständige
inferenzielle Ergebnisse (Tests, Effektgrößen, Post-hoc-Paare). Diese müssen im Frontend
sichtbar gemacht werden.

**Performance-Tab:** Nach den deskriptiven Charts (bereits vorhanden) wird ein
**Inferenz-Panel** angezeigt:
- Verwendeter Test (`test_used`): Anzeige als Badge (z.B. "RM-ANOVA + Bonferroni Post-hoc")
- Voraussetzungen: Shapiro-Wilk p-Werte pro Bedingung, Sphärizität (einklappbar)
- Haupteffekt: F/χ²-Statistik, p-Wert, Signifikanz-Marker, η²p / ω²p / Kendall's W
- Post-hoc-Paare: Tabelle mit Bedingungspaar | p_adjusted | Signifikanz | Cohen's d / Cliff's Delta + Interpretation
- Bestehende `InferentialResultBadge`-Komponente (`components/shared/`) für Badges nutzen
- `DescriptiveOnlyWarning` wenn n < 3 (kein Test möglich)

**Eye-Tracking-Tab:** Gleiches Inferenz-Panel für AOI-Dwell-Time-Ergebnisse.

**Fragebögen-Tab:** Nach Backend-Migration (Abschnitt 3.4) ebenfalls Inferenz-Panel.

**PosthocHeatmap** (vollständige Visualisierung) kommt in Session B. In Session A:
Post-hoc als kompakte Tabelle in der UI.

### 8.4 Export-Tab

```jsx
// Download-Buttons mit inline ErrorMessage (kein alert())
const [downloading, setDownloading] = useState(false);
const [downloadError, setDownloadError] = useState(null);
// downloadStudyCsv(studyId) und downloadStudyXlsx(studyId) aus inferentialAnalysisService
```

### 8.5 Tab-Verkabelung

```jsx
<ExperimentAnalyseTabs tabs={TABS} defaultKey="performance" onTabChange={handleTabChange}>
    <TabPanel tabKey="performance">
        {perfLoading && <LoadingSpinner />}
        {perfError && <ErrorMessage error={perfError} />}
        {studyPerformance && <StudyPerformanceCharts chartData={studyPerformance} />}
        {studyPerformance && <InferenzPanel data={studyPerformance.inferential} />}
    </TabPanel>
    ...
</ExperimentAnalyseTabs>
```

Hooks:
```js
const { data: studyPerformance } = useStudyPerformanceMetrics(studyId, true);
const { data: studyQuestionnaires } = useStudyUxMetrics(studyId, loadedTabs.has('questionnaires'));
const { data: studyEyeTracking } = useStudyEyeTrackingMetrics(studyId, loadedTabs.has('eyetracking'));
```

---

## 9. ExperimentAnalysisPage — Vollständige deskriptive Neustrukturierung

### 9.1 Analyseprinzip

**Nur deskriptiv.** Die ~25–50 Handovers pro Bedingung kommen vom selben Paar
(Pseudoreplikation). Inferenzielle Tests gehören auf Studienebene. Ein Hinweis-Banner
verweist bei Bedarf auf die Studien-Analyse.

### 9.2 Neue Tab-Struktur

| Tab-Key | Label | Datenquellen | Laden |
|---|---|---|---|
| `details` | Experiment Info | `useExperiment` + `useParticipantsForExperiment` | sofort |
| `performance` | Performance | `usePerformanceMetrics` | lazy |
| `eyetracking` | Eye-Tracking | `useEyeTrackingMetrics` + neue ET-Hooks | lazy |
| `ux` | Fragebögen / UX | `useUxMetrics` | lazy |
| `compare` | Vergleich | gecachte perf + ux Daten | lazy, triggert perf+ux |

### 9.3 Details-Tab (unverändert)

Experiment-Metadaten via `ExperimentDetails`. `useExperiment` + `useParticipantsForExperiment`
laden sofort (schnelle Calls).

### 9.4 Performance-Tab

Zeigt Handover-Daten deskriptiv **nach Bedingung** (Trial-Bedingung, nicht Trial-Nummer):

**Vorhandene Komponenten (direkt einbindbar):**
- `PerformanceCharts.jsx` → Boxplot + Stacked-Bar + Statistiktabelle (vorhanden, bedingungsbasiert)

**Platzhalter für Session B:**
```jsx
{/* SESSION B: PerformanceViolin */}
<PlaceholderChart label="Violinplot pro Bedingung (kommt in Session B)" />
{/* SESSION B: ErrorRateBar */}
<PlaceholderChart label="Fehlerrate pro Bedingung (kommt in Session B)" />
```

**Deskriptiver Hinweis:**
```jsx
<DescriptiveOnlyWarning
  message="Deskriptive Analyse eines Messdurchgangs. Inferenzielle Auswertung über alle Experimente → Studien-Analyse."
/>
```

### 9.5 Eye-Tracking-Tab

Drei neue Backend-Endpoints werden in Session A hinzugefügt (siehe Abschnitt 10).
Entsprechend drei neue Frontend-Hooks.

**Vorhandene Komponenten (direkt einbindbar):**
- `EyeTrackingCharts.jsx` → AOI Stacked Bar + Tabelle (vorhanden)

**Platzhalter für Session B:**
```jsx
{/* SESSION B: PhaseAOIHeatmap */}
<PlaceholderChart label="AOI × Phasen-Heatmap (kommt in Session B)" />
{/* SESSION B: TransitionSankey */}
<PlaceholderChart label="Blickpfad-Sankey (kommt in Session B)" />
{/* SESSION B: SaccadeRateBar */}
<PlaceholderChart label="Sakkaden-Rate pro Bedingung (kommt in Session B)" />
{/* SESSION B: GazeTimeline */}
<PlaceholderChart label="Gaze-Timeline (kommt in Session B)" />
{/* SESSION B: PPIBar */}
<PlaceholderChart label="Proaktiver Planungsindex (kommt in Session B)" />
```

**Was ist PPI:** Proaktiver Planungsindex = Anteil der Blickzeit des Gebers auf den
Aufgabenbereich (`environment`) in Phase 3 (Transfer). Hoher PPI (>30%) bedeutet: der
Geber schaut bereits zur nächsten Aufgabe, die Übergabe läuft automatisch-haptisch —
analog zum Realwelt-Befund (300ms Baseline). Getrennt für Geber und Empfänger berechnet.

### 9.6 Fragebögen/UX-Tab

**Vorhandene Komponenten:**
- `QuestionnaireCharts.jsx` → Items pro Bedingung (vorhanden)

**Platzhalter für Session B:**
```jsx
{/* SESSION B: NASATLXBar (bedingungsbasiert, 6 Subskalen) */}
<PlaceholderChart label="NASA-TLX Subskalen pro Bedingung (kommt in Session B)" />
{/* SESSION B: SUSScoreBar */}
<PlaceholderChart label="SUS-Score pro Bedingung (kommt in Session B)" />
{/* SESSION B: AttrakDiffMatrix (Portfolio) */}
<PlaceholderChart label="AttrakDiff2 Portfolio-Matrix (kommt in Session B)" />
{/* SESSION B: AttrakDiffRadar */}
<PlaceholderChart label="AttrakDiff2 Subskalen-Radar (kommt in Session B)" />
```

### 9.7 Vergleich-Tab

Aktivierung triggert automatisch Performance + UX laden:
```js
if (tabKey === 'compare') {
    setLoadedTabs(prev => new Set([...prev, tabKey, 'performance', 'ux']));
}
```

Vorhandene `ComparisonCharts.jsx` bleibt. Platzhalter für Session B:
```jsx
{/* SESSION B: CorrelationMatrix */}
<PlaceholderChart label="Korrelationsmatrix (kommt in Session B)" />
```

### 9.8 PlaceholderChart-Komponente (neu, klein)

Minimale Komponente die einen beschrifteten Rahmen mit Hinweis rendert:
```jsx
// components/shared/PlaceholderChart.jsx
export default function PlaceholderChart({ label }) {
    return (
        <div className="border border-dashed border-gray-600 rounded-xl p-6 text-center text-gray-500 my-4">
            <div className="text-sm">{label}</div>
        </div>
    );
}
```

### 9.9 Entfernung des kombinierten Ladeindikators

Zeile 57 in `ExperimentAnalysisPage.jsx` (`if (loading || ...) return`) wird entfernt.
`useHandovers` und `computeMetricsPerTrial` werden vollständig entfernt
(`_metricsPerTrial` war unused).

---

## 10. Neue Backend-Endpoints (Experiment-Ebene)

Diese Endpoints existieren noch nicht und werden in Session A hinzugefügt:

```
GET /api/analysis/experiment/{experiment_id}/eyetracking/phases
GET /api/analysis/experiment/{experiment_id}/eyetracking/transitions
GET /api/analysis/experiment/{experiment_id}/ppi
```

Die Berechnungslogik existiert bereits in `eye_tracking_analysis_service.py`
(phasenweise Zuordnung, Transition-Matrix, PPI-Berechnung). Es müssen nur die
Route-Handler in `Backend/routes/analysis.py` und die Service-Aufrufe ergänzt werden.

Entsprechende Frontend-Hooks:
```
hooks/useEyeTrackingPhases.js      (experimentId, enabled)
hooks/useEyeTrackingTransitions.js (experimentId, enabled)
hooks/usePPI.js                    (experimentId, enabled)
```

---

## 11. Hook-Änderungen (vollständige Liste)

### Bestehende Hooks — `enabled`-Flag hinzufügen, `loading` init `false`

| Hook | Änderung |
|---|---|
| `useStudyPerformanceMetrics.js` | `enabled = true`, `loading` init `false` |
| `useStudyUxMetrics.js` | `enabled = true`, `loading` init `false` |
| `useStudyEyeTrackingMetrics.js` | `enabled = true`, `loading` init `false` |
| `useUxMetrics.js` | `enabled = true`, `loading` init `false` |
| `usePerformanceMetrics.js` | `enabled = true`, `loading` init `false` |
| `useEyeTrackingMetrics.js` | `enabled = true`, `loading` init `false` |

### Neue Hooks (Session A)

| Hook | Endpoint | Wo genutzt |
|---|---|---|
| `useEyeTrackingPhases.js` | `/experiment/{id}/eyetracking/phases` | ExperimentAnalysisPage ET-Tab |
| `useEyeTrackingTransitions.js` | `/experiment/{id}/eyetracking/transitions` | ExperimentAnalysisPage ET-Tab |
| `usePPI.js` | `/experiment/{id}/ppi` | ExperimentAnalysisPage ET-Tab |

Unverändert: `useExperiment`, `useParticipantsForExperiment`, `useHandovers`.

---

## 12. Navigations-Korrektheit

Alle Routen und Navigations-Buttons existieren bereits. Keine Routing-Änderungen.

| Von | Button | Ziel |
|---|---|---|
| `StudyOverview` | "Statistiken" | `/analysis` ✓ |
| `StudyTile` | "Analyse" | `/study/:id/analysis` ✓ |
| `ExperimentOverview` | "Auswertung" | `/study/:id/analysis` ✓ |
| `ExperimentTile` | "Daten-Übersicht ansehen" | `/study/:id/experiment/:id/analysis` ✓ |

---

## 13. Dateistruktur nach Session A

```
Backend/
├── routes/analysis.py                          ÄNDERN (+3 neue ET-Endpoints)
├── services/data_analysis/
│   └── questionnaire_analysis_service.py       ÄNDERN (run_paired_test → run_inferential_analysis)

src/features/Analysis/
├── AnalysisPage.jsx                            ÄNDERN (Cross-Study-Inhalt)
├── StudyAnalysisPage.jsx                       ÄNDERN (lazy loading, Inferenz-Panel, export tab)
├── ExperimentAnalysisPage.jsx                  ÄNDERN (neue Tab-Struktur, deskriptiv, Platzhalter)
├── pages/AnalysisDashboard.jsx                 LÖSCHEN
├── components/
│   ├── PerformanceChart.jsx                    LÖSCHEN
│   ├── EyeTrackingChart.jsx                    LÖSCHEN
│   ├── shared/PlaceholderChart.jsx             NEU
│   └── experiment/ExperimentAnalyseTabs.jsx    ÄNDERN (CSS-Visibility)
├── hooks/
│   ├── useStudyPerformanceMetrics.js           ÄNDERN
│   ├── useStudyUxMetrics.js                    ÄNDERN
│   ├── useStudyEyeTrackingMetrics.js           ÄNDERN
│   ├── useUxMetrics.js                         ÄNDERN
│   ├── usePerformanceMetrics.js                ÄNDERN
│   ├── useEyeTrackingMetrics.js                ÄNDERN
│   ├── useEyeTrackingPhases.js                 NEU
│   ├── useEyeTrackingTransitions.js            NEU
│   └── usePPI.js                               NEU
└── services/                                   UNVERÄNDERT
```

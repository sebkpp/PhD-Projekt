# Design-Spec: Umfassende statistische Auswertung — VR-Handover-Studie

**Datum:** 2026-03-14
**Branch:** 20-web-interface-for-data-collection
**Projekt:** PhD-Studie — VR-chirurgisches Instrumenten-Handover
**Status:** Draft v2 (nach Reviewer-Feedback)

---

## 1. Kontext & Ziel

### 1.1 Studienaufbau

Die Untersuchung analysiert Handover-Interaktionen in VR. Zwei Teilnehmende führen eine
kooperative Aufgabe durch, bei der Objekte zwischen den Partnern übergeben werden müssen.
Reihenfolge der Übergaben: teilnehmergesteuert. Das System ist szenario-agnostisch —
Aufgabentyp, Objekttypen und Anzahl der Übergaben variieren je Studie (siehe 1.4).

*Erste Instanz (Bauklötzchen-Studie):* je 50 Objekte pro Person, davon 25 zu übergeben →
pro Trial symmetrisch: 25× Geber, 25× Empfänger pro Teilnehmer.

**Zwei unabhängige Variablen:**

| Faktor | Ausprägungen | Ebene |
|---|---|---|
| Stimulus | 15 konkrete Stimuli; 3 Typen (visual, auditory, tactile); Kombinationen | TrialSlot |
| Avatar Visibility | hands / head+hands / full | TrialSlot |

**Studiensequenz (je Studie neue Teilnehmer):**

| Studie | Typ | Vergleich | AV |
|---|---|---|---|
| VS1 | Visibility-Studie | Avatar Visibility: hands vs. head+hands vs. full | kein Stimulus |
| HS1 | Hauptstudie | Visuelle Stimuli untereinander | AV aus VS1 |
| VS2 | Visibility-Studie (unabhängig) | Auditive Stimuli untereinander | unabhängig |
| HS2 | Hauptstudie | V(best) vs. A(best) vs. V+A | AV aus VS1 |
| VS3 | Visibility-Studie (unabhängig) | Taktile Stimuli untereinander | unabhängig |
| HS3 | Hauptstudie | T(best) vs. T+V vs. T+A vs. T+A+V + A (Referenz) | AV aus VS1 |

*VS = Vorstudien (Visibility- bzw. unimodale Stimulus-Studie), HS = Hauptstudie (Modalitätsvergleich)*

**Within-Subject:** Jedes Experiment-Paar durchläuft alle Bedingungen (permutiert via `trials_permuted`).
**Between-Study:** Verschiedene Teilnehmer je Studie → Cross-Study-Vergleiche nur deskriptiv.

### 1.4 Szenario-Unabhängigkeit (Design-Constraint)

Das Analyse-System ist **szenario-agnostisch** zu implementieren. Der Bauklötzchen-Kontext
(VS1–HS3) ist die erste Instanz — es ist geplant, dieselbe Plattform auf andere Kontexte
zu übertragen (z.B. VR-Operations-Szenario mit Skalpell, Schere, Klemme etc.).

Folgende Parameter **dürfen nicht hardcodiert** werden:
- **Objekt-Typen** (`grasped_object`): Freitext, variiert je Szenario
- **Anzahl Handovers pro Trial**: variiert je Szenario und Teilnehmerpaar
- **Anzahl Trials pro Experiment**: konfigurierbar über `study_config.trial_number`
- **AOI-Definitionen**: kommen aus der DB (`area_of_interest`-Tabelle), nicht aus Code
- **Stimulus-Typen und -Namen**: kommen aus der DB (`stimulus`-Tabelle)
- **Szenario-spezifische Schwellenwerte** (z.B. "gute" Transferzeit): nur als
  konfigurierbare Referenzwerte (wie `baseline_ms`), nicht als Konstante im Code

Das bedeutet konkret: alle Gruppierungen, Labels und Metriken werden dynamisch aus den
Datenbankeinträgen abgeleitet. Tests verwenden synthetische Daten die verschiedene
Objekt-Typen und Handover-Zahlen abdecken.

### 1.2 Theoretischer Rahmen

**Realwelt-Baseline:** Voruntersuchung (120Hz-Kamera, Inter-Rater-Reliabilität ICC=88%)
ergab ~300ms reine Transferzeit. Geber schaut während der Übergabe bereits zurück zur
nächsten Aufgabe (haptisch-automatisch).

**Wickens Multiple Resource Theory (MRT):** Visuelle Stimuli konkurrieren mit visueller
Aufmerksamkeit für Aufgabenplanung; auditive/taktile Stimuli nutzen andere Ressourcenkanäle.
Hypothese: Taktile Stimuli replizieren den Realwelt-Automatismus am besten.

### 1.3 Analysedimensionen

Das System unterstützt drei Analyseebenen:
- **Innerhalb einer Studie:** Within-Subject inferenzielle Tests (RM-ANOVA / Friedman)
- **Innerhalb eines Experiments:** Deskriptiv pro Trial
- **Zwischen Studien:** Nur deskriptiv (Effektgrößen + CIs, kein inferenzieller Test)

---

## 2. Schema-Erweiterungen

### 2.1 Handover: Fehler-Tracking

```sql
ALTER TABLE handover
  ADD COLUMN is_error BOOLEAN DEFAULT FALSE,
  ADD COLUMN error_type VARCHAR(100);
  -- error_type: 'dropped', 'missed', 'timeout', 'incomplete'
```

**ORM:** `Handover`-Modell um `is_error: bool` und `error_type: Optional[str]` erweitern.

**Unity-Kompatibilität:** Die neuen Felder werden **ausschließlich durch die Web-Applikation**
gesetzt (manuell durch Forscher oder automatisch über zukünftige Unity-Integration).
Bestehende Unity-API-Endpunkte (`POST /handover`) bleiben unverändert; die neuen Felder
haben Defaults und sind optionale Ergänzungen. Unity-Schema-Kompatibilität: nicht betroffen.

### 2.2 Study: Typ-Konfiguration

```sql
ALTER TABLE study_config
  ADD COLUMN study_type VARCHAR(50) DEFAULT 'stimulus_comparison';
  -- Werte: 'avatar_comparison', 'stimulus_comparison', 'combination_comparison'
```

**ORM:** `StudyConfig`-Modell entsprechend erweitern.

### 2.3 Keine Migrations-Tooling

Das Projekt verwendet kein Alembic. Schema-Änderungen werden manuell in `sql/schema.sql`
gepflegt. SQLAlchemy erstellt fehlende Spalten nicht automatisch — die ALTER TABLE-Statements
müssen manuell auf der Produktions-DB ausgeführt werden.

---

## 3. Backend: Analyse-Services

### 3.1 Architektur & Migrationsplan

Bestehende Services werden **schrittweise refaktoriert**, nicht auf einmal ersetzt.

```
Backend/services/data_analysis/
├── descriptive_service.py           # Deskriptive Statistik (allgemein)
├── performance_analysis_service.py  # Handover-Performance (erweitert)
├── eye_tracking_analysis_service.py # Eye-Tracking (erweitert)
├── questionnaire_analysis_service.py # Fragebogen (erweitert)
├── inferential_service.py           # NEU: RM-ANOVA, Friedman, Post-hoc
├── effect_size_service.py           # NEU: η²p, ω², Cohen's d, Cliff's Delta
├── correlation_service.py           # NEU: Pearson/Spearman, Kovariaten
└── cross_study_service.py           # NEU: Deskriptiver Cross-Study-Vergleich

Backend/utils/
└── stats_utils.py                   # NEU: sanitize_stats, cohens_d, run_paired_test (migriert)
```

**Migrationsplan für bestehende Inferenzlogik:**

Der bestehende Code in `performance_analysis_service.py` (Funktion `run_paired_test`,
`cohens_d`, `sanitize_stats`) und die Nutzung in `questionnaire_analysis_service.py`
wird in dieser Reihenfolge migriert:

1. `sanitize_stats`, `cohens_d`, `run_paired_test` nach `utils/stats_utils.py` verschieben
2. Alle bestehenden Imports aktualisieren
3. Die hartcodierte Zweikondition-Logik (`cond_a, cond_b = conditions[0], conditions[1]`)
   in `performance_analysis_service.py` (Zeilen ~301–311) und `questionnaire_analysis_service.py`
   durch Aufrufe an den neuen `inferential_service` ersetzen
4. Bestehende Tests anpassen und sicherstellen dass alle Tests weiterhin grün sind

Die bestehenden API-Endpunkte bleiben während der Migration lauffähig.

### 3.2 Gemeinsame Konventionen

- Alle Services empfangen `session` + IDs + optionalen `handedness`-Filter (`right|left|all`)
- N-Bedingungen: keine Hardcodierung auf 2 Bedingungen — alle Gruppierungen sind generisch
- Bestehende Pydantic Response-Modelle bleiben unverändert; neue Endpunkte erhalten neue Modelle

**Händigkeits-Filter: Join-Strategie je Service-Typ:**

| Service | Filterpfad | Semantik |
|---|---|---|
| Performance | `Handover.giver → Participant.handedness` | Händigkeit des Gebers |
| Eye-Tracking | `EyeTracking.participant_id → Participant.handedness` | Händigkeit des beobachteten TN |
| Questionnaire | `QuestionnaireResponse.participant_id → Participant.handedness` | Händigkeit des antwortenden TN |
| Correlation | Participant-Tabelle direkt | Händigkeit der Kovariate |

Bei `handedness=right`: nur Datenpunkte einbeziehen wo der jeweilige Teilnehmer Rechtshänder ist.
Bei `handedness=all` (default): kein Filter angewendet.
Empfänger-Händigkeit wird nicht als Filterkriterium für Performance verwendet — der Geber
initiiert und kontrolliert die Übergabe und ist die primäre Analyseeinheit.

### 3.3 Performance Analysis (erweitert)

**Neue Metriken:**
- `error_rate`: `is_error=True` Handovers / Gesamtzahl Handovers pro Bedingung
- `object_stats`: Deskriptive Statistik getrennt nach `grasped_object` (Objekt-Typ) UND aggregiert

**Gruppierungsdimensionen** (alle kombinierbar):
- nach Bedingung (Stimulus-Name oder -Typ)
- nach Avatar Visibility
- nach Objekt-Typ (`grasped_object`) — separat und aggregiert
- nach Rolle (giver / receiver) — für PPI-spezifische Analysen

**Phasen-Definitionen:**
```
Phase 1 (Coordination Latency): giver_grasped_object → receiver_touched_object
Phase 2 (Grasp Latency):        receiver_touched_object → receiver_grasped_object
Phase 3 (Transfer Duration):    receiver_grasped_object → giver_released_object
Total:                          giver_grasped_object → giver_released_object
```

### 3.4 Eye-Tracking Analysis (erweitert)

**Basis:** AOI-Fixations-Events (starttime, endtime, duration, aoi_id). Die 5 AOIs im System:

| AOI-Name (DB) | Label | Verfügbar bei AvatarVis |
|---|---|---|
| `partner_face` | Gesicht des anderen Avatars | head+hands, full |
| `object` | Übergabeobjekt | immer |
| `own_hand` | Eigene Hand | immer |
| `partner_hand` | Hand des Partners | immer |
| `environment` | Sonstige Umgebung / Aufgabenbereich | immer |

**Timestamp-Synchronisierungsannahme (C-2):**
Unity-VR-System und Eye-Tracker verwenden **dieselbe Systemuhr** (gleicher Rechner/Netzwerk-NTP).
Die Timestamps in `eye_tracking.starttime`/`endtime` und `handover.giver_grasped_object` etc.
sind direkt vergleichbar. Falls Uhren-Drift auftritt (>10ms), ist die Phasenzuordnung
ungenau — das muss bei der Datenerhebung überwacht werden. Diese Prämisse ist
in der Dissertation zu dokumentieren.

**AOI fehlt bei bestimmter AvatarVis:** Wenn `avatar_visibility = hands`,
existiert `partner_face` nicht im VR-Environment → keine Fixationen auf diese AOI
→ `partner_face`-Werte erscheinen in der Ausgabe als `null` bzw. werden übersprungen.
Kein Konfund — die Daten sind intern konsistent.

**Berechnete Metriken pro Bedingung:**

| Metrik | Beschreibung |
|---|---|
| `dwell_time_ms` | Summe Fixationsdauern pro AOI |
| `dwell_percentage` | Anteil an Gesamtblickzeit (%) |
| `fixation_count` | Anzahl Fixations-Events pro AOI |
| `mean_fixation_duration_ms` | Mittlere Einzelfixationsdauer pro AOI |
| `saccade_count` | Anzahl AOI-Wechsel (konsekutive Events auf verschiedene AOIs) |
| `saccade_rate` | Sakkaden pro Sekunde (saccade_count / Gesamtdauer) |
| `transition_matrix` | 5×5 Matrix: Häufigkeit der AOI-Wechselpaare (AOI_i → AOI_j) |

**Phasenweise Auswertung (temporal):**
EyeTracking-Records werden vor Berechnung **nach `starttime ASC` sortiert** (Voraussetzung
für korrekte Sakkaden-Erkennung und Phasenzuordnung).
Jede Fixation (via `starttime`) wird der Handover-Phase zugeordnet in der sie liegt.
Bedingung: `phase_start ≤ fixation.starttime < phase_end` der jeweiligen Phase.
Ergebnis: `phase_aoi_distribution[phase_1|2|3][aoi_name]` = Dwell-Time-% pro Phase × AOI.

**Proaktiver Planungsindex (PPI):**
```
PPI_giver   = dwell_time("environment", phase=3, participant=giver) /
              total_phase3_duration × 100
PPI_receiver = dwell_time("environment", phase=3, participant=receiver) /
               total_phase3_duration × 100
```
Berechnet **getrennt** für Geber und Empfänger.
Hoher PPI (>30%) = Übergabe läuft automatisch, visuelle Kapazität frei für nächsten Task.

### 3.5 Questionnaire Analysis (erweitert)

**Instrument-aware Scoring** vor jeder statistischen Analyse.
Instrument-Erkennung: automatisch über `questionnaire.name`-Feld (exakter String-Match).

**Naming-Conventions (Data Contract):**

*AttrakDiff2* — Subskalen-Zuordnung über Präfix in `questionnaire_item.item_name`:
- `pq_*` → PQ (Pragmatische Qualität)
- `hqs_*` → HQS (Hedonische Qualität – Stimulation)
- `hqi_*` → HQI (Hedonische Qualität – Identität)
- `att_*` → ATT (Attraktivität)

*ISO-Metrics* — Subskalen-Zuordnung über `questionnaire_item.item_description`-Feld
(exakter String-Match der Subskala-Bezeichnungen):
- `"Aufgabenangemessenheit"` → Subskala 1
- `"Selbstbeschreibungsfähigkeit"` → Subskala 2
- `"Steuerbarkeit"` → Subskala 3
- `"Erwartungskonformität"` → Subskala 4
- `"Individualisierbarkeit"` → Subskala 5
- `"Fehlertoleranz"` → Subskala 6
- `"Lernförderlichkeit"` → Subskala 7

**Scoring-Formeln:**

| Fragebogen | Scoring |
|---|---|
| NASA-TLX | Mittelwert der 6 Items (Raw TLX, 0–100) |
| SUS | Ungerade Items (1,3,5,7,9): (x−1)×2.5; Gerade (2,4,6,8,10): (5−x)×2.5; Summe → 0–100 |
| AttrakDiff2 | 4 Subskalen-Mittelwerte (PQ, HQS, HQI, ATT); HQ = Mittelwert(HQS, HQI) |
| ISO-Metrics | 7 Subskalen-Mittelwerte über `item_description` |
| Eigene | Mittelwert aller Items |

### 3.6 Inferential Service (neu)

**Test-Selektion (automatisch, pro abhängige Variable):**

```
k = Anzahl Bedingungen

k == 2:
  Shapiro-Wilk pro Gruppe (n ≥ 4)
    beide p ≥ 0.05 → gepaarter t-Test
    sonst → Wilcoxon-Test
  Effektgröße: Cohen's d (parametrisch) oder Cliff's Delta (non-parametrisch)

k >= 3:
  Shapiro-Wilk pro Gruppe (n ≥ 4)
    alle p ≥ 0.05 → normalverteilt
      pingouin.rm_anova(correction='auto')
        → führt Mauchly intern aus
        → Sphärizität ok: RM-ANOVA
        → verletzt: RM-ANOVA + Greenhouse-Geisser-Korrektur
    mind. 1 Gruppe p < 0.05 → Friedman-Test
```

**Post-hoc Tests (alle n×(n-1)/2 Paare):**

| Haupttest | Post-hoc | Korrektur |
|---|---|---|
| k=2 t-Test / Wilcoxon | keiner (nur ein Paar) | — |
| RM-ANOVA | pingouin pairwise_tests (Tukey HSD) | auto |
| RM-ANOVA + GG | Bonferroni paarweise t-Tests | Bonferroni |
| Friedman | Dunn-Test (scikit_posthocs) | Bonferroni oder FDR |

**Ausgabe-Struktur pro abhängige Variable:**
```json
{
  "test_used": "paired_ttest | wilcoxon | rm_anova | rm_anova_gg | friedman",
  "n_conditions": 3,
  "normality": {"condition_A": 0.23, "condition_B": 0.05, "condition_C": 0.31},
  "sphericity_p": 0.12,
  "sphericity_correction": "none | greenhouse_geisser",
  "main_effect": {
    "statistic": 12.4,
    "p_value": 0.002,
    "significant": true,
    "effect_eta2p": 0.18,
    "effect_omega2p": 0.15,
    "effect_kendalls_w": null
  },
  "posthoc": [
    {
      "pair": ["condition_A", "condition_B"],
      "p_value": 0.003,
      "p_adjusted": 0.009,
      "correction": "bonferroni",
      "effect_size_d": 0.74,
      "effect_size_cliffs_delta": 0.41,
      "significant": true
    }
  ]
}
```

**Mindest-Stichprobe:**
- Shapiro-Wilk: n ≥ 4 pro Gruppe (`len(series) > 3`); bei n < 4: Test übersprungen, non-parametrisch
- RM-ANOVA: n ≥ 5 pro Bedingung für stabile Varianzschätzung; bei n < 5: direkt Friedman
- Friedman: n ≥ 3 ausreichend; bei n < 3: kein inferenzieller Test möglich
- UI-Warnung bei n < 5 pro Bedingung

### 3.7 Effect Size Service (neu)

| Maß | Implementierung | Wann |
|---|---|---|
| η²p | pingouin rm_anova Output-Spalte `np2` | RM-ANOVA Haupteffekt |
| ω²p | manuell: `(SS_effect - df_effect * MS_error) / (SS_total + MS_error)` | RM-ANOVA, Publikationen |
| Kendall's W | pingouin friedman Output | Friedman-Test |
| Cohen's d | `(mean_a - mean_b) / pooled_std` | Post-hoc parametrisch, k=2 |
| Cliff's Delta | manuelle Implementierung (siehe unten) | Post-hoc non-parametrisch + Fragebögen |

**Cliff's Delta — manuelle Implementierung (kein separates Package nötig):**
```python
def cliffs_delta(x: list, y: list) -> float | None:
    if not x or not y:
        return None
    dominance = sum(
        1 if xi > yj else (-1 if xi < yj else 0)
        for xi in x for yj in y
    )
    return dominance / (len(x) * len(y))
```

### 3.8 Correlation Service (neu)

**Auto-Selektion:** Shapiro-Wilk auf beide Variablen → beide p ≥ 0.05: Pearson r; sonst: Spearman ρ.

**Analysierte Zusammenhänge:**
- Alter × Performance-Phasen (alle 4 Metriken)
- Alter × Questionnaire-Scores (je Instrument/Subskala)
- Alter × Eye-Tracking-Metriken (Sakkaden-Rate, PPI)
- Händigkeit: deskriptiv (Boxplots je Gruppe), kein inferenzieller Test (kategorial)

**Ausgabe:** Korrelationskoeffizient, p-Wert (Bonferroni-korrigiert über alle Tests), r².

**Filter:** Alle Analysen akzeptieren `handedness: right | left | all` (default: `all`).

### 3.9 Cross-Study Service (neu)

Lädt aggregierte Ergebnisse aus mehreren Studien (via Liste von `study_id`s).
**Kein inferenzieller Test** (verschiedene Teilnehmer je Studie).

**Response-Schema für `GET /analysis/cross-study`:**
```json
{
  "baseline_ms": 300,
  "studies": [
    {
      "study_id": 1,
      "study_name": "HS1 — Visuelle Stimuli",
      "conditions": ["inner_hand", "outer_hand"],
      "metrics": {
        "total_mean_ms": 850.3,
        "total_ci_lower": 780.1,
        "total_ci_upper": 920.5,
        "effect_size_d": 0.62,
        "effect_size_ci_lower": 0.31,
        "effect_size_ci_upper": 0.93,
        "n_experiments": 20
      }
    }
  ]
}
```

Referenzlinie `baseline_ms` = 300ms (Standard, pro Studie überschreibbar).

---

## 4. Backend: API-Endpunkte

Neue Endpunkte unter `/api/analysis/`:

```
GET /analysis/study/{study_id}/inferential
GET /analysis/study/{study_id}/correlations
GET /analysis/study/{study_id}/eye-tracking/phases
GET /analysis/study/{study_id}/eye-tracking/transitions
GET /analysis/study/{study_id}/ppi
GET /analysis/cross-study?study_ids=1,2,3&baseline_ms=300
GET /analysis/experiment/{experiment_id}/inferential
GET /analysis/experiment/{experiment_id}/eye-tracking/phases
GET /analysis/experiment/{experiment_id}/ppi
```

Optionaler Query-Parameter für alle Endpunkte: `?handedness=right|left|all` (default: `all`)

**Pydantic Response-Modelle** für alle neuen Endpunkte (in `models/analysis.py`).
Bestehende Endpunkte (performance, questionnaires, eyetracking) erhalten **keine** neuen
Response-Modelle in diesem Scope — das wäre eine separate Aufgabe.

---

## 5. Frontend: Visualisierungen

### 5.1 Frontend Service-Architektur

Neue API-Calls werden in **einem neuen Service** gebündelt:
`src/features/Analysis/services/inferentialAnalysisService.js`

Bestehende Services (`studyAnalysisService.js`, `experimentAnalysisService.js`) bleiben
unverändert. Neue Komponenten importieren ausschließlich aus dem neuen Service.

### 5.2 Kategorie 1 — Performance & Verhalten

| Komponente | Bibliothek | Endpunkt |
|---|---|---|
| `PerformanceBoxplot` | Plotly | study/performance |
| `PerformanceBarCI` | Plotly | study/performance |
| `PerformanceViolin` | Plotly | study/performance |
| `ErrorRateBar` | Recharts | study/performance |
| `PosthocHeatmap` | Plotly Heatmap | study/inferential |

### 5.3 Kategorie 2 — Eye-Tracking

| Komponente | Bibliothek | Endpunkt |
|---|---|---|
| `AOIDwellStackedBar` | Plotly | study/eyetracking |
| `PhaseAOIHeatmap` | Plotly | study/eye-tracking/phases |
| `TransitionSankey` | Plotly Sankey | study/eye-tracking/transitions |
| `SaccadeRateBar` | Recharts | study/eye-tracking/transitions |
| `GazeTimeline` | Plotly Gantt | experiment/eye-tracking/phases |
| `PPIBar` | Recharts | study/ppi |

### 5.4 Kategorie 3 — Fragebögen

| Komponente | Bibliothek | Endpunkt |
|---|---|---|
| `NASATLXBar` | Recharts | study/questionnaires |
| `SUSScoreBar` | Recharts | study/questionnaires |
| `AttrakDiffMatrix` | Plotly Scatter | study/questionnaires |
| `AttrakDiffRadar` | Recharts Radar | study/questionnaires |
| `ISOMetricsHeatmap` | Plotly | study/questionnaires |
| `QuestionnaireItemHeatmap` | Plotly | study/questionnaires |

**AttrakDiff Portfolio-Matrix:** X-Achse = PQ (-3 bis +3), Y-Achse = HQ = Mittelwert(HQS, HQI).
Quadranten: begehrt (oben rechts), aufgabenorientiert (unten rechts),
selbstorientiert (oben links), überflüssig (unten links).
Konfidenz-Rechtecke = ±1 SE um Mittelpunkt je Bedingung.

### 5.5 Kategorie 4 — Zusammenhänge & Muster

| Komponente | Bibliothek | Endpunkt |
|---|---|---|
| `CorrelationScatter` | Plotly | study/correlations |
| `CorrelationMatrix` | Plotly Heatmap | study/correlations |
| `PCABiplot` | Plotly | study/exploratory |
| `ClusterDendrogram` | Plotly | study/exploratory |

**PCA und Clustering: serverseitige Berechnung** via `GET /analysis/study/{study_id}/exploratory`.
Service: `exploratory_service.py` (NEU). PCA via `sklearn.decomposition.PCA`,
Clustering via `scipy.cluster.hierarchy`. Abhängigkeit: `scikit-learn` zu `pyproject.toml`.

### 5.6 Kategorie 5 — Cross-Study (deskriptiv)

| Komponente | Bibliothek | Endpunkt |
|---|---|---|
| `ForestPlot` | Plotly | cross-study |
| `CrossStudyBoxplot` | Plotly | cross-study |

**Kennzeichnung:** Alle Cross-Study-Charts tragen Hinweis:
*"Deskriptiver Vergleich — kein inferenzieller Test (verschiedene Stichproben)"*

### 5.7 Händigkeit-Filter

Globaler Filter auf Analyse-Seiten: Dropdown `Händigkeit: Alle | Rechtshänder | Linkshänder`.
Wird als `?handedness=...` an alle API-Calls weitergegeben.

### 5.8 UX-Funktionen

#### 5.8.1 Automatisch generierter Analyse-Report

Ein **"Report generieren"**-Button pro Studie erstellt ein vollständiges Analyse-Dokument
mit allen Charts und Statistik-Tabellen — für Dissertation und Präsentationen.

- Format: HTML (druckbar) und/oder PDF
- Inhalt: alle Chart-Kategorien (1–5) + Inferenz-Tabellen + Effektgrößen + Metadaten der Studie
- Backend: `Jinja2`-HTML-Template + `WeasyPrint` für PDF-Rendering
- Endpunkt: `GET /export/study/{study_id}/report?format=html|pdf`
- Charts werden server-seitig als Base64-PNG eingebettet (weißer Hintergrund, 300dpi)
- Dependency: `weasyprint` zu `pyproject.toml`

#### 5.8.2 Voraussetzungs-Transparenz

Unter jedem inferenziellen Chart: Info-Box die zeigt welcher Test verwendet wurde und warum.

Beispiel:
> *Shapiro-Wilk: Bedingung A p=0.23 ✓ · B p=0.04 ✗ → Friedman-Test · Post-hoc: Dunn (Bonferroni)*

Datenquelle: `test_used`, `normality`, `sphericity_p` aus dem Inferenz-Response (Abschnitt 3.6).
Einklappbar (default: zugeklappt), damit es erfahrene Nutzer nicht stört.

#### 5.8.3 Signifikanz-Highlighting in Tabellen

In allen Ergebnis-Tabellen (Post-hoc, Korrelationen, Effektgrößen):
- Signifikante p-Werte (p_adjusted < 0.05): grün hinterlegt
- Tendenziell signifikant (0.05 ≤ p < 0.10): gelb hinterlegt
- Effektgrößen mit Interpretation: `d=0.74` → `d=0.74 (groß)`
  (Schwellenwerte nach Cohen: klein <0.5, mittel <0.8, groß ≥0.8 für d;
  klein <0.06, mittel <0.14, groß ≥0.14 für η²p)

#### 5.8.4 Datenqualitäts-Indikator

Vor der Analyse: nicht-blockierende Warnung mit Überblick über Datenvollständigkeit.

Angezeigt als gelbes Banner (dismissbar), **blockiert die Analyse nicht**:

> ⚠️ *Studie HS1 · 18/20 Experimente abgeschlossen · Bedingung A: n=18, B: n=16 ·
> 3 Handovers ohne Timestamps · ET-Daten fehlen: 2 Handovers*

Endpunkt: `GET /analysis/study/{study_id}/quality-check`
Gibt zurück: n pro Bedingung, fehlende Timestamps, fehlende ET-Records, unfertige Trials.
UI-Warnung wird beim Laden der Analyse-Seite automatisch abgerufen.

#### 5.8.5 Bedingungsvergleich-Overlay

In Performance- und ET-Charts: **Overlay-Modus** per Checkbox im Chart-Header.
- Aus: Bedingungen nebeneinander (default)
- An: Bedingungen überlagert in einem Chart (verschiedene Farben/Linientypen)

Besonders nützlich für Boxplots (überlappende Verteilungen sichtbar) und
Phasen-Zeitverläufe (Linien überlagert).

#### 5.8.6 Cross-Study-Vergleichsseite

Dedizierte Seite `/analysis/cross-study` mit:
- Multi-Select-Dropdown: Studien aus der DB auswählen (nicht manuell IDs eingeben)
- Automatische Befüllung von Forest Plot und Side-by-side-Charts
- Optionale Baseline-Eingabe (default: 300ms, überschreibbar)
- Kennzeichnung "Deskriptiver Vergleich — kein inferenzieller Test" prominent sichtbar

### 5.9 Download & Export

Alle Daten und Visualisierungen müssen exportierbar sein — für SPSS-Import, Paper-Abbildungen
und Rohdaten-Verifikation.

**Daten-Export (Backend-Endpunkte):**

Neue Endpunkte unter `/api/export/`:

```
GET /export/study/{study_id}/raw?format=csv|xlsx
    → Rohdaten: Handovers, Eye-Tracking, Questionnaire-Responses als separate Sheets/Dateien

GET /export/study/{study_id}/analysis?format=csv|xlsx
    → Analyseergebnisse: deskriptive Statistiken, Inferenz-Tabellen, Effektgrößen,
      Post-hoc-Tabellen, Korrelationen — SPSS-importierbar formatiert

GET /export/experiment/{experiment_id}/raw?format=csv|xlsx
    → Rohdaten eines einzelnen Experiments
```

Format `csv`: eine Datei pro Datensatz-Typ (zip-Archiv bei mehreren Dateien).
Format `xlsx`: mehrere Sheets in einer Datei (Handovers, EyeTracking, Questionnaire, Stats).

**Python-Bibliothek:** `openpyxl` (für xlsx). CSV via Python-stdlib.
**Dependency:** `openpyxl` zu `pyproject.toml` hinzufügen.

**Daten-Konventionen für SPSS-Kompatibilität:**
- Spaltennamen: nur ASCII, keine Leerzeichen (Unterstriche statt Leerzeichen)
- Maximale Spaltenname-Länge: 64 Zeichen (SPSS-Limit)
- Encoding: UTF-8 mit BOM für Windows-Kompatibilität (`encoding='utf-8-sig'`)
- Zahlen: Punkt als Dezimaltrennzeichen (nicht Komma)
- Fehlende Werte: leere Zelle (kein `NaN`-String)
- Datetimes: ISO 8601 Format (`YYYY-MM-DD HH:MM:SS.fff`)

**Visualisierungs-Export (Frontend):**

Jede Chart-Komponente erhält einen **Download-Button** (Symbol: ↓) der Folgendes exportiert:

| Format | Verwendung | Technische Umsetzung |
|---|---|---|
| PNG (300 dpi) | Paper-Abbildungen, Präsentationen | Plotly `toImage({format:'png', scale:3})` |
| SVG | Vektorgrafik für Editoren (Inkscape, Illustrator) | Plotly `toImage({format:'svg'})` |
| CSV | Rohdaten der Grafik für Nachbearbeitung | Daten des Chart-Calls direkt |

**Weißer Hintergrund für Publikationen:**
Alle Chart-Komponenten unterstützen einen `exportMode`-Prop. Beim Download wird:
- Hintergrundfarbe auf `#ffffff` gesetzt (statt transparent/dunkel)
- Schriftfarbe auf `#000000`
- Gitternetzlinien: `#cccccc` (hellgrau, gut sichtbar auf weiß)
- Farbpalette: publikationsfähig (farbenblindheitssicher, druckbar in Graustufen)

Technisch: vor dem PNG-Export wird die Plotly-Figur temporär mit `paper_bgcolor='white'`
und `plot_bgcolor='white'` neu gerendert, ohne die angezeigte Version zu verändern.

Dateiname-Konvention: `{study_name}_{chart_type}_{datum}.{format}`
Beispiel: `HS1_performance_boxplot_2026-03-14.png`

---

## 6. Methodische Einschränkungen (in UI kommunizieren)

1. **Cross-Study-Vergleiche:** Immer als "deskriptiv, nicht inferenziell" gekennzeichnet
2. **Sakkaden:** Abgeleitet aus AOI-Wechseln — methodisch korrekt für AOI-basiertes ET
3. **PPI:** Nur sinnvoll wenn Geber-Aufgabenbereich im selben VR-Space sichtbar ist
4. **Kleine Stichproben:** Shapiro-Wilk n ≥ 4; RM-ANOVA stabil ab n ≥ 5 pro Bedingung; Friedman ab n ≥ 3. UI-Warnung bei n < 5.
5. **NASA-TLX:** Raw TLX ohne Gewichtung (kein Paarvergleich-Aufgabe durchgeführt)
6. **Timestamp-Synchronisation:** Phasenweise ET-Zuordnung setzt synchrone Uhren voraus (Unity + ET)

---

## 7. Abhängigkeiten (Python-Pakete)

Neue Pakete in `pyproject.toml` (`uv add pingouin scikit_posthocs scikit-learn openpyxl`):
```
pingouin        # RM-ANOVA, Post-hoc, Effektgrößen (η²p, Mauchly intern)
scikit_posthocs # Dunn-Test, Nemenyi-Test nach Friedman
scikit-learn    # PCA (exploratory_service), Clustering (scipy bereits vorhanden)
openpyxl        # Excel-Export (.xlsx) mit mehreren Sheets
```

Cliff's Delta: **manuelle Implementierung** in `effect_size_service.py` (kein zusätzliches Package).
Bereits vorhanden: `scipy`, `pandas`, `numpy`.

**Implementierungs-Hinweise (vom Reviewer):**
1. Beim Migrieren von `run_paired_test` nach `stats_utils.py`: Shapiro-Wilk-Guard von `n < 3` auf `n <= 3` korrigieren (= n > 3 erforderlich)
2. Bei `ω²p`-Formel: `MS_error = SS_error / ddof2` und `SS_total = SS_effect + SS_error` aus pingouin-Output ableiten (Spaltennamen je Version prüfen)
3. Alle drei Packages als **ersten Schritt** der Implementierung hinzufügen

---

## 8. Tests

Neue Tests in `Backend/tests/`:
- `test_inferential.py`: RM-ANOVA (k=2 und k≥3), Friedman, Post-hoc, GG-Korrektur
- `test_effect_sizes.py`: η²p, ω², Kendall's W, Cohen's d, Cliff's Delta
- `test_correlation.py`: Pearson/Spearman Auto-Selektion, Bonferroni-Korrektur
- `test_eye_tracking_extended.py`: Sakkaden, Transition Matrix, PPI, phasenweise Zuordnung
- `test_questionnaire_scoring.py`: NASA-TLX, SUS (Umkehrung), AttrakDiff2 (Subskalen), ISO-Metrics

Migrations-Tests: Alle bestehenden Tests (`test_analysis.py`, `test_experiment.py` etc.)
müssen nach dem Refactoring weiterhin grün sein.

---

## 9. Offene Punkte für Betreuer-Diskussion

Siehe `docs/study-design/offene-fragen-professor.md` für vollständige Liste.
Wichtigste Punkte:
1. Cross-Study-Vergleiche methodisch akzeptabel oder Mini-Replikation nötig?
2. Power-Analyse: Welche Effektgröße ist für den Kontext realistisch? (Richtwert: n≈28 für η²p=0.06)
3. Selektionskriterium für "besten" Stimulus in Vorstudien vorab festlegen (Pre-Registration)
4. Geber/Empfänger-Eye-Tracking: kombiniert oder getrennt auswerten?
5. Timestamp-Synchronisierung Unity ↔ Eye-Tracker: Wie wird Uhren-Drift überwacht?

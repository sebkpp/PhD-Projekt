# Unity — VR Handover Study

Multiplayer VR application for a surgical instrument handover study. Two players share a virtual workspace and hand over objects while multisensory feedback is applied based on the study condition.

**Stack:** Unity, C#, Photon Fusion 2 (Shared Mode), OpenXR

---

## Scene Setup Guide

Describes how to build a new study scene. The system is structured in four layers — each layer depends on the one below it. The order corresponds to the recommended setup sequence.

---

### Prerequisites — Project Assets (one-time setup)

These ScriptableObject assets must be present before a scene can run. They are already assigned in the relevant prefabs and do not need to be re-assigned per scene.

| Asset | Type | Purpose |
|---|---|---|
| `GrabSettings` | ScriptableObject | Physics tuning for grabbing and handover: grab/release/drop thresholds, spring constant, damping, fingertip radius. Shared by `PlayerAvatar`, interactable objects, and `Local_XR_Rig`. |
| `AvatarConfig` | ScriptableObject | Tracking offsets (position/rotation) per joint for calibrating hardware tracking to avatar bones. Different per avatar type. |
| `AvatarSet` | ScriptableObject | Holds references to male and female avatar mesh prefabs (`Medical_Male_prefab`, `Medical_Female_prefab`). `PlayerVisuals` uses this to select the correct mesh based on the gender string. |
| `StimulusDefinition` (×4) | ScriptableObject | One asset per visual stimulus. The filename must exactly match the backend stimulus name (loaded via `Resources.Load`). Located under `Assets/App/Resources/Stimuli/`. |

**StimulusDefinition assets:**

| Filename | Rendering Mode | Technique |
|---|---|---|
| `inner_hand` | IH | RenderingMode |
| `outer_hand` | OH | RenderingMode |
| `finger_color` | OH | ColorMapping |
| `object_color` | OH | ColorMapping |

---

### Layer 1 — Infrastructure

Provides network connection, experiment context, and hardware tracking. Must be initialized before all other layers.

---

#### Prefab: `NetworkManager`

```
NetworkManager
```

| Component | Origin | Purpose |
|---|---|---|
| `NetworkRunner` | Photon Fusion | Fusion runtime; manages network tick, clients, shared state |
| `ConnectionManager` | Project | Builds the Fusion Shared-Mode room; connects automatically on start |
| `PlayerManager` | Project | Spawns `PlayerAvatar` at `SpawnPoint_P1`/`SpawnPoint_P2` when a player joins; despawns on leave; calls `SetGender()` on the spawned avatar |

---

#### Prefab: `ExperimentContext`

```
ExperimentContext
```

| Component | Origin | Purpose |
|---|---|---|
| `ExperimentContext` | Project | Loads the next open experiment from the backend on start; provides experiment data to the rest of the system; fires `OnExperimentReady` when data is available |

**Backend data (`GET /experiments/next`):**

| Field | Exposed as | Used by |
|---|---|---|
| `trial_id` | `TrialId` property | `StimulusConfigLoader`, `HandoverReporter` |
| `experiment_id` | `ExperimentId` property | — |
| `slot → gender` | `GetGender(playerId)` | `PlayerManager` → avatar mesh selection |
| `slot → participant_id` | `GetParticipantId(playerId)` | `HandoverReporter` |
| `slot → stimuli[]` | via `OnExperimentReady` + `StimulusConfigLoader` | `HandoverFeedbackController` |

**Inspector:** Set the backend URL.

---

#### Prefab: `Local_XR_Rig`

```
Local_XR_Rig
├── Hand_Left   ← HardwareHand, GrabHand
├── Hand_Right  ← HardwareHand, GrabHand
└── Head        ← HardwareHeadset
```

**Root**

| Component | Origin | Purpose |
|---|---|---|
| `HardwareRig` | Project | Collects local XR tracking data (headset + hands) and exposes it as `RigState`; found and subscribed to by `NetworkRig` on spawn |

**Children: `Hand_Left` / `Hand_Right`**

| Component | Origin | Purpose |
|---|---|---|
| `HardwareHand` | Project | Reads position, rotation, and joint poses of the physical hand from the OpenXR system |
| `GrabHand` | Project | Detects fingertip contact with objects; computes `EffectiveGrip`; writes to `NetworkedGrabber` on the spawned avatar |

**Child: `Head`**

| Component | Origin | Purpose |
|---|---|---|
| `HardwareHeadset` | Project | Reads HMD position and rotation |

---

### Layer 2 — Player (`PlayerAvatar` prefab)

Spawned at runtime by `PlayerManager` — once per connected player.

```
PlayerAvatar  ← NetworkObject, NetworkTransform, NetworkRig,
               AvatarConfigReference, PlayerVisuals, AvatarDriver,
               HandRenderingController, HandVisualFeedback,
               AudioSource, ToneAuditoryFeedback, TactileFeedbackPlaceholder
├── Head       ← NetworkTransform, NetworkHeadset
├── Hand_Left  ← NetworkHand (Left)
├── Hand_Right ← NetworkHand (Right)
└── Visuals    ← empty; avatar mesh is spawned here at runtime by PlayerVisuals
```

**Root: `PlayerAvatar`**

| Component | Origin | Purpose |
|---|---|---|
| `NetworkObject` | Photon Fusion | Makes the GameObject a network object; assigns state authority (who may write the state) |
| `NetworkTransform` | Photon Fusion | Syncs root transform position and rotation across all clients |
| `AvatarConfigReference` | Project | Holds a reference to the `AvatarConfig` ScriptableObject; provides tracking offsets to `AvatarDriver` |
| `NetworkRig` | Project | On the local client, reads XR hardware data (`HardwareRig`) and writes it to the network components; read-only on remote clients |
| `PlayerVisuals` | Project | Spawns the correct avatar mesh (male/female) from `AvatarSet` under `Visuals` based on gender set via `SetGender()`; fires `AvatarInitialized` with `AvatarBoneReference` when the mesh is ready |
| `AvatarDriver` | Project | Drives avatar bones every frame from the synced `HandState`; runs on all clients for all players |
| `HandRenderingController` | Project | Overrides wrist bone position in `LateUpdate` for OH mode (Outer Hand — hand stays visually outside the object) |
| `HandVisualFeedback` | Project | Activates IH/OH rendering mode and color-mapping shader based on the active stimulus |
| `AudioSource` | Unity | Controlled by `ToneAuditoryFeedback` |
| `ToneAuditoryFeedback` | Project | Generates a procedural sine tone; volume scales with the local player's grip strength |
| `TactileFeedbackPlaceholder` | Project | No-op placeholder; replaceable with a hardware-specific haptic implementation later |

**Child: `Head`**

| Component | Origin | Purpose |
|---|---|---|
| `NetworkTransform` | Photon Fusion | Syncs head transform across all clients |
| `NetworkHeadset` | Project | Carrier component for the head transform in the network rig |

**Child: `Hand_Left` / `Hand_Right`**

| Component | Origin | Purpose |
|---|---|---|
| `NetworkHand` | Project | Syncs `HandState` (all joint positions + grip strength) of the respective hand over the network |

**Child: `Visuals`**

Empty in the prefab. `PlayerVisuals` spawns the avatar mesh here at runtime and registers `AvatarBoneReference`.

---

### Layer 3 — Interactable Objects

All graspable objects are based on `Block_Original` as the base prefab. Specific variants are derived as prefab variants — they only override mesh and collider shape.

```
[ObjectName]
├── Collider  ← BoxCollider (or appropriate collider shape)
└── Visuals   ← MeshFilter, MeshRenderer
```

**Root**

| Component | Origin | Purpose |
|---|---|---|
| `Rigidbody` | Unity | Physics body for grabbing and dropping |
| `NetworkObject` | Photon Fusion | Makes the object network-capable; state authority transfers to the grabbing player |
| `NetworkTransform` | Photon Fusion | Syncs position/rotation; uses the `Visuals` child as the interpolation target for smooth rendering without moving the physics collider |
| `Grabbable` | Project | Detects grabbing via hand tracking contact; prerequisite for `NetworkGrabbableObject` |
| `NetworkGrabbableObject` | Project | Dual-grip during handover, spring physics, authority transfer after full handover |
| `HandoverTracker` | Project | Detects the four handover phases (GiverGrabbed → ReceiverTouched → ReceiverGrabbed → GiverReleased) and broadcasts them via Fusion RPC to all clients; must be on the same GameObject as `NetworkGrabbableObject` |
| `HandoverReporter` | Project | Persists handover events to the backend; only the giver client sends HTTP |

**Child: `Collider`**

Contains the actual physics collider (BoxCollider, MeshCollider, etc.). Separated as a child so scale and shape can be adjusted independently from the root.

**Child: `Visuals`**

Contains MeshFilter + MeshRenderer. Used as `NetworkTransform` interpolation target — visually smooth movement even under network latency.

**Minimum requirement:** Without `HandoverTracker` and `HandoverReporter`, the object can be grabbed but no study events are triggered and nothing is recorded.

---

### Layer 4 — Feedback Manager (`FeedbackManager` prefab)

```
FeedbackManager  ← StimulusConfigLoader, HandoverFeedbackController
```

`HandoverFeedbackController` has `[RequireComponent(typeof(StimulusConfigLoader))]` — both components are always together. `HandoverFeedbackController` resolves `StimulusConfigLoader` and `ExperimentContext` via `GetComponent<>()`.

| Component | Origin | Purpose |
|---|---|---|
| `StimulusConfigLoader` | Project | Subscribes to `OnExperimentReady`; fetches all slot→stimulus configurations from the backend (`GET /trials/{id}/stimuli`); provides `GetStimuli(slot)` |
| `HandoverFeedbackController` | Project | Subscribes to `HandoverTracker` events; activates the correct `HandVisualFeedback` and `ToneAuditoryFeedback` on the relevant `PlayerAvatar` per phase; calls `UpdateGrip()` every frame on all active providers |

**Inspector:** Set the `ExperimentContext` reference on `StimulusConfigLoader`.

---

## Checklist: Building a New Scene

### Prerequisites
- [ ] `GrabSettings` asset present and assigned in prefabs
- [ ] `AvatarConfig` asset present and assigned in `PlayerAvatar`
- [ ] `AvatarSet` asset present with male/female prefab references and assigned in `PlayerAvatar`
- [ ] `StimulusDefinition` assets under `Assets/App/Resources/Stimuli/`: `inner_hand`, `outer_hand`, `finger_color`, `object_color`

### Layer 1 — Infrastructure
- [ ] Drag prefab `NetworkManager` into the scene
- [ ] Drag prefab `ExperimentContext` into the scene — set backend URL
- [ ] Drag prefab `Local_XR_Rig` into the scene

### Layer 2 — Player
- [ ] Assign prefab `PlayerAvatar` as spawn prefab in `PlayerManager`
- [ ] Place two empty GameObjects `SpawnPoint_P1` and `SpawnPoint_P2` and assign them in `PlayerManager`

### Layer 3 — Interactable Objects
- [ ] Place at least one interactable object (based on `Block_Original`) in the scene
- [ ] `HandoverReporter` — set `ExperimentContext` reference

### Layer 4 — Feedback
- [ ] Drag prefab `FeedbackManager` into the scene — set `ExperimentContext` reference on `StimulusConfigLoader`

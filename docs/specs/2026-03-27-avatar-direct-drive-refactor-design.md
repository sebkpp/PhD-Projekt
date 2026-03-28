# Avatar Direct-Drive Refactor – Design Spec

**Date:** 2026-03-27
**Branch:** `feature/avatar-direct-drive-refactor`
**Status:** Approved

---

## Context

The project requires two participants in VR to each embody an avatar (Microsoft Rocketbox) and hand over surgical instruments. The current avatar control system uses Unity's Animation Rigging package (runtime constraint setup) which is complex, fragile, and introduces unnecessary indirection for a setup where OpenXR optical hand tracking already provides precise per-joint rotations.

**Hardware:** Meta Quest 3 / Meta Quest Pro, optical hand tracking via OpenXR Hand Tracking System.

---

## Goal

Replace Animation Rigging with a custom direct-drive system that:
- Copies OpenXR joint rotations directly to avatar bones each `LateUpdate`
- Supports full finger tracking (all 5 fingers × 3 Rocketbox bones)
- Handles anatomically correct arm IK with elbow hint derived from wrist rotation
- Distributes forearm twist via a virtual twist bone (no FBX modification needed)
- Supports runtime avatar switching with automatic re-initialization
- Handles retargeting for avatars of different proportions
- Remains compatible with Photon Fusion multiplayer

---

## Rocketbox Avatar Bone Structure

All Rocketbox avatars use a 3ds Max Biped rig. Key findings from FBX inspection:

**Arm chain (no twist bones):**
```
Bip01 L UpperArm → Bip01 L Forearm → Bip01 L Hand
```

**Finger bones (3 per finger, same for all 5 fingers):**
```
Bip01 L Finger0   (Metacarpal / base)
Bip01 L Finger01  (Proximal phalanx)
Bip01 L Finger02  (Intermediate+Distal combined)
```

**OpenXR → Rocketbox finger mapping:**
| OpenXR XRHandJointID | Rocketbox Bone  |
|---|---|
| Metacarpal           | Finger0         |
| Proximal             | Finger01        |
| Intermediate         | Finger02        |
| Distal               | *(ignored)*     |

All avatar variants (Casual, Medical) share the same Biped rig, so one `AvatarConfig` asset covers all.

---

## Folder Structure

```
Assets/App/Scripts/Avatar/
├── Hardware/
│   ├── HardwareRig.cs          # Collects headset + both hands → XRInputState
│   ├── HardwareHand.cs         # Reads XRHandSubsystem (26 joints), replaces controller tracking
│   └── HardwareHeadset.cs      # Unchanged
│
├── Driver/
│   ├── AvatarDriver.cs         # Main LateUpdate bone driver (head, body, arms, fingers)
│   ├── AvatarBoneReference.cs  # Pure bone reference container, no IK setup
│   └── ArmIKSolver.cs          # Analytic 2-bone IK with elbow hint + forearm twist
│
├── Mapping/
│   ├── AvatarConfig.cs         # ScriptableObject: head/body/hand offsets (extended, existing)
│   └── AvatarRetargeting.cs    # One-time calibration for height and arm proportion
│
├── Visuals/
│   ├── PlayerVisuals.cs        # Refactored: runtime avatar swap + AvatarDriver re-init
│   ├── AvatarLookup.cs         # Unchanged
│   ├── Fader.cs                # Unchanged
│   └── Gender.cs               # Unchanged
│
└── Data/
    └── RigPart.cs              # Unchanged

Assets/App/Scripts/Avatar/Utils/           # remaining Utils (unchanged)
    ├── AvatarConfigReference.cs           # unchanged, stays here
    └── Axis.cs                            # unchanged, stays here
    # Note: AvatarConfig.cs moves FROM here TO Mapping/

Assets/App/Scripts/Editor/Avatar/         # Editor scripts
    └── Utils/AvatarConfigReferenceEditor.cs  # unchanged
    # New: HandCalibrationTool.cs (Editor-only, calculates bone offsets)

Assets/App/Config/
    └── AvatarConfig.asset                 # existing asset, extended with new fields
```

**Files to delete (dead code):**
- `IKTargetFollowVRRig.cs` — explicitly marked Deprecated
- `WalkingController.cs` — explicitly marked Deprecated
- `CustomHandVisualizer.cs` — almost entirely commented out, never integrated
- `AvatarSkeleton.cs` — Animation Rigging setup, replaced by AvatarBoneReference + AvatarDriver
- `AvatarFingerJointMap.cs`, `AvatarHandJointMap.cs`, `AvatarJointMap.cs` — replaced by AvatarDriver
- `Hand/HandTransformData.cs` — superseded by new data structures
- `boneUtilities.cs`, `RotationHelper.cs` — verify if still referenced before deleting

---

## Architecture & Data Flow

```
[OpenXR XRHandSubsystem]
        │ 26 joint poses (world space)
        ▼
[HardwareHand]  reads XRHandSubsystem each frame, stores full HandPose
        │
[HardwareRig]   collects headset + both hands → XRInputState
        │
[NetworkRig]    (Fusion) copies local state to network on each tick
        │ (local player: direct from HardwareRig)
        │ (remote players: from HandStateNetworked via Fusion)
        ▼
[AvatarDriver]  LateUpdate: reads state, applies to bones via AvatarBoneReference
        │
[Avatar Bones]  Bip01 bones driven directly
```

The same `AvatarDriver.Apply(XRInputState)` code path is used for both local and remote players. Remote players receive `HandStateNetworked` which is converted to `XRInputState` before being passed to the driver — one unified code path, no divergence.

---

## Component Responsibilities

### HardwareHand (refactored)

Reads `XRHandSubsystem` each frame. Exposes a `HandPose` struct containing world-space pose for each of the 26 `XRHandJointID` joints. Replaces the previous controller-based `HandTrackingData`.

### AvatarBoneReference

Pure data container — no MonoBehaviour setup logic, no constraint building. Holds direct `Transform` references to all relevant avatar bones, populated by name-lookup from the avatar's `HumanDescription` at initialization. Built as part of avatar instantiation.

### AvatarDriver

Single `LateUpdate` driver. On each frame:
1. **Body position:** `avatarRoot.position` follows head XZ position; Y adjusted by `AvatarRetargeting` calibration offset
2. **Body rotation:** avatar root yaws toward head forward direction (smoothed)
3. **Head:** direct world rotation copy from HMD → head bone with `AvatarConfig.Head` offset
4. **Arms:** `ArmIKSolver.Solve()` for each arm
5. **Fingers:** direct local rotation copy per joint with coordinate offset from `AvatarConfig`

### ArmIKSolver

Static utility class (not a MonoBehaviour). Called by `AvatarDriver`. Inputs: shoulder position, target wrist pose (from OpenXR), avatar bone lengths.

**Elbow hint (anatomically informed):**
```
palmNormal     = wristRotation * Vector3.up   // back-of-hand normal
shoulderToWrist = (wristPos - shoulderPos).normalized
elbowDirection  = Cross(shoulderToWrist, palmNormal).normalized
elbowHintPos    = midpoint(shoulder, wrist) + elbowDirection * hintDistance
```
When the palm faces down (pronation) the elbow moves backward/up; when palm faces up (supination) the elbow moves backward/down — matching natural anatomy.

**Forearm twist (virtual twist bone, no FBX modification):**

At avatar initialization, a virtual `ForearmTwist` GameObject is inserted between Forearm and Hand in the scene hierarchy:
```
Bip01 L Forearm
  └── ForearmTwist   (new, created at runtime)
        └── Bip01 L Hand  (re-parented)
```
SkinnedMeshRenderer skinning uses world-space bone matrices directly, so Hand-weighted vertices inherit ForearmTwist's rotation. The gradient through the wrist mesh arises naturally from the vertex weighting blend between Forearm and Hand.

Per frame:
- `Forearm.rotation` = swing component (pure direction change)
- `ForearmTwist.localRotation` = `Slerp(identity, twist, 0.5)` — half the twist
- `Hand.rotation` = full target rotation from OpenXR

**Out-of-reach clamping:** If the target wrist position exceeds the avatar's arm reach, the target is clamped to `(upperArmLength + forearmLength) * 0.98`. Prevents stretch artifacts.

### AvatarRetargeting

One-time calibration at avatar spawn. Computes a vertical offset:
```
verticalOffset = avatarEyeHeight - hmdHeight
avatarRoot.y  -= verticalOffset
```
Avatar feet stay grounded, avatar eyes align with HMD height. No horizontal retargeting needed because arm IK naturally handles different arm-length proportions: the avatar's IK solver uses the avatar's own bone lengths, so shorter/longer user arms are accommodated by different elbow angles.

### PlayerVisuals (refactored)

Orchestrates runtime avatar switching:
1. Fade-out via `Fader`
2. Destroy old avatar GameObject
3. Instantiate new avatar, build `AvatarBoneReference` from `HumanDescription`
4. Insert virtual `ForearmTwist` bones
5. Call `AvatarRetargeting.Calibrate()`
6. Call `AvatarDriver.Reinitialize(boneReference)`
7. Fade-in

---

## Coordinate System Mapping (OpenXR → Rocketbox Bones)

OpenXR delivers joint rotations in **world space**. Rocketbox Biped bones have their own local axis orientation. A per-joint rotation offset is needed.

**Foundation:** The existing `AvatarConfig` ScriptableObject with its `FingerOffsets` struct (containing `fingerForward: Axis`, `fingerUp: Axis` which compute `OffsetAxis`) is the right approach. The new system extends rather than replaces this.

**Per-frame application for each finger joint:**
```csharp
Quaternion openXRWorldRot = xrJoint.pose.rotation;
Quaternion boneOffset     = config.GetFingerOffset(finger, jointIndex);

bone.localRotation = Quaternion.Inverse(bone.parent.rotation)
                     * openXRWorldRot
                     * boneOffset;
```

**Calibration workflow (once per avatar rig type):**
1. Load avatar in Unity, verify T-pose
2. User holds T-pose (or defined reference hand pose)
3. Editor tool `HandCalibrationTool` (to be built) computes:
   `boneOffset = Quaternion.Inverse(openXRWorldRot) * bone.rotation`
4. Result is saved into `AvatarConfig.asset`
5. Fine-tune manually via Euler sliders in Inspector

Since all Rocketbox avatars share the same Biped rig, one `AvatarConfig` asset suffices for all variants.

---

## Network Layer Changes

The Photon Fusion network layer (`NetworkRig`, `NetworkHand`, `HandStateNetworked`) is structurally unchanged. One addition:

**`FingerStateNetworked` gains a Metacarpal joint:**
```csharp
public struct FingerStateNetworked : INetworkStruct
{
    public TransformStateNetworked Metacarpal;  // NEW
    public TransformStateNetworked Proximal;
    public TransformStateNetworked Intermediate;
    public TransformStateNetworked Distal;       // kept for potential future use
}
```

`HardwareHand` now populates Metacarpal from `XRHandJointID.ThumbMetacarpal` / `IndexMetacarpal` etc. `AvatarDriver` reads and applies it to `Bip01 L Finger0` / `Bip01 R Finger0`.

---

## AvatarConfig Extensions

The existing `AvatarConfig` ScriptableObject gains:
- `forearmTwistWeight: float` — fraction of twist applied to ForearmTwist bone (default: 0.5)
- `upperArmTwistWeight: float` — future use if upper arm twist is needed
- Metacarpal offset per finger (currently `FingerOffsets` has proximal/intermediate/distal; add `metacarpal: TrackingOffsets`)

The `AvatarConfigReference` MonoBehaviour and its Custom Inspector are unchanged.

---

## What is NOT in scope

- Leg animation / locomotion (stationary setup for surgical handover task)
- Facial animation
- IK for lower body
- Full body retargeting beyond height calibration

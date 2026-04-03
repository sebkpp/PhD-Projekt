# Mirror – URP VR Planar Reflection

Performant planar mirror reflections for Unity URP with full VR / Single-Pass Stereo support.

## Architecture

| File | Purpose |
|---|---|
| `Scripts/Mirror.cs` | Core component. Attach to the mirror plane. Manages render textures, portal camera, and reflection math. Rendering is triggered from `LateUpdate`. |
| `Scripts/MirrorRendererFeature.cs` | URP `ScriptableRendererFeature`. Enqueues the no-op `MirrorRenderPass` so that portal cameras tagged `PortalCam` are excluded from other renderer features. |
| `Scripts/MirrorRenderPass.cs` | No-op URP `ScriptableRenderPass`. Retained so `MirrorRendererFeature` can gate the pass on the `PortalCam` tag check. |
| `Shader/MirrorReflection.shader` | HLSL URP Unlit shader. Samples left/right reflection textures and selects the correct eye via `unity_StereoEyeIndex`. Supports optional Fresnel overlay. |
| `Materials/MirrorMaterial.mat` | Pre-configured material using `Mirror/MirrorReflection`. |
| `Prefab/Mirror.prefab` | Ready-to-use mirror prefab. |
| `TestScene.unity` | Test scene for verifying mirror setup. |

## Setup

### 1. Add the PortalCam tag

`Edit → Project Settings → Tags & Layers → Tags` → `+` → enter `PortalCam`

### 2. Add MirrorRendererFeature to the URP Renderer

1. Open your URP Renderer asset (e.g. `PC_Renderer`) in the Project window.
2. In the Inspector click `Add Renderer Feature`.
3. Select `Mirror Renderer Feature`.

### 3. Place the Mirror prefab

Drag `Prefab/Mirror.prefab` into the scene. The `Mirror` component is pre-configured with sensible defaults.

### 4. Verify the material shader

The material must use the `Mirror/MirrorReflection` shader (not the old ShaderGraph).  
Select `Materials/MirrorMaterial.mat` and confirm `Shader: Mirror/MirrorReflection` in the Inspector.  
The `Mirror Texture Left` and `Mirror Texture Right` slots are filled automatically at runtime by `Mirror.cs` — leave them empty.

## Inspector reference (Mirror component)

| Field | Description |
|---|---|
| `Projection Direction` | Mirror surface normal in local space. Default: `Vector3.forward`. |
| `Layer Mask` | Which layers are reflected. |
| `Texture Size` | Render texture resolution. |
| `Target Camera` | Camera used for reflection. Leave empty to use `Camera.main`. |
| `Clip Plane Offset` | Small offset to avoid z-fighting at the mirror surface. |
| `Near Clip Limit` | Minimum near clip plane for the portal camera. |
| `Disable Pixel Lights` | Disables pixel lights during reflection render for performance. |
| `Frames Needed To Update` | Skip N frames between reflection renders. |
| `Anti Aliasing` | MSAA samples for the reflection render texture (1/2/4/8). |
| `Texture Format` | `Default` (ARGB32), `RGB111110Float` (HDR), `RGB565` (16-bit, lower bandwidth). |

## Stereo / VR

When the main camera has `stereoEnabled = true`, `Mirror.cs` computes separate reflected view and projection matrices for each eye via `GetStereoViewMatrix` / `GetStereoProjectionMatrix` and issues two `SubmitRenderRequest` calls — one per eye, each rendering into its own `RenderTexture`. The shader selects the correct texture at runtime via `unity_StereoEyeIndex`.

Rendering is triggered from `LateUpdate` (after all camera transforms are finalised). This is required because `SubmitRenderRequest` starts a new URP pipeline iteration and cannot be called from within an active `ScriptableRenderPass`.

> **Note:** URP does not support `Camera.stereoTargetEye`, `SetStereoViewMatrix`, or `SetStereoProjectionMatrix` on arbitrary cameras. True GPU-level single-pass stereo instancing is therefore not available for the portal camera; two sequential mono renders per frame are used instead.

## Removing the old ShaderGraph

The original `MirrorReflection.shadergraph` is superseded by the HLSL shader. Delete it via the Unity Editor (`Assets/Packages/Mirror/Shader/MirrorReflection.shadergraph`). Do not delete it from the filesystem directly.

# IKG-Projektstudium - Entwicklung einer immersiven VR-Simulation zur Optimierung chirurgischer Abläufe

Dies ist das Repository für das Projektstudium **"Entwicklung einer immersiven VR-Simulation zur Optimierung chirurgischer Abläufe"** im Studiengang IKG.

Das Repository beinhaltet ein **Unity-Projekt** mit einer immersiven **Multiplayer-VR-Anwendung**. Die Anwendung simuliert ein chirurgisches Szenario, in dem zwei Spieler virtuelle Operationsinstrumente greifen können. Ziel ist es, Strategien für multisensorisches Feedback beim Greifen zu entwickeln, die die Übergabe der Operationsinstrumente unterstützen.

---
## Setup

### Benötigte Software
Zur Einrichtung und Entwicklung des Setups muss folgende Software installiert werden:

> **Hinweis:** Die Entwicklung wurde auf **Windows** durchgeführt. Einige Software-Komponenten, wie **Meta Quest Link**, sind nur für Windows verfügbar.

- **Unity**
  - Unity Hub: [Download](https://unity.com/unity-hub)
  - Unity Editor Version **6000.0.42f1** (inklusive **Android Build Support**): [Download](https://unity.com/releases/editor/archive)
- **IDE** (Wahlweise):
  - JetBrains Rider: [Download](https://www.jetbrains.com/rider/download/#section=windows)  
    oder
  - Visual Studio
- **Git** + **Git LFS**
- **Meta Quest Link**: [Download](https://www.meta.com/de-de/help/quest/1517439565442928/)
- **Meta Quest Developer Hub**: [Download](https://developers.meta.com/horizon/downloads/package/oculus-developer-hub-win/)

---

### Abhängigkeiten (Dependencies)

#### UPM-Packages (Unity Package Manager)
Diese Pakete wurden über den Unity Package Manager (UPM) installiert:

- **OpenXR** - Ermöglicht die Nutzung von OpenXR für plattformübergreifende VR-Entwicklung. [Dokumentation](https://docs.unity3d.com/Packages/com.unity.xr.openxr@1.14/manual/index.html)
- **XR Interaction Toolkit** - Bietet Interaktionssysteme für VR, z. B. Greifen von Objekten und UI-Interaktionen. [Dokumentation](https://docs.unity3d.com/Packages/com.unity.xr.interaction.toolkit@3.1/manual/index.html)
- **XR Hands** - Unterstützt Handtracking für natürliche Interaktionen in VR. [Dokumentation](https://docs.unity3d.com/Packages/com.unity.xr.hands@1.5/manual/index.html)
- **Animation Rigging** - Ermöglicht Animierung und inverse Kinematik (IK) für die Avatare. [Dokumentation](https://docs.unity3d.com/Packages/com.unity.animation.rigging@1.3/manual/index.html)
- **Khronos GLTF Unity Importer** - Ermöglicht das Laden und Verwenden von GLTF-3D-Modellen in Unity. [GitHub](https://github.com/KhronosGroup/UnityGLTF)
- **ParrelSync** - Erlaubt paralleles Testen von Multiplayer-Funktionen in Unity. [GitHub](https://github.com/VeriorPies/ParrelSync)

#### Plugins (Unity Asset Store / Externe Quellen)
Diese Plugins stammen aus dem Unity Asset Store oder externen Quellen:

- **Photon Fusion 2** - Netzwerkframework für Unity. [Dokumentation](https://doc.photonengine.com/fusion/current/fusion-intro)
- **Gleechi Virtual Grasp SDK** - Ermöglicht natürliches Greifen von Objekten mit physikalisch basierten Handinteraktionen. [Website](https://www.virtualgrasp.com)

#### 3D-Assets
Diese 3D-Modelle werden in der Anwendung verwendet:

- **Microsoft Rocketbox Avatare** - Enthält 3D-Avatarmodelle. [GitHub](https://github.com/microsoft/Microsoft-Rocketbox)
- **Operationsraum 3D-Modell** - Verwendetes 3D-Modell eines Operationsraums. [Sketchfab](https://sketchfab.com/3d-models/operating-room-4248fba251a5482ca501d23919c5b8c6)

---

## Installation

**Repository klonen:**

```sh
# HTTPS
https://gitlab.rz.htw-berlin.de/s0583646/projekt_ws24.git

# SSH
git@gitlab.rz.htw-berlin.de:s0583646/projekt_ws24.git
```

**Projekt in Unity öffnen:**

1. Das geklonte Repository im Unity Hub öffnen.
2. Das erstmalige Laden des Projekts kann einige Zeit in Anspruch nehmen.
3. Beim Öffnen erscheinen mehrere Popups, die das Projekt auf die neue **OpenXR-Version** umstellen. Diese mit **"Ja"** bestätigen.
4. Nach dem Laden des Projekts erscheint ein **Setup-Fenster für Photon Fusion**.
  - Stelle sicher, dass die **App-ID** korrekt eingetragen ist: `5c77e000-f752-43ad-996a-25c8149edcf6`

**Hauptszene:**

Die Hauptszene befindet sich unter:

```
Application/Scenes/operational room.unity
```

---

## Projektstruktur

Die Ordnerstruktur des Unity-Projekts ist wie folgt aufgebaut:

```
- Assets
  - Application (Alle Komponenten der Anwendung - Hier finden die wesentlichen Entwicklungen statt)
    - Models (3D-Modelle)
    - Prefabs (Verwendete Prefabs)
    - Scenes (3D-Szenen)
    - Scripts (Eigene Skripte)
  - com.gleechi.unity.virtualgrasp (Plugin für Objektgriff)
  - Photon (Multiplayer-Framework)
  - Plugins (Diverse Plugins)
  - Resources (Diverse Plugin-Einstellungen)
  - Samples (Beispieldateien aus Plugins)
  - Settings (Rendering-Einstellungen)
  - TextMesh Pro (UI-Komponenten)
  - VG_Grasps (Mesh-Bibliotheken für das Greifen)
  - XR (XR-Setup und Loader)
  - XRI (XR-Interaktionen)
- Packages (Enthält die `manifest.json`, welche alle Plugins referenziert, die über UPM hinzugefügt wurden)
- ProjectSettings (Projekt-Einstellungen, nur im Unity-Editor bearbeiten)
```

---

## Deployment auf Meta Quest

**To-Do** *(Hier sollen in Zukunft Anweisungen zum Erstellen und Bereitstellen der Anwendung auf Meta Quest hinzugefügt werden.)*

---

## Troubleshooting

to-be-added

---

## Weitere Ressourcen

**Link zur Präsentation:** [Google Slides](https://docs.google.com/presentation/d/18H9MO7WaeibtrPGkoeIOe2Euw6h_182z3YXetdKaGrA/edit#slide=id.g2af481c8749_0_33)

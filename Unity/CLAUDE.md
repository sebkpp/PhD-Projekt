# Unity – projekt_ws24

## Stack
- Engine: Unity (C#)
- IDE: JetBrains Rider

## Wichtige Ordner
- `Assets/`         – Spielinhalte, Scripts, Prefabs, Scenes
- `Packages/`       – Unity Package Manager Dependencies
- `ProjectSettings/` – Unity Projekteinstellungen

## Coding Conventions (C#)
- PascalCase für Klassen, Methoden und Properties
- camelCase für private Felder (Prefix `_` für private: `_myField`)
- `[SerializeField]` statt public Felder wo möglich
- Keine Logik in `Update()` die in `Start()` oder Events gehört

## Build
- Build über Unity Editor oder Unity CLI (`-batchmode`)
- Buildausgabe landet in `Unity/Build/` (nicht committen)

## Kritische Hinweise
- NIEMALS Dateien in `Library/`, `Temp/`, `obj/` anfassen
- `.meta` Dateien immer zusammen mit ihrem Asset committen
- Assets umbenennen nur über den Unity Editor, nie direkt im Filesystem

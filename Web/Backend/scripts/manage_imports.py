import import_stimuli
import import_avatar_visibility
import import_aoi

def main():
    print("Importiere Stimuli...")
    import_stimuli.main()

    print("Importiere Avatar-Sichtbarkeiten...")
    import_avatar_visibility.main()

    print("Importiere Area of Interests...")
    import_aoi.main()

    print("✅ Alle Importe erfolgreich abgeschlossen.")

if __name__ == '__main__':
    main()

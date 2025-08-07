def validate_experiment_data(data):
    errors = []

    name = data.get("name", "").strip()
    if not name:
        errors.append("name ist erforderlich.")

    if len(name) > 100:
        errors.append("name darf nicht länger als 100 Zeichen sein.")

    # Optional:more Validierungen for description, researcher, etc.

    return errors
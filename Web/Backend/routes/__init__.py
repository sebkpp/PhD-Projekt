from fastapi import FastAPI

def register_routes(app: FastAPI):
    from Backend.routes import (
        participant,
        study,
        experiment,
        trials,
        stimuli,
        questionnaire,
        analysis,
        handover_routes,
        avatar_visibility,
    )

    modules = (
        participant,
        study,
        experiment,
        trials,
        stimuli,
        questionnaire,
        analysis,
        handover_routes,
        avatar_visibility,
    )

    for mod in modules:
        if hasattr(mod, "router"):
            app.include_router(mod.router)

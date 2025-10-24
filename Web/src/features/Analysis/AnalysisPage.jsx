import React from "react";
import Breadcrumbs from "@/components/Breadcrumbs.jsx";

export default function AnalysisPage() {

    const breadcrumbItems = [
        { label: "Studienübersicht", to: "/" },
        { label: "Studien-Meta-Analyse"},
    ];

    return (
        <div className="p-6 relative bg-gray-900 min-h-screen text-gray-100">
            <Breadcrumbs items={breadcrumbItems} styled={true} className="mb-6" />
            <h1>Experiment-Analyse</h1>
            <p>Hier werden die Analyse-Daten des ausgewählten Experiments angezeigt.</p>
            {/* Platz für Diagramme, Tabellen, etc. */}
        </div>
    );
}
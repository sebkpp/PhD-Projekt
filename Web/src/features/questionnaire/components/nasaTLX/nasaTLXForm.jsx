import React from 'react';

export default function NasaTLXForm({ values= {}, questions, onChange, validationError }) {
    return (
        <div className="space-y-8">
            {questions.map((dim) => {
                const isPerformance = dim.key === 'performance';
                const labelStart = isPerformance ? 'Gut' : 'Niedrig';
                const labelEnd = isPerformance ? 'Schlecht' : 'Hoch';

                return (
                    <div key={dim.key}>
                        {/* Titel + Beschreibung */}
                        <div className="flex items-start justify-between mb-1 gap-4">
                            <label className="font-semibold">{dim.name}</label>
                            <p className="text-sm text-gray-400 text-right">{dim.description}</p>
                        </div>

                        {/* Skala */}
                        <div className="flex items-center gap-4">
                            <div className="relative w-full h-6">
                                {/* Hintergrund */}
                                <div className="absolute top-0 left-0 w-full h-6 bg-gray-700 rounded pointer-events-none" />

                                {/* Hilfslinien */}
                                {[...Array(21)].map((_, i) => (
                                    <div
                                        key={i}
                                        className={`absolute top-0 h-6 ${
                                            i === 10 ? 'w-[2px] bg-gray-300' : 'w-[1px] bg-gray-400 opacity-70'
                                        } pointer-events-none`}
                                        style={{
                                            left: `${i * 5}%`,
                                            transform: 'translateX(-0.5px)',
                                        }}
                                    />
                                ))}

                                {/* Marker */}
                                {values[dim.key] !== undefined && (
                                    <div
                                        className="absolute top-0 h-6 w-[2px] bg-accent pointer-events-none"
                                        style={{
                                            left: `${values[dim.key]}%`,
                                            transform: 'translateX(-1px)',
                                        }}
                                    />
                                )}

                                {/* Klickfläche */}
                                <div
                                    className="absolute top-0 left-0 w-full h-6 cursor-pointer"
                                    onClick={(e) => {
                                        const { left, width } = e.target.getBoundingClientRect();
                                        const clickX = e.clientX - left;
                                        const value = Math.round((clickX / width) * 100);
                                        onChange(dim.key, value);
                                    }}
                                />
                            </div>
                        </div>

                        {/* Beschriftung */}
                        <div className="flex justify-between text-sm text-gray-400 mt-1">
                            <span>{labelStart}</span>
                            <span>{labelEnd}</span>
                        </div>
                    </div>
                );
            })}

            {validationError && (
                <p className="text-sm text-red-400 mt-3">
                    ⚠️ Bitte füllen Sie alle Skalen aus, bevor Sie fortfahren.
                </p>
            )}
        </div>
    );
}

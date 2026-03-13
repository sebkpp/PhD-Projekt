import { useEffect } from 'react'

/**
 * Generischer Fragebogen-Renderer.
 * Rendert Slider-, Likert- oder Bipolar-Widgets basierend auf questionnaire.scale_type.
 */
export default function DynamicQuestionnaireForm({ questionnaire, onChange, responses, onValidationChange }) {
    const items = questionnaire?.items ?? []
    const scaleType = questionnaire?.scale_type ?? 'slider'
    const scaleMin = questionnaire?.scale_min ?? 0
    const scaleMax = questionnaire?.scale_max ?? 100

    useEffect(() => {
        const isValid = items.every(item => {
            const val = responses[item.item_name]
            return val !== undefined && val !== null && val !== '' && !Number.isNaN(val)
        })
        onValidationChange(isValid)
    }, [responses, items, onValidationChange])

    if (items.length === 0) {
        return <p className="text-gray-400">Keine Items für diesen Fragebogen vorhanden.</p>
    }

    return (
        <div className="space-y-8">
            <h2 className="text-xl font-bold text-white">{questionnaire.name}</h2>
            {scaleType === 'bipolar'
                ? <BipolarRenderer items={items} scaleMin={scaleMin} scaleMax={scaleMax} responses={responses} onChange={onChange} />
                : scaleType === 'likert'
                    ? <LikertRenderer items={items} scaleMin={scaleMin} scaleMax={scaleMax} responses={responses} onChange={onChange} />
                    : <SliderRenderer items={items} scaleMin={scaleMin} scaleMax={scaleMax} responses={responses} onChange={onChange} />
            }
        </div>
    )
}

function RadioButton({ name, value, checked, onChange }) {
    return (
        <label className="cursor-pointer flex items-center justify-center">
            <input type="radio" name={name} value={value} checked={checked} onChange={onChange} className="sr-only peer" />
            <div className="w-5 h-5 rounded-full border-2 border-gray-500 peer-checked:border-blue-400 peer-checked:bg-blue-400 transition-colors" />
        </label>
    )
}

function SliderRenderer({ items, scaleMin, scaleMax, responses, onChange }) {
    return (
        <div className="space-y-8">
            {items.map(item => {
                const value = responses[item.item_name]
                const percent = value !== undefined
                    ? ((value - scaleMin) / (scaleMax - scaleMin)) * 100
                    : undefined

                return (
                    <div key={item.item_name} className="space-y-3">
                        <p className="font-semibold text-white">{item.item_label ?? item.item_name}</p>
                        <div className="relative w-full h-6">
                            <div className="absolute top-0 left-0 w-full h-6 bg-gray-700 rounded pointer-events-none" />
                            {[...Array(21)].map((_, i) => (
                                <div
                                    key={i}
                                    className={`absolute top-0 h-6 ${i === 10 ? 'w-[2px] bg-gray-300' : 'w-[1px] bg-gray-400 opacity-70'} pointer-events-none`}
                                    style={{ left: `${i * 5}%`, transform: 'translateX(-0.5px)' }}
                                />
                            ))}
                            {percent !== undefined && (
                                <div
                                    className="absolute top-0 h-6 w-[2px] bg-accent pointer-events-none"
                                    style={{ left: `${percent}%`, transform: 'translateX(-1px)' }}
                                />
                            )}
                            <div
                                className="absolute top-0 left-0 w-full h-6 cursor-pointer"
                                onClick={(e) => {
                                    const { left, width } = e.target.getBoundingClientRect()
                                    const clickX = e.clientX - left
                                    const raw = (clickX / width) * (scaleMax - scaleMin) + scaleMin
                                    onChange(item.item_name, Math.round(raw))
                                }}
                            />
                        </div>
                        <div className="flex justify-between text-sm text-gray-400">
                            <span>{item.min_label ?? scaleMin}</span>
                            <span>{item.max_label ?? scaleMax}</span>
                        </div>
                    </div>
                )
            })}
        </div>
    )
}

function LikertRenderer({ items, scaleMin, scaleMax, responses, onChange }) {
    const steps = []
    for (let v = scaleMin; v <= scaleMax; v++) steps.push(v)

    return (
        <div className="space-y-6">
            {items.map(item => (
                <div key={item.item_name} className="rounded-lg bg-gray-800/50 px-5 py-4 space-y-4">
                    <p className="text-white leading-snug">{item.item_label ?? item.item_name}</p>
                    <div className="flex items-center gap-4">
                        {item.min_label && (
                            <span className="text-sm text-gray-400 shrink-0 w-44 text-right">{item.min_label}</span>
                        )}
                        <div className="flex flex-1 justify-evenly">
                            {steps.map(val => (
                                <RadioButton
                                    key={val}
                                    name={item.item_name}
                                    value={val}
                                    checked={responses[item.item_name] === val}
                                    onChange={() => onChange(item.item_name, val)}
                                />
                            ))}
                        </div>
                        {item.max_label && (
                            <span className="text-sm text-gray-400 shrink-0 w-44">{item.max_label}</span>
                        )}
                    </div>
                </div>
            ))}
        </div>
    )
}

/* Semantisches Differential (z.B. AttrakDiff):
   min_label  ○ ○ ○ ○ ○ ○ ○  max_label – volle Breite, gleichmäßig verteilt */
function BipolarRenderer({ items, scaleMin, scaleMax, responses, onChange }) {
    const steps = []
    for (let v = scaleMin; v <= scaleMax; v++) steps.push(v)

    return (
        <div className="rounded-lg bg-gray-800/50 overflow-hidden">
            {items.map((item, idx) => (
                <div
                    key={item.item_name}
                    className={`flex items-center gap-4 px-6 py-3 ${idx % 2 === 0 ? '' : 'bg-gray-800/50'}`}
                >
                    <span className="text-sm text-gray-300 text-right w-44 shrink-0">{item.min_label ?? ''}</span>
                    <div className="flex flex-1 justify-evenly">
                        {steps.map(val => (
                            <RadioButton
                                key={val}
                                name={item.item_name}
                                value={val}
                                checked={responses[item.item_name] === val}
                                onChange={() => onChange(item.item_name, val)}
                            />
                        ))}
                    </div>
                    <span className="text-sm text-gray-300 w-44 shrink-0">{item.max_label ?? ''}</span>
                </div>
            ))}
        </div>
    )
}

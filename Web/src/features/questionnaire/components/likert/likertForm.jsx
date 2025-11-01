export default function LikertForm({
                                       questions,
                                       values,
                                       validationError,
                                       submitting,
                                       onChange,
                                   }) {
    return (
        <div className="space-y-6">
            {questions.map(q => (
                <div key={q.key}>
                    <p className="font-semibold mb-2">{q.question}</p>
                    <div className="flex gap-6">
                        {[1, 2, 3, 4, 5].map(val => (
                            <label key={val} className="flex flex-col items-center cursor-pointer">
                                <input
                                    type="radio"
                                    name={q.key}
                                    value={val}
                                    checked={values[q.key] === val}
                                    onChange={() => onChange(q.key, val)}
                                    className="mb-1"
                                />
                                <span className="text-xs text-gray-500">
                                    {val === 1
                                        ? 'Stimme nicht zu'
                                        : val === 3
                                            ? 'Neutral'
                                            : val === 5
                                                ? 'Stimme voll zu'
                                                : ''}
                                </span>
                            </label>
                        ))}
                    </div>
                </div>
            ))}

            {validationError && (
                <p className="text-sm text-red-400 mt-3">
                    ⚠️ Bitte beantworten Sie alle Fragen.
                </p>
            )}
        </div>
    )
}

import LikertForm from './likertForm.jsx';
import {useEffect} from 'react';

const likertQuestions = [
    { key: 'q1', question: 'Ich finde die Aufgabe interessant.' },
    { key: 'q2', question: 'Die Schwierigkeit war angemessen.' },
    { key: 'q3', question: 'Ich konnte mich gut konzentrieren.' }
];

export default function Likert({questionnaire, onChange, responses, submitting, error, onValidationChange}) {
    // Validierung bei jeder Änderung der responses
    useEffect(() => {
        const isValid = likertQuestions.every(q =>
            responses[q.key] !== undefined &&
            responses[q.key] !== null &&
            responses[q.key] !== ''
        );
        onValidationChange(isValid);
    }, [responses, onValidationChange]);

    return (
        <LikertForm
            questions={likertQuestions}
            values={responses}
            onChange={onChange}
            submitting={submitting}
            validationError={error}
        />
    )
}

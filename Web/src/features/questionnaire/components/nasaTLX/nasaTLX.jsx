import NasaTLXForm from './nasaTLXForm.jsx'
import {useEffect} from "react";

export default function NasaTLX({questionnaire, onChange, responses, onValidationChange}) {
    const dimensions = [
        {
            key: 'mental',
            name: 'Geistige Anforderung',
            description: 'Wie viel geistige Anstrengung war bei der Informationsaufnahme und -verarbeitung erforderlich?'
        },
        {
            key: 'physical',
            name: 'Körperliche Anforderungen',
            description: 'Wie viel körperliche Aktivität war erforderlich?'
        },
        {
            key: 'temporal',
            name: 'Zeitliche Anforderung',
            description: 'Wieviel Zeitdruck empfanden Sie hinsichtlich der Häufigkeit oder dem Takt?'
        },
        {
            key: 'performance',
            name: 'Leistung',
            description: 'Wie gut haben Sie die Aufgabe Ihrer Meinung nach erledigt?'
        },
        {
            key: 'effort',
            name: 'Anstrengung',
            description: 'Wie viel Mühe mussten Sie investieren, um das Ziel zu erreichen?'
        },
        {
            key: 'frustration',
            name: 'Frustration',
            description: 'Wie genervt, gestresst oder unsicher haben Sie sich gefühlt?'
        }
    ];

    // Validierung bei jeder Änderung der responses
    useEffect(() => {
        const isValid = dimensions.every(dim =>
            typeof responses[dim.key] === 'number' &&
            !isNaN(responses[dim.key])
        );
        onValidationChange(isValid);
    }, [responses, onValidationChange]);


    return (
        <NasaTLXForm
            questions={dimensions}
            values={responses}
            onChange={onChange}
        />
    );
}

import {useState} from "react";

export function useQuestionnaireValidation(type, responses, questions) {
    const [isValid, setIsValid] = useState(false);

    useEffect(() => {
        switch(type) {
            case 'NASA-TLX':
                setIsValid(validateNasaTLX(responses, questions));
                break;
            case 'LIKERT':
                setIsValid(validateLikert(responses, questions));
                break;
            default:
                setIsValid(false);
        }
    }, [type, responses, questions]);

    return isValid;
}

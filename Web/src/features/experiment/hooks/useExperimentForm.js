import {useEffect, useState} from 'react'

export function useExperimentForm(studyGeneralInfo) {

    const [description, setDescription] = useState(studyGeneralInfo?.description || "")
    const [researcher, setResearcher] = useState(studyGeneralInfo?.principalInvestigator || "")
    const [prevInfo, setPrevInfo] = useState(studyGeneralInfo);

    const [error, setError] = useState(null)

    useEffect(() => {
        // Nur aktualisieren, wenn sich die Werte wirklich ändern
        if (
            studyGeneralInfo &&
            (
                studyGeneralInfo.description !== prevInfo?.description ||
                studyGeneralInfo.principalInvestigator !== prevInfo?.principalInvestigator
            )
        ) {
            setDescription(studyGeneralInfo.description || "");
            setResearcher(studyGeneralInfo.principalInvestigator || "");
            setPrevInfo(studyGeneralInfo);
        }
    }, [studyGeneralInfo, prevInfo]);

    return {
        description, setDescription,
        researcher, setResearcher,
        error,
    }
}

import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import DynamicQuestionnaireForm from './components/dynamic/DynamicQuestionnaireForm.jsx'
import { fetchQuestionnaireById } from './service/questionnaireFlowService.js'

export default function QuestionnairePreviewPage() {
    const { questionnaireId } = useParams()
    const [questionnaire, setQuestionnaire] = useState(null)
    const [responses, setResponses] = useState({})
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    useEffect(() => {
        fetchQuestionnaireById(questionnaireId)
            .then(setQuestionnaire)
            .catch(err => setError(err.message))
            .finally(() => setLoading(false))
    }, [questionnaireId])

    const handleChange = (itemName, value) => {
        setResponses(prev => ({ ...prev, [itemName]: value }))
    }

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-900 flex items-center justify-center">
                <p className="text-gray-400">Lade Fragebogen...</p>
            </div>
        )
    }

    if (error) {
        return (
            <div className="min-h-screen bg-gray-900 flex items-center justify-center">
                <p className="text-red-400">{error}</p>
            </div>
        )
    }

    return (
        <div className="min-h-screen bg-gray-900 text-white p-8">
            <div className="max-w-4xl mx-auto">
                <div className="mb-6 px-4 py-3 rounded border border-yellow-500 bg-yellow-900/30 text-yellow-300 text-sm">
                    Vorschau-Modus – keine Daten werden gespeichert
                </div>
                <DynamicQuestionnaireForm
                    questionnaire={questionnaire}
                    responses={responses}
                    onChange={handleChange}
                    onValidationChange={() => {}}
                />
            </div>
        </div>
    )
}

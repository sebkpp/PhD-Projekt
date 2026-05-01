import { generateQuestionnaireStartUrl } from '../../services/particpantQuestionnaireQRCodeService.js'

export function useQuestionnaireStartQrUrl(experimentId, slot, participantId, trial_id) {

    if (!experimentId || !slot || !participantId || !trial_id) {
        return ''
    }
    return generateQuestionnaireStartUrl(experimentId, slot, participantId, trial_id)
}

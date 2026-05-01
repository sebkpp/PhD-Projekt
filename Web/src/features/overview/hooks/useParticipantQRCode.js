import { generateParticipantUrl } from '../services/participantQRCodeService.js'

export function useParticipantQrUrl(study_id, experimentId, participant_id, trial_id, slot, status) {
    return generateParticipantUrl(study_id, experimentId, participant_id, trial_id, slot, status)
}

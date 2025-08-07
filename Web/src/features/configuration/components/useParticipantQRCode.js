import { generateParticipantUrl } from './participantQRCodeService'

export function useParticipantQrUrl(experimentId, slot) {
    return generateParticipantUrl(experimentId, slot)
}

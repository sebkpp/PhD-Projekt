import { EyeIcon, SpeakerWaveIcon, HandRaisedIcon } from '@heroicons/react/24/outline'

export const stimuliIdToShortcode = {
    1: "vis",
    2: "aud",
    3: "tak"
};

export const shortcodeToStimuliId = {
    vis: 1,
    aud: 2,
    tak: 3
};

export default function StimulusIcon({ type, className = "" }) {
    switch (type) {
        case 'visual':
            return <EyeIcon className={`w-4 h-4 text-blue-500 ${className}`} />
        case 'auditory':
            return <SpeakerWaveIcon className={`w-4 h-4 text-green-500 ${className}`} />
        case 'tactile':
            return <HandRaisedIcon className={`w-4 h-4 text-yellow-500 ${className}`} />
        default:
            return null
    }
}
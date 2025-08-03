import { QRCodeSVG } from 'qrcode.react'
import { useRef } from 'react'

export default function QuestionnaireQRCode({ experimentId, slot }) {
    const url = `${window.location.origin}/participant/start?experiment=${experimentId}&slot=${slot}`
    const textRef = useRef(null)

    const handleUrlClick = () => {
        if (textRef.current) {
            textRef.current.select()
        }
    }

    return (
        <div className="text-center p-4 border border-border rounded-xl bg-gray-800 w-full max-w-[360px]">
            <h3 className="text-lg font-semibold mb-2">Participant Slot {slot}</h3>

            {/* QR-Code zentriert */}
            <div className="flex justify-center mb-2">
                <QRCodeSVG value={url} size={160} bgColor="#ffffff" fgColor="#000000" />
            </div>

            {/* URL mit Copy-Fokus */}
            <textarea
                ref={textRef}
                onClick={handleUrlClick}
                readOnly
                rows={2}
                value={url}
                className="w-full resize-none text-xs text-gray-400 text-center bg-transparent cursor-pointer outline-none break-words"
            />
        </div>
    )
}

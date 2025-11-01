import { QRCodeSVG } from 'qrcode.react'
import { useRef } from 'react'

export default function QRCodeCard({ url, slot, participant_id }) {
    const textRef = useRef(null)

    const handleUrlClick = () => {
        if (textRef.current) {
            textRef.current.select()
        }
    }

    return (
        <div className="text-center p-4 border border-border rounded-xl bg-gray-800 w-full max-w-[360px]">
            <h3 className="text-lg font-semibold mb-2">Probanden Slot {slot}
                {participant_id && (
                    <span className="text-sm text-gray-400 ml-2">
                        (Probanden ID: {participant_id})
                    </span>
                )}
            </h3>
            <div className="flex justify-center mb-2">
                <QRCodeSVG value={url} size={160} bgColor="#ffffff" fgColor="#000000" />
            </div>
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

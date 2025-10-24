export default function ConfirmDialog({ open, title, message, onConfirm, onCancel }) {
    if (!open) return null;

    return (
        <div className="fixed inset-0 backdrop-blur-sm flex items-center justify-center z-50"
             style={{ backgroundColor: 'rgba(0, 0, 0, 0.5)' }}>
            <div className="bg-gray-800 p-8 rounded-lg shadow-lg max-w-md">
                <h3 className="text-lg font-bold mb-4">{title}</h3>
                <p className="mb-6 text-gray-300">{message}</p>
                <div className="flex gap-4 justify-end">
                    <button
                        className="px-4 py-2 bg-gray-600 rounded hover:bg-gray-500"
                        onClick={onCancel}
                    >
                        Abbrechen
                    </button>
                    <button
                        className="px-4 py-2 bg-blue-600 rounded hover:bg-blue-500"
                        onClick={onConfirm}
                    >
                        Ja, abschließen
                    </button>
                </div>
            </div>
        </div>
    );
}
export default function DeleteConfirmModal({ open, onConfirm, onCancel }) {
    if (!open) return null;
    return (
        <div className="fixed inset-0 flex items-center justify-center z-50 backdrop-blur-sm"
             style={{ backgroundColor: 'rgba(0, 0, 0, 0.5)' }}>
            <div className="bg-white dark:bg-gray-900 rounded-lg shadow-lg p-8 max-w-md w-full">
                <h3 className="text-xl font-bold mb-4 text-gray-900 dark:text-gray-100">Studie löschen?</h3>
                <p className="mb-6 text-gray-700 dark:text-gray-300">
                    Möchtest du diese Studie wirklich löschen? Dieser Vorgang kann nicht rückgängig gemacht werden.
                </p>
                <div className="flex gap-4 justify-end">
                    <button
                        className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded hover:bg-gray-300 dark:hover:bg-gray-600"
                        onClick={onCancel}
                    >
                        Abbrechen
                    </button>
                    <button
                        className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
                        onClick={onConfirm}
                    >
                        Ja, löschen
                    </button>
                </div>
            </div>
        </div>
    );
}
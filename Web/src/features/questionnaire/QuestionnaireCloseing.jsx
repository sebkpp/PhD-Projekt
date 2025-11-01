import React from 'react';

export default function QuestionnaireClosing() {
    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 dark:bg-gray-900 px-4">
            <div className="bg-white dark:bg-gray-800 p-8 rounded-2xl shadow-md max-w-md text-center">
                <h1 className="text-3xl font-semibold text-gray-800 dark:text-white mb-4">
                    Vielen Dank!
                </h1>
                <p className="text-gray-600 dark:text-gray-300 text-lg mb-6">
                    Deine Antworten wurden erfolgreich gespeichert.
                </p>
                <p className="text-gray-500 dark:text-gray-400 text-sm">
                    Du kannst das Fenster jetzt schließen oder auf weitere Anweisungen warten.
                </p>
            </div>
        </div>
    );
}

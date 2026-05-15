import { useTranslation } from 'react-i18next'

const LANGUAGES = ['de', 'en']

export default function LanguageSwitcher() {
    const { i18n } = useTranslation()
    const active = i18n.language

    const change = (lang) => {
        i18n.changeLanguage(lang)
        localStorage.setItem('lang', lang)
    }

    return (
        <div className="flex items-center gap-0.5 bg-gray-700/60 border border-gray-600 rounded-md p-0.5">
            {LANGUAGES.map((lang) => {
                const isActive = active === lang
                return (
                    <button
                        key={lang}
                        onClick={() => change(lang)}
                        className={`px-2.5 py-1 rounded text-xs font-semibold uppercase tracking-wide transition-colors ${
                            isActive
                                ? 'bg-white text-gray-900'
                                : 'text-gray-400 hover:text-gray-200'
                        }`}
                    >
                        {lang}
                    </button>
                )
            })}
        </div>
    )
}

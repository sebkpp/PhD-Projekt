import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import './i18n'
import AppRouter from './AppRouter.jsx'
import { PhaseProvider } from './components/PhaseProvider.jsx'
import LanguageSwitcher from './components/LanguageSwitcher.jsx'

createRoot(document.getElementById('root')).render(
    <StrictMode>
        <LanguageSwitcher />
        <PhaseProvider>
            <AppRouter />
        </PhaseProvider>
    </StrictMode>
)
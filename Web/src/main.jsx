import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import AppRouter from './AppRouter.jsx'
import { PhaseProvider } from './components/PhaseProvider.jsx'

createRoot(document.getElementById('root')).render(
    <StrictMode>
        <PhaseProvider>
            <AppRouter />
        </PhaseProvider>
    </StrictMode>
)
import { useParams } from 'react-router-dom'
import { usePhase } from '../../components/PhaseProvider.jsx'
import { useConfigurationForm } from './useConfigurationForm'
import ConfigurationForm from './ConfigurationForm'

export default function ConfigPage() {
    const { experimentId  } = useParams()
    const { setCurrentPhase, setTotalTrials } = usePhase()


    const handleSave = (configs) => {
        setTotalTrials(configs.length) // z.B. beim Speichern
    }

    // Alle Form-Logik & State wird vom Hook bereitgestellt
    const configFormProps = useConfigurationForm(experimentId, setCurrentPhase)

    // UI-Komponente bekommt alle Props und rendert das Formular
    return <ConfigurationForm {...configFormProps} experiment_id={experimentId} />
}

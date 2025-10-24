import {Outlet, useOutletContext, useParams} from 'react-router-dom'
import Timeline from '../components/Timeline.jsx'
import PlayerStatus from '../components/participantStatus.jsx'
import Breadcrumbs from '../components/Breadcrumbs.jsx';

export default function Layout({ playerSlots }) {
    const { studyId, experimentId } = useParams();

    const breadcrumbItems = [
        { label: "Studienübersicht", to: "/" },
        { label: `Studie ${studyId}`, to: `/study/${studyId}/experiments` },
        { label: `Experiment ${experimentId}` }
    ];

    return (
        <main className="bg-background text-foreground min-h-screen p-6">
            <div className="max-w-6xl mx-auto space-y-6">
                <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center w-full bg-gray-800/80 backdrop-blur-sm rounded-lg px-4 shadow-md h-10">
                        <Breadcrumbs items={breadcrumbItems} styled={false} />
                        <div className="flex-1" />
                        <PlayerStatus playerSlots={playerSlots} />
                    </div>
                </div>
                <Timeline/>
                <Outlet />
            </div>
        </main>
    )
}


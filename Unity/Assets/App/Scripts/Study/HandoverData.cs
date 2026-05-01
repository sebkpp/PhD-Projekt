using System;

namespace Application.Scripts.Study
{
    /// <summary>
    /// All timing and participant data for one completed handover interaction.
    /// Passed to BackendService.ReportHandover() — BackendService handles HTTP and local logging.
    /// </summary>
    public class HandoverData
    {
        public int      TrialId;
        public int      GiverParticipantId;
        public int      ReceiverParticipantId;
        public string   GraspedObject;
        public DateTime GiverGraspedAt;
        public DateTime ReceiverTouchedAt;
        public DateTime ReceiverGraspedAt;
        public DateTime? GiverReleasedAt;
        public bool     IsError;
        public string   ErrorType;
    }
}

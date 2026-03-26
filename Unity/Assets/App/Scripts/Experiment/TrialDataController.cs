using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace Application.Scripts.Experiment
{
    public class TrialDataController : MonoBehaviour
    {
        public int TrialId { get; private set; }

        public CollaborationPhase Phase { get; private set; }
        public int GiverId { get; private set; }
        public int ReceiverId { get; private set; }

        public Role GetPlayerRole(int id)
        {
            if (id == GiverId)
                return Role.Giver;

            return Role.Receiver;
        }

        private void Start()
        {
            //Dummy data
            TrialId = 0;
            Phase = CollaborationPhase.Inactive;
            GiverId = 1;
            ReceiverId = 2;
        }

        //OnGrip, OnTransfer.. triggers
        //new Coroutine for trial data



    }
}
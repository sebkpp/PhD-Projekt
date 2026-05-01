using System;
using System.Diagnostics;
using UnityEngine;
using UnityEngine.Events;

namespace Application.Scripts.Experiment
{
    public class ExperimentTimer : MonoBehaviour
    {
        private readonly Stopwatch _stopwatch = new();

        public TimeSpan GetTimeStopwatch()
        {
            return _stopwatch.Elapsed;
        }
        public bool StopwatchIsRunning()
        {
            return _stopwatch.IsRunning;
        }
        public void StartStopwatch()
        {
            _stopwatch.Start();
        }
        public void ResetStopwatch()
        {
            _stopwatch.Reset();
        }

        public void StopStopwatch()
        {
            _stopwatch.Stop();
        }
    }
}

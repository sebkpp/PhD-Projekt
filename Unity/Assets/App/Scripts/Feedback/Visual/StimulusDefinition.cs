using UnityEngine;

namespace Application.Scripts.Feedback.Visual
{
    /// <summary>
    /// Defines the visual taxonomy for one stimulus by name.
    /// Place assets in Assets/App/Resources/Stimuli/ named exactly like the backend stimulus name.
    /// Loaded at runtime via Resources.Load&lt;StimulusDefinition&gt;("Stimuli/{stimulusName}").
    /// </summary>
    [CreateAssetMenu(fileName = "StimulusDefinition", menuName = "ManualStudy/StimulusDefinition")]
    public class StimulusDefinition : ScriptableObject
    {
        [Tooltip("Must match the backend stimulus name exactly (e.g. 'outer_hand').")]
        public string stimulusName;

        [Tooltip("IH: hand penetrates object. OH: hand stays outside (LateUpdate bone override).")]
        public HandRenderingMode renderingMode;

        [Tooltip("Where the visual effect is applied.")]
        public FeedbackTarget target;

        [Tooltip("How the visual effect is rendered.")]
        public VisualTechnique technique;

        [Tooltip("Shader property name for ColorMapping technique (e.g. '_Color').")]
        public string colorShaderProperty = "_Color";

        [Tooltip("Grip 0..1 mapped through this gradient for ColorMapping technique.")]
        public Gradient colorGradient;
    }
}

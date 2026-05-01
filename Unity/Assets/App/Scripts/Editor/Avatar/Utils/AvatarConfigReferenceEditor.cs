using Application.Scripts.Avatar.Utils;
using UnityEditor;

namespace Application.Scripts.Editor.Avatar.Utils
{
    /// <summary>
    /// Custom inspector for the <see cref="AvatarConfigReference"/> component.
    /// Displays additional details of the assigned <see cref="AvatarConfig"/> directly in the Inspector.
    /// </summary>
    [CustomEditor(typeof(AvatarConfigReference))]
    public class AvatarConfigReferenceEditor : UnityEditor.Editor
    {
        /// <summary>
        /// Draws the custom inspector UI.
        /// If an <see cref="AvatarConfig"/> is assigned, its serialized properties are shown below the default inspector.
        /// </summary>
        public override void OnInspectorGUI()
        {
            DrawDefaultInspector();
        
            AvatarConfigReference configReference = (AvatarConfigReference)target;

            if (configReference.Config != null)
            {
                EditorGUILayout.Space();
                EditorGUILayout.LabelField("Avatar Config Details", EditorStyles.boldLabel);

                SerializedObject configSerialized = new SerializedObject(configReference.Config);
                SerializedProperty property = configSerialized.GetIterator();

                // Skip first property
                if (property.NextVisible(true)) 
                {
                    do
                    {
                        // script-field should not be rendered
                        if (property.name == "m_Script") continue;

                        EditorGUILayout.PropertyField(property, true);
                    } while (property.NextVisible(false));
                }

                configSerialized.ApplyModifiedProperties();
            }
            else
            {
                EditorGUILayout.HelpBox("No AvatarConfig applied!", MessageType.Warning);
            }
        }
    }
}
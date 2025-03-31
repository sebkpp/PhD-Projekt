using Application.Scripts.Avatar.Utils;
using UnityEditor;

namespace Application.Scripts.Editor.Avatar.Utils
{
    [CustomEditor(typeof(AvatarConfigReference))]
    public class AvatarConfigReferenceEditor : UnityEditor.Editor
    {
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
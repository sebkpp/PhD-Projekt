using Application.Scripts.Avatar.Visuals;
using UnityEditor;

namespace Application.Scripts.Editor.Player
{
    [CustomEditor(typeof(PlayerVisuals))]
    public class PlayerVisualsEditor : UnityEditor.Editor
    {
        private SerializedProperty _avatarSet;
        private SerializedProperty _avatarDriver;
        private SerializedProperty _avatarConfigReference;
        private SerializedProperty _hmdCameraTransform;
        private SerializedProperty _avatarVisibility;

        private void OnEnable()
        {
            _avatarSet             = serializedObject.FindProperty("_avatarSet");
            _avatarDriver          = serializedObject.FindProperty("_avatarDriver");
            _avatarConfigReference = serializedObject.FindProperty("_avatarConfigReference");
            _hmdCameraTransform    = serializedObject.FindProperty("_hmdCameraTransform");
            _avatarVisibility      = serializedObject.FindProperty("_avatarVisibility");
        }

        public override void OnInspectorGUI()
        {
            serializedObject.Update();
            EditorGUILayout.PropertyField(_avatarSet);
            EditorGUILayout.PropertyField(_avatarDriver);
            EditorGUILayout.PropertyField(_avatarConfigReference);
            EditorGUILayout.PropertyField(_hmdCameraTransform);
            EditorGUILayout.PropertyField(_avatarVisibility);
            EditorGUILayout.PropertyField(serializedObject.FindProperty("_avatarInitialized"));
            serializedObject.ApplyModifiedProperties();
        }
    }
}

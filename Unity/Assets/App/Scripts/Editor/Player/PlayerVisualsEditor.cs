using System.Linq;
using Application.Scripts.ScriptableObjects;
using Application.Scripts.Avatar;
using Application.Scripts.Avatar.Visuals;
using UnityEditor;
using UnityEngine;

namespace Application.Scripts.Editor.Player
{
    [CustomEditor(typeof(PlayerVisuals))]
    public class PlayerVisualsEditor : UnityEditor.Editor
    {
        private SerializedProperty _avatarVisibility;
        private SerializedProperty _handMeshRenderer;
        //private SerializedProperty _gender;
        private string[] _names;
        private AvatarScriptableObject[] _avatars;


        private int _selectedAvatarIndex = 0;

        void OnEnable()
        {
            //_gender = serializedObject.FindProperty("_gender");
            _avatarVisibility = serializedObject.FindProperty("avatarVisibility");
            _handMeshRenderer = serializedObject.FindProperty("handMeshRenderer");
            _avatars = LoadAvatars();
            _names = ExtractNames(_avatars);
        }

        public override void OnInspectorGUI()
        {
            serializedObject.Update();
            EditorGUILayout.PropertyField(_handMeshRenderer);

            EditorGUILayout.PropertyField(_avatarVisibility);

            EditorGUI.BeginChangeCheck();
            //EditorGUILayout.PropertyField(_gender);
            if (EditorGUI.EndChangeCheck())
            {
                _avatars = LoadAvatars();
                _names = ExtractNames(_avatars);
                _selectedAvatarIndex = 0;
                if (_avatars.Length != 0)
                {
                    ((PlayerVisuals)serializedObject.targetObject).Avatar = _avatars[0];
                }
            }

            EditorGUI.BeginChangeCheck();
            _selectedAvatarIndex = EditorGUILayout.Popup("Select Avatar", _selectedAvatarIndex, _names);
            if (EditorGUI.EndChangeCheck())
            {
                if (_avatars.Length != 0)
                {
                    ((PlayerVisuals)serializedObject.targetObject).Avatar = _avatars[_selectedAvatarIndex];
                }
            }


            EditorGUILayout.PropertyField(serializedObject.FindProperty("avatarInitialized"));

            serializedObject.ApplyModifiedProperties();
        }

        private string[] ExtractNames(AvatarScriptableObject[] avatarList)
        {
            return avatarList.Select(a => a.name).ToArray();
        }


        private AvatarScriptableObject[] LoadAvatars()
        {
            AvatarScriptableObject[] allAvatars = Resources.LoadAll<AvatarScriptableObject>("Avatars");

            // if (_gender.enumValueIndex == (int)Gender.Undefined)
            // {
            //     return allAvatars;
            // }
            return allAvatars;

            //return allAvatars.Where(a => (int)a.Gender == _gender.enumValueIndex).ToArray();
        }
    }
}
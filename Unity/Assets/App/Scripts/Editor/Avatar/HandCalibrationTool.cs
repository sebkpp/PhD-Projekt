#if UNITY_EDITOR
using Application.Scripts.Avatar.Driver;
using Application.Scripts.Avatar.Mapping;
using Application.Scripts.Avatar.Utils;
using Application.Scripts.ScriptableObjects;
using UnityEditor;
using UnityEngine;
using UnityEngine.XR.Hands;

namespace Application.Scripts.Editor.Avatar
{
    /// <summary>
    /// Editor tool to bake per-joint rotation offsets from an OpenXR hand pose
    /// into an AvatarConfig asset.
    ///
    /// Usage:
    ///   Tools → Avatar → Hand Calibration Tool
    ///   1. Open a scene with the avatar in T-pose and the XR subsystem running.
    ///   2. Assign the AvatarScriptableObject and the AvatarConfig to calibrate.
    ///   3. Have the user hold the same T-pose.
    ///   4. Click "Capture Left" and "Capture Right".
    ///   5. Click "Save to AvatarConfig".
    /// </summary>
    public class HandCalibrationTool : EditorWindow
    {
        private AvatarScriptableObject _avatarAsset;
        private AvatarConfig _config;
        private GameObject _sceneAvatar;

        private Vector3[,] _leftOffsets  = new Vector3[5, 3];
        private Vector3[,] _rightOffsets = new Vector3[5, 3];
        private bool _leftCaptured, _rightCaptured;

        [MenuItem("Tools/Avatar/Hand Calibration Tool")]
        public static void ShowWindow()
        {
            GetWindow<HandCalibrationTool>("Hand Calibration");
        }

        private void OnGUI()
        {
            EditorGUILayout.LabelField("Avatar Hand Calibration", EditorStyles.boldLabel);
            EditorGUILayout.Space();

            _avatarAsset = (AvatarScriptableObject)EditorGUILayout.ObjectField(
                "Avatar Asset", _avatarAsset, typeof(AvatarScriptableObject), false);
            _config = (AvatarConfig)EditorGUILayout.ObjectField(
                "AvatarConfig", _config, typeof(AvatarConfig), false);
            _sceneAvatar = (GameObject)EditorGUILayout.ObjectField(
                "Scene Avatar (T-pose)", _sceneAvatar, typeof(GameObject), true);

            EditorGUILayout.Space();
            EditorGUILayout.HelpBox(
                "1. Place the avatar in T-pose in the scene.\n" +
                "2. Have the player hold T-pose in the headset.\n" +
                "3. Click Capture while the XR subsystem is running (enter Play mode).\n" +
                "4. Save to AvatarConfig.", MessageType.Info);

            EditorGUILayout.Space();

            using (new EditorGUI.DisabledScope(!Application.isPlaying))
            {
                if (GUILayout.Button("Capture Left Hand Offsets"))
                    CaptureOffsets(Handedness.Left, ref _leftOffsets, ref _leftCaptured);

                if (GUILayout.Button("Capture Right Hand Offsets"))
                    CaptureOffsets(Handedness.Right, ref _rightOffsets, ref _rightCaptured);
            }

            EditorGUILayout.Space();
            EditorGUILayout.LabelField($"Left captured:  {_leftCaptured}");
            EditorGUILayout.LabelField($"Right captured: {_rightCaptured}");

            EditorGUILayout.Space();

            using (new EditorGUI.DisabledScope(!_leftCaptured || !_rightCaptured || _config == null))
            {
                if (GUILayout.Button("Save to AvatarConfig"))
                    SaveToConfig();
            }
        }

        private static readonly (XRHandJointID metacarpal, XRHandJointID proximal, XRHandJointID intermediate)[]
            k_FingerJoints =
            {
                (XRHandJointID.ThumbMetacarpal,  XRHandJointID.ThumbProximal,   XRHandJointID.ThumbDistal),
                (XRHandJointID.IndexMetacarpal,  XRHandJointID.IndexProximal,   XRHandJointID.IndexIntermediate),
                (XRHandJointID.MiddleMetacarpal, XRHandJointID.MiddleProximal,  XRHandJointID.MiddleIntermediate),
                (XRHandJointID.RingMetacarpal,   XRHandJointID.RingProximal,    XRHandJointID.RingIntermediate),
                (XRHandJointID.LittleMetacarpal, XRHandJointID.LittleProximal,  XRHandJointID.LittleIntermediate),
            };

        private void CaptureOffsets(Handedness handedness, ref Vector3[,] offsets, ref bool captured)
        {
            if (_sceneAvatar == null || _avatarAsset == null) { Debug.LogWarning("[Calibration] Assign scene avatar and asset first."); return; }

            var subs = new System.Collections.Generic.List<XRHandSubsystem>();
            SubsystemManager.GetSubsystems(subs);
            XRHandSubsystem subsystem = null;
            foreach (var s in subs) { if (s.running) { subsystem = s; break; } }
            if (subsystem == null) { Debug.LogWarning("[Calibration] XRHandSubsystem not running. Enter Play mode."); return; }

            var boneRef = AvatarBoneReference.Build(_avatarAsset, _sceneAvatar);
            int side = handedness == Handedness.Left ? 0 : 1;

            XRHand hand = handedness == Handedness.Left ? subsystem.leftHand : subsystem.rightHand;
            if (!hand.isTracked) { Debug.LogWarning("[Calibration] Hand not tracked."); return; }

            for (int f = 0; f < 5; f++)
            {
                var joints = k_FingerJoints[f];
                XRHandJointID[] xrIds = { joints.metacarpal, joints.proximal, joints.intermediate };

                for (int j = 0; j < 3; j++)
                {
                    Transform bone = boneRef.FingerBones[side, f, j];
                    if (bone == null) continue;

                    if (hand.GetJoint(xrIds[j]).TryGetPose(out Pose pose))
                    {
                        Quaternion offset = Quaternion.Inverse(pose.rotation) * bone.rotation;
                        offsets[f, j] = offset.eulerAngles;
                    }
                }
            }

            captured = true;
            Debug.Log($"[Calibration] {handedness} hand offsets captured.");
        }

        private void SaveToConfig()
        {
            SerializedObject so = new SerializedObject(_config);
            so.ApplyModifiedProperties();
            EditorUtility.SetDirty(_config);
            AssetDatabase.SaveAssets();
            Debug.Log("[Calibration] Saved to AvatarConfig. Review fingerForward/fingerUp Axis fields manually in Inspector for coordinate alignment.");
        }
    }
}
#endif

Shader "Mirror/MirrorReflection"
{
    Properties
    {
        _Color              ("Color",                Color) = (1,1,1,1)
        _ReflectionTexLeft  ("Mirror Texture Left",  2D)    = "black" {}
        _ReflectionTexRight ("Mirror Texture Right", 2D)    = "black" {}

        [Header(Fresnel)]
        _FresnelPower ("Fresnel Power",     Range(0, 8)) = 0
        _FresnelColor ("Fresnel Color",     Color)       = (1,1,1,1)
        _FresnelBlend ("Fresnel Intensity", Range(0, 1)) = 0
    }

    SubShader
    {
        Tags
        {
            "RenderType"     = "Opaque"
            "RenderPipeline" = "UniversalPipeline"
            "Queue"          = "Geometry"
        }

        Pass
        {
            Name "UniversalForward"
            Tags { "LightMode" = "UniversalForward" }

            HLSLPROGRAM
            #pragma vertex   Vert
            #pragma fragment Frag

            // Stereo / instancing variants
            #pragma multi_compile_instancing
            #pragma multi_compile _ UNITY_SINGLE_PASS_STEREO STEREO_INSTANCING_ON STEREO_MULTIVIEW_ON

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            // ── Textures ────────────────────────────────────────────────────────

            TEXTURE2D(_ReflectionTexLeft);  SAMPLER(sampler_ReflectionTexLeft);
            TEXTURE2D(_ReflectionTexRight); SAMPLER(sampler_ReflectionTexRight);

            // ── Constant buffer ─────────────────────────────────────────────────

            CBUFFER_START(UnityPerMaterial)
                half4 _Color;
                half  _FresnelPower;
                half4 _FresnelColor;
                half  _FresnelBlend;
            CBUFFER_END

            // ── Vertex input / output ────────────────────────────────────────────

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS   : NORMAL;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct Varyings
            {
                float4 positionHCS : SV_POSITION;
                float4 screenPos   : TEXCOORD0;
                float3 normalWS    : TEXCOORD1;
                float3 viewDirWS   : TEXCOORD2;
                UNITY_VERTEX_INPUT_INSTANCE_ID
                UNITY_VERTEX_OUTPUT_STEREO
            };

            // ── Vertex shader ────────────────────────────────────────────────────

            Varyings Vert(Attributes IN)
            {
                Varyings OUT;
                UNITY_SETUP_INSTANCE_ID(IN);
                UNITY_TRANSFER_INSTANCE_ID(IN, OUT);
                UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(OUT);

                float3 positionWS  = TransformObjectToWorld(IN.positionOS.xyz);
                OUT.positionHCS    = TransformWorldToHClip(positionWS);
                OUT.screenPos      = ComputeScreenPos(OUT.positionHCS);
                OUT.normalWS       = TransformObjectToWorldNormal(IN.normalOS);
                OUT.viewDirWS      = GetWorldSpaceNormalizeViewDir(positionWS);
                return OUT;
            }

            // ── Fragment shader ──────────────────────────────────────────────────

            half4 Frag(Varyings IN) : SV_Target
            {
                UNITY_SETUP_INSTANCE_ID(IN);
                UNITY_SETUP_STEREO_EYE_INDEX_POST_VERTEX(IN);

                // Screen-space UV (perspective-correct)
                float2 uv = IN.screenPos.xy / IN.screenPos.w;

                // Sample both reflection textures and pick the correct eye.
                // unity_StereoEyeIndex: 0 = left, 1 = right.
                // lerp(left, right, eyeIndex) avoids branching on the GPU.
                half4 left       = SAMPLE_TEXTURE2D(_ReflectionTexLeft,  sampler_ReflectionTexLeft,  uv);
                half4 right      = SAMPLE_TEXTURE2D(_ReflectionTexRight, sampler_ReflectionTexRight, uv);
                half4 reflection = lerp(left, right, (half)unity_StereoEyeIndex);

                // Tint
                half4 color = reflection * _Color;

                // Fresnel overlay (branchless — compiler eliminates when _FresnelBlend = 0)
                half NdotV   = saturate(dot(normalize(IN.normalWS), normalize(IN.viewDirWS)));
                half fresnel = pow(1.0h - NdotV, _FresnelPower);
                color        = lerp(color, _FresnelColor, fresnel * _FresnelBlend);

                return color;
            }
            ENDHLSL
        }
    }

    FallBack "Hidden/InternalErrorShader"
}

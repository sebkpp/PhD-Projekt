using Application.Scripts.Avatar;
using VirtualGrasp;

namespace Application.Scripts.Utils.Extensions
{
    public static class RigConverter
    {
        public static VG_HandSide ToVGHandSide(this RigPart rigPart)
        {
            return rigPart switch
            {
                RigPart.LeftController => VG_HandSide.LEFT,
                RigPart.RightController => VG_HandSide.RIGHT,
                _ => VG_HandSide.UNKNOWN_HANDSIDE,
            };
        }
        
        public static RigPart ToRigPart(this VG_HandSide handSide)
        {
            return handSide switch
            {
                VG_HandSide.LEFT => RigPart.LeftController,
                VG_HandSide.RIGHT => RigPart.RightController,
                _ => RigPart.Undefined,
            };
        }
    }
}
import { useTheme } from "../../../features/theme/theme-context";
import MagicRings from "./MagicRings";

export default function MagicRingsBackground() {
  const { resolvedTheme } = useTheme();
  const dark = resolvedTheme === "dark";
  return <div className="magic-rings-background" aria-hidden="true"><MagicRings color={dark?"#b8ff3d":"#0f9f6e"} colorTwo={dark?"#25e6f4":"#007f91"} speed={.42} ringCount={5} attenuation={14} lineThickness={1.35} baseRadius={.22} radiusStep={.09} scaleRate={.055} opacity={dark?.46:.58} noiseAmount={.015} rotation={-18} ringGap={1.65} fadeIn={.85} fadeOut={1.05} /></div>;
}

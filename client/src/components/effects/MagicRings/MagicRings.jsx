import { useEffect, useRef } from "react";
import PropTypes from "prop-types";
import * as THREE from "three";
import "./MagicRings.css";

const vertexShader = `void main(){gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}`;
const fragmentShader = `
precision highp float;
uniform float uTime,uAttenuation,uLineThickness,uBaseRadius,uRadiusStep,uScaleRate,uOpacity,uNoiseAmount,uRotation,uRingGap,uFadeIn,uFadeOut;
uniform vec2 uResolution; uniform vec3 uColor,uColorTwo; uniform int uRingCount;
const float HP=1.5707963; const float CYCLE=3.45;
float fade(float t){return t<uFadeIn?smoothstep(0.,uFadeIn,t):1.-smoothstep(uFadeOut,CYCLE-.2,t);}
float ring(vec2 p,float ri,float cut,float t0,float px){float t=mod(uTime+t0,CYCLE);float r=ri+t/CYCLE*uScaleRate;float d=abs(length(p)-r);float a=atan(abs(p.y),abs(p.x))/HP;float th=max(1.-a,.5)*px*uLineThickness;float h=(1.-smoothstep(th,th*1.5,d))+1.;d+=pow(cut*a,3.)*r;return h*exp(-uAttenuation*d)*fade(t);}
void main(){float px=1./min(uResolution.x,uResolution.y);vec2 p=(gl_FragCoord.xy-.5*uResolution.xy)*px;float cr=cos(uRotation),sr=sin(uRotation);p=mat2(cr,-sr,sr,cr)*p;vec3 c=vec3(0.);float rcf=max(float(uRingCount)-1.,1.);for(int i=0;i<10;i++){if(i>=uRingCount)break;float fi=float(i);vec3 rc=mix(uColor,uColorTwo,fi/rcf);c=mix(c,rc,vec3(ring(p,uBaseRadius+fi*uRadiusStep,pow(uRingGap,fi),i==0?0.:2.95*fi,px)));}float n=fract(sin(dot(gl_FragCoord.xy+uTime*100.,vec2(12.9898,78.233)))*43758.5453);c+=(n-.5)*uNoiseAmount;gl_FragColor=vec4(c,max(c.r,max(c.g,c.b))*uOpacity);}`;

export default function MagicRings({ color="#fc42ff", colorTwo="#42fcff", speed=1, ringCount=6, attenuation=10, lineThickness=2, baseRadius=.35, radiusStep=.1, scaleRate=.1, opacity=1, blur=0, noiseAmount=.1, rotation=0, ringGap=1.5, fadeIn=.7, fadeOut=.5 }) {
  const mountRef = useRef(null);
  const propsRef = useRef();
  propsRef.current = { color,colorTwo,speed,ringCount,attenuation,lineThickness,baseRadius,radiusStep,scaleRate,opacity,noiseAmount,rotation,ringGap,fadeIn,fadeOut };

  useEffect(() => {
    const mount = mountRef.current;
    if (!mount) return undefined;
    let renderer;
    try { renderer = new THREE.WebGLRenderer({ alpha:true, antialias:false }); } catch { return undefined; }
    if (!renderer.capabilities.isWebGL2) { renderer.dispose(); return undefined; }
    renderer.setClearColor(0x000000,0);
    mount.appendChild(renderer.domElement);
    const scene = new THREE.Scene();
    const camera = new THREE.OrthographicCamera(-.5,.5,.5,-.5,.1,10); camera.position.z=1;
    const geometry = new THREE.PlaneGeometry(1,1);
    const uniforms = { uTime:{value:0},uAttenuation:{value:0},uResolution:{value:new THREE.Vector2()},uColor:{value:new THREE.Color()},uColorTwo:{value:new THREE.Color()},uLineThickness:{value:0},uBaseRadius:{value:0},uRadiusStep:{value:0},uScaleRate:{value:0},uRingCount:{value:0},uOpacity:{value:1},uNoiseAmount:{value:0},uRotation:{value:0},uRingGap:{value:1.6},uFadeIn:{value:.5},uFadeOut:{value:.75} };
    const material = new THREE.ShaderMaterial({ vertexShader,fragmentShader,uniforms,transparent:true });
    scene.add(new THREE.Mesh(geometry,material));
    let frameId=0, visible=false, pageVisible=!document.hidden, elapsed=0, lastTime=0;
    const motionQuery=window.matchMedia("(prefers-reduced-motion: reduce)");
    let reduceMotion=motionQuery.matches;
    const render=()=>{const p=propsRef.current; uniforms.uTime.value=elapsed;uniforms.uAttenuation.value=p.attenuation;uniforms.uColor.value.set(p.color);uniforms.uColorTwo.value.set(p.colorTwo);uniforms.uLineThickness.value=p.lineThickness;uniforms.uBaseRadius.value=p.baseRadius;uniforms.uRadiusStep.value=p.radiusStep;uniforms.uScaleRate.value=p.scaleRate;uniforms.uRingCount.value=p.ringCount;uniforms.uOpacity.value=p.opacity;uniforms.uNoiseAmount.value=reduceMotion?0:p.noiseAmount;uniforms.uRotation.value=p.rotation*Math.PI/180;uniforms.uRingGap.value=p.ringGap;uniforms.uFadeIn.value=p.fadeIn;uniforms.uFadeOut.value=p.fadeOut;renderer.render(scene,camera);};
    const resize=()=>{const w=mount.clientWidth,h=mount.clientHeight;if(!w||!h)return;const dpr=Math.min(window.devicePixelRatio,1.5);renderer.setPixelRatio(dpr);renderer.setSize(w,h,false);uniforms.uResolution.value.set(w*dpr,h*dpr);render();};
    const animate=(time)=>{frameId=requestAnimationFrame(animate);const dt=lastTime?Math.min(time-lastTime,100):0;lastTime=time;elapsed+=dt*.001*propsRef.current.speed;render();};
    const stop=()=>{if(frameId)cancelAnimationFrame(frameId);frameId=0;};
    const start=()=>{if(visible&&pageVisible&&!reduceMotion&&!frameId){lastTime=0;frameId=requestAnimationFrame(animate);}else if(reduceMotion)render();};
    resize(); const ro=new ResizeObserver(resize);ro.observe(mount);
    const io=new IntersectionObserver(([entry])=>{visible=entry.isIntersecting;visible?start():stop();});io.observe(mount);
    const onVisibility=()=>{pageVisible=!document.hidden;pageVisible?start():stop();};document.addEventListener("visibilitychange",onVisibility);
    const onMotion=(event)=>{reduceMotion=event.matches;if(reduceMotion){stop();render();}else start();};motionQuery.addEventListener("change",onMotion);
    return()=>{stop();io.disconnect();ro.disconnect();document.removeEventListener("visibilitychange",onVisibility);motionQuery.removeEventListener("change",onMotion);renderer.domElement.remove();geometry.dispose();material.dispose();renderer.dispose();};
  },[]);
  return <div ref={mountRef} className="magic-rings-container" style={blur>0?{filter:`blur(${blur}px)`}:undefined} aria-hidden="true" />;
}

MagicRings.propTypes={color:PropTypes.string,colorTwo:PropTypes.string,speed:PropTypes.number,ringCount:PropTypes.number,attenuation:PropTypes.number,lineThickness:PropTypes.number,baseRadius:PropTypes.number,radiusStep:PropTypes.number,scaleRate:PropTypes.number,opacity:PropTypes.number,blur:PropTypes.number,noiseAmount:PropTypes.number,rotation:PropTypes.number,ringGap:PropTypes.number,fadeIn:PropTypes.number,fadeOut:PropTypes.number};

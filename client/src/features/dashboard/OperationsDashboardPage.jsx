import { ArrowRight, BarChart3, Boxes, Plus, Radio, Zap } from "lucide-react";
import { Link } from "react-router-dom";
import AppLayout from "../../layouts/AppLayout";
import { useAuth } from "../auth/auth-context";
import dashboardHero from "../../assets/energy/dashboard-grid-hero.jpg";
import storageImage from "../../assets/energy/battery-storage-register.jpg";
import solarGridImage from "../../assets/energy/energy-infrastructure-hero.jpg";
import windImage from "../../assets/energy/carousel-wind-offshore.jpg";
import hydroImage from "../../assets/energy/carousel-hydroelectric.jpg";
import cityImage from "../../assets/energy/carousel-smart-city.jpg";
import DepthCarousel from "../../components/effects/DepthCarousel/DepthCarousel";

const actions = [
  { to: "/resumen", label: "Abrir resumen", detail: "Analiza precios y tendencias", icon: BarChart3 },
  { to: "/precios", label: "Consultar mercados", detail: "Filtra y exporta datos", icon: Zap },
  { to: "/productos", label: "Gestionar productos", detail: "Revisa tu catálogo", icon: Boxes },
  { to: "/productos/create", label: "Nuevo producto", detail: "Añade una nueva referencia", icon: Plus },
];
const panorama = [
  { image: windImage, alt: "Parque eólico offshore durante la hora azul", category: "Generación renovable", title: "Energía eólica", description: "Infraestructura preparada para un sistema en constante evolución." },
  { image: solarGridImage, alt: "Paneles solares conectados a una subestación eléctrica", category: "Generación distribuida", title: "Solar conectada", description: "Producción e infraestructura bajo una misma visión energética." },
  { image: dashboardHero, alt: "Red de alta tensión y subestación al amanecer", category: "Transmisión", title: "Red inteligente", description: "La infraestructura que conecta generación, demanda y mercado." },
  { image: storageImage, alt: "Instalación de baterías industriales junto a un parque solar", category: "Flexibilidad", title: "Almacenamiento", description: "Capacidad operativa para una nueva generación de sistemas energéticos." },
  { image: hydroImage, alt: "Central hidroeléctrica integrada en un valle de montaña", category: "Infraestructura", title: "Energía hidroeléctrica", description: "Escala, precisión y recursos trabajando de forma coordinada." },
  { image: cityImage, alt: "Ciudad y subestación eléctrica conectadas durante el atardecer", category: "Demanda conectada", title: "Ciudad energética", description: "Redes urbanas preparadas para decisiones con mayor contexto." },
];

export default function OperationsDashboardPage() {
  const auth = useAuth();
  const username = auth.getUser();
  return <AppLayout>
    <header className="dashboard-welcome"><div><p className="eyebrow">Centro de operaciones</p><h1>Bienvenido, {username}</h1><p>Consulta el mercado y gestiona tu actividad energética desde un único espacio.</p></div><span className="workspace-status"><i />Espacio conectado</span></header>
    <div className="dashboard-home-grid">
      <section className="operations-hero"><img src={dashboardHero} alt="Red eléctrica y subestación conectadas al amanecer" width="1600" height="1000" fetchPriority="high" /><div className="operations-hero-overlay"><span className="energy-kicker"><Radio />Infraestructura conectada</span><h2>Energía en movimiento</h2><p>Información de mercado y herramientas operativas para decidir con mayor contexto.</p><Link className="button operations-hero-cta" to="/resumen">Explorar resumen <ArrowRight size={17} /></Link></div></section>
      <aside className="quick-actions" aria-labelledby="quick-actions-title"><div><p className="eyebrow">Accesos directos</p><h2 id="quick-actions-title">¿Qué quieres hacer?</h2></div><div className="quick-action-list">{actions.map(({to,label,detail,icon:Icon})=><Link key={to} to={to} className="quick-action"><span><Icon /></span><div><strong>{label}</strong><small>{detail}</small></div><ArrowRight /></Link>)}</div></aside>
    </div>
    <section className="energy-panorama" aria-labelledby="panorama-title"><header><div><p className="eyebrow">Panorama energético</p><h2 id="panorama-title">Infraestructura que conecta el presente.</h2><p>Una visión cercana de los sistemas que impulsan el mercado energético.</p></div><span>Arrastra · Explora · Usa las flechas</span></header><div className="energy-panorama-stage"><DepthCarousel items={panorama} /></div></section>
    <section className="dashboard-context"><div><p className="eyebrow">Tu espacio de trabajo</p><h2>Del dato a la operación</h2><p>WAC Energy conecta análisis de mercado y gestión de productos en un flujo de trabajo claro.</p></div><div className="context-steps"><span><b>01</b>Consulta</span><span><b>02</b>Analiza</span><span><b>03</b>Gestiona</span></div></section>
  </AppLayout>;
}

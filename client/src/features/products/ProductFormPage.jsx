import { useEffect, useState } from "react";
import { ArrowLeft, Save, Trash2 } from "lucide-react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { createTask, deleteTask, fetchTask, updateTask } from "../../api/products";
import { getApiError } from "../../api/client";
import AppLayout from "../../layouts/AppLayout";
import PageHeader from "../../components/PageHeader";
import SpinnerLoader from "../../components/SpinnerLoader";
const EMPTY = { name: "", category: "", price: "", description: "" };
export default function ProductFormPage() {
  const { id } = useParams(); const navigate = useNavigate(); const [form, setForm] = useState(EMPTY); const [status, setStatus] = useState(id ? "loading" : "idle"); const [error, setError] = useState("");
  useEffect(() => { if (!id) return; fetchTask(id).then(({ data }) => { setForm({ name: data.name || "", category: data.category || "", price: data.price || "", description: data.description || "" }); setStatus("idle"); }).catch((requestError) => { setError(getApiError(requestError, "No se pudo cargar el producto.")); setStatus("error"); }); }, [id]);
  const update = (event) => setForm({ ...form, [event.target.name]: event.target.value });
  const submit = async (event) => { event.preventDefault(); setStatus("saving"); setError(""); try { if (id) await updateTask(id, form); else await createTask(form); navigate("/productos", { replace: true }); } catch (requestError) { setError(getApiError(requestError, "No se pudo guardar el producto.")); setStatus("idle"); } };
  const remove = async () => { if (!window.confirm(`¿Eliminar “${form.name}”? Esta acción no se puede deshacer.`)) return; setStatus("saving"); try { await deleteTask(id); navigate("/productos", { replace: true }); } catch (requestError) { setError(getApiError(requestError, "No se pudo eliminar el producto.")); setStatus("idle"); } };
  return <AppLayout><PageHeader eyebrow="Catálogo" title={id ? "Editar producto" : "Nuevo producto"} description={id ? "Actualiza la información del producto." : "Añade un producto al catálogo."} actions={<Link className="button button-secondary" to="/productos"><ArrowLeft size={16} />Volver</Link>} />{status === "loading" ? <SpinnerLoader label="Cargando producto" /> : <section className="form-card"><form onSubmit={submit}><div className="form-grid"><label className="field">Nombre<input required name="name" value={form.name} onChange={update} autoFocus /></label><label className="field">Categoría<input required name="category" value={form.category} onChange={update} /></label></div><label className="field">Precio (€)<input required min="0" step="0.01" type="number" name="price" value={form.price} onChange={update} /></label><label className="field">Descripción<textarea name="description" rows="5" value={form.description} onChange={update} placeholder="Información útil para identificar el producto" /></label>{error && <p className="form-error" role="alert">{error}</p>}<div className="form-actions">{id && <button type="button" className="button button-danger" onClick={remove} disabled={status === "saving"}><Trash2 size={16} />Eliminar</button>}<button className="button button-primary" disabled={status === "saving"}><Save size={16} />{status === "saving" ? "Guardando…" : "Guardar producto"}</button></div></form></section>}</AppLayout>;
}

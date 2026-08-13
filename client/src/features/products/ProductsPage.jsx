import { useCallback, useEffect, useMemo, useState } from "react";
import { CheckCircle2, Circle, Pencil, Plus } from "lucide-react";
import { Link } from "react-router-dom";
import { fetchTasks, updateTask } from "../../api/products";
import { getApiError } from "../../api/client";
import AppLayout from "../../layouts/AppLayout";
import DataTable from "../../components/data-table/DataTable";
import PageHeader from "../../components/PageHeader";
import SpinnerLoader from "../../components/SpinnerLoader";
import StatePanel from "../../components/StatePanel";
export default function ProductsPage() {
  const [tasks, setTasks] = useState([]);
  const [status, setStatus] = useState("loading");
  const [error, setError] = useState("");
  useEffect(() => {
    fetchTasks()
      .then(({ data }) => {
        setTasks(data);
        setStatus(data.length ? "success" : "empty");
      })
      .catch((requestError) => {
        setError(
          getApiError(requestError, "No se pudieron cargar los productos."),
        );
        setStatus("error");
      });
  }, []);
  const toggle = useCallback(
    async (task) => {
      const previous = tasks;
      const next = tasks.map((item) =>
        item._id === task._id ? { ...item, completed: !item.completed } : item,
      );
      setTasks(next);
      try {
        await updateTask(task._id, { completed: !task.completed });
      } catch {
        setTasks(previous);
      }
    },
    [tasks],
  );
  const columns = useMemo(
    () => [
      {
        accessorKey: "name",
        header: "Producto",
        meta: { label: "Producto" },
        cell: ({ row }) => (
          <div className="primary-cell">
            <strong>{row.original.name}</strong>
            <span>{row.original.description || "Sin descripción"}</span>
          </div>
        ),
      },
      {
        accessorKey: "category",
        header: "Categoría",
        meta: { label: "Categoría" },
        cell: ({ getValue }) => (
          <span className="badge neutral">{getValue() || "Sin categoría"}</span>
        ),
      },
      {
        accessorKey: "price",
        header: "Precio",
        meta: { label: "Precio" },
        cell: ({ getValue }) => <strong>{getValue()} €</strong>,
      },
      {
        accessorKey: "completed",
        header: "Estado",
        meta: { label: "Estado" },
        cell: ({ row }) => (
          <button
            className={`status-button ${row.original.completed ? "complete" : "pending"}`}
            onClick={() => toggle(row.original)}
          >
            {row.original.completed ? <CheckCircle2 /> : <Circle />}
            {row.original.completed ? "Completado" : "Pendiente"}
          </button>
        ),
      },
      {
        id: "actions",
        header: "",
        enableSorting: false,
        enableHiding: false,
        cell: ({ row }) => (
          <Link
            className="icon-button"
            to={`/productos/${row.original._id}`}
            aria-label={`Editar ${row.original.name}`}
          >
            <Pencil size={17} />
          </Link>
        ),
      },
    ],
    [toggle],
  );
  return (
    <AppLayout>
      <PageHeader
        eyebrow="Catálogo"
        title="Productos"
        description="Gestiona el catálogo y su estado operativo."
        actions={
          <Link className="button button-primary" to="/productos/create">
            <Plus size={16} />
            Nuevo producto
          </Link>
        }
      />
      {status === "loading" && <SpinnerLoader label="Cargando productos" />}
      {status === "error" && (
        <StatePanel
          type="error"
          title="No se pudieron cargar los productos"
          description={error}
        />
      )}
      {status === "empty" && (
        <StatePanel
          title="Aún no hay productos"
          description="Crea el primer producto para comenzar."
          action={
            <Link className="button button-primary" to="/productos/create">
              Crear producto
            </Link>
          }
        />
      )}
      {status === "success" && (
        <DataTable
          columns={columns}
          data={tasks}
          searchPlaceholder="Buscar por nombre, categoría o precio…"
        />
      )}
    </AppLayout>
  );
}

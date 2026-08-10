import { useMemo, useState } from "react";
import PropTypes from "prop-types";
import { ChevronDown, ChevronLeft, ChevronRight, ChevronsUpDown, Search, SlidersHorizontal } from "lucide-react";
import { flexRender, getCoreRowModel, getFilteredRowModel, getPaginationRowModel, getSortedRowModel, useReactTable } from "@tanstack/react-table";
import StatePanel from "../StatePanel";

export default function DataTable({ columns, data, searchPlaceholder = "Buscar en todos los campos…", pageSize = 10 }) {
  const [sorting, setSorting] = useState([]);
  const [globalFilter, setGlobalFilter] = useState("");
  const [columnVisibility, setColumnVisibility] = useState({});
  const initialState = useMemo(() => ({ pagination: { pageSize } }), [pageSize]);
  const table = useReactTable({ data, columns, state: { sorting, globalFilter, columnVisibility }, initialState, onSortingChange: setSorting, onGlobalFilterChange: setGlobalFilter, onColumnVisibilityChange: setColumnVisibility, getCoreRowModel: getCoreRowModel(), getFilteredRowModel: getFilteredRowModel(), getSortedRowModel: getSortedRowModel(), getPaginationRowModel: getPaginationRowModel() });
  return <section className="data-table-card">
    <div className="table-toolbar"><label className="search-field"><Search size={17} /><span className="sr-only">Buscar</span><input value={globalFilter} onChange={(e) => setGlobalFilter(e.target.value)} placeholder={searchPlaceholder} /></label><details className="column-menu"><summary className="button button-secondary"><SlidersHorizontal size={16} />Columnas<ChevronDown size={15} /></summary><div className="column-options">{table.getAllLeafColumns().map((column) => <label key={column.id}><input type="checkbox" checked={column.getIsVisible()} onChange={column.getToggleVisibilityHandler()} />{column.columnDef.meta?.label || column.id}</label>)}</div></details></div>
    <div className="table-scroll"><table><thead>{table.getHeaderGroups().map((group) => <tr key={group.id}>{group.headers.map((header) => <th key={header.id}><button className={header.column.getCanSort() ? "table-sort" : "table-label"} onClick={header.column.getToggleSortingHandler()} disabled={!header.column.getCanSort()}>{flexRender(header.column.columnDef.header, header.getContext())}{header.column.getCanSort() && <ChevronsUpDown size={14} />}</button></th>)}</tr>)}</thead><tbody>{table.getRowModel().rows.map((row) => <tr key={row.id}>{row.getVisibleCells().map((cell) => <td key={cell.id} data-label={cell.column.columnDef.meta?.label || cell.column.id}>{flexRender(cell.column.columnDef.cell, cell.getContext())}</td>)}</tr>)}</tbody></table></div>
    {!table.getFilteredRowModel().rows.length ? <StatePanel title="Sin resultados" description="Prueba con otra búsqueda o modifica los filtros." /> : <div className="table-pagination"><span>{table.getFilteredRowModel().rows.length} registros · Página {table.getState().pagination.pageIndex + 1} de {table.getPageCount()}</span><div><button className="icon-button" onClick={() => table.previousPage()} disabled={!table.getCanPreviousPage()} aria-label="Página anterior"><ChevronLeft /></button><button className="icon-button" onClick={() => table.nextPage()} disabled={!table.getCanNextPage()} aria-label="Página siguiente"><ChevronRight /></button></div></div>}
  </section>;
}
DataTable.propTypes = { columns: PropTypes.arrayOf(PropTypes.object).isRequired, data: PropTypes.arrayOf(PropTypes.object).isRequired, searchPlaceholder: PropTypes.string, pageSize: PropTypes.number };

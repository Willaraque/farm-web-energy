import PropTypes from "prop-types";
export default function SpinnerLoader({ label = "Cargando" }) {
  return <div className="loading-state" role="status"><span className="spinner" aria-hidden="true" /><span>{label}…</span></div>;
}
SpinnerLoader.propTypes = { label: PropTypes.string };

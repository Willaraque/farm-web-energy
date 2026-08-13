import PropTypes from "prop-types";
import { AlertCircle, Inbox } from "lucide-react";
export default function StatePanel({
  type = "empty",
  title,
  description,
  action,
}) {
  const Icon = type === "error" ? AlertCircle : Inbox;
  return (
    <div
      className={`state-panel ${type}`}
      role={type === "error" ? "alert" : "status"}
    >
      <Icon size={28} />
      <h2>{title}</h2>
      <p>{description}</p>
      {action}
    </div>
  );
}
StatePanel.propTypes = {
  type: PropTypes.oneOf(["empty", "error"]),
  title: PropTypes.string.isRequired,
  description: PropTypes.string.isRequired,
  action: PropTypes.node,
};

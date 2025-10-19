import React from 'react';
import { useNavigate } from "react-router-dom";
import { updateTask } from "../api/Tasks";

function TaskCard({ task }) {
  const navigate = useNavigate();

  return (
    <div
      className="bg-zinc-950 p-4 hover:cursor-pointer hover:bg-gray-950 my-4"
      onClick={() => {
        console.log(task)
        navigate(`/productos/${task._id}`);
      }}
    >
      <div className="flex justify-between my-1">
        <h2 className="font-bold text-2xl">{task.name}</h2>
        <button
          onClick={async (e) => {
            e.stopPropagation();
            const res = await updateTask(task._id, {
              completed: !task.completed,
            });
            if (res.status == 200) {
              window.location.reload();
            }
          }}
        >
          <svg
            className={`w-6 h-6 ${task.completed ? "text-green-500" : ""}`}
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path d="m4.5 12.75 6 6 9-13.5" strokeLinecap="round" />
          </svg>
        </button>
      </div>
      <p className="text-slate-300">{task.category}</p>
      <p className="text-slate-300">{`${task.price} €`}</p>
      <p className="text-slate-300">{task.description}</p>
    </div>
  );
}

export default TaskCard;

import React from 'react';
import TaskCard from "../components/TaskCard";

function TaskList({ tasks }) {
  return (
    <div className="max-w-screen-xl mx-auto p-4">
      <div className="grid grid-cols-1 mt-20 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {tasks.map((task) => (
          <TaskCard task={task} key={task._id} />
        ))}
      </div>
    </div>
  );
}

export default TaskList

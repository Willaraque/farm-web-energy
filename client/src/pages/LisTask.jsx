import React from 'react';
import { useEffect, useState } from "react";
import TaskList from "../components/TaskList";
import { fetchTasks } from "../api/Tasks";
import LogingOut from "../router/LogingOut";

function LisTask() {
    const [tasks, setTasks] = useState([]);

    useEffect(() => {
        fetchTasks()
            .then(res => {
                setTasks(res.data)

            })
            .catch(err => console.log(err))
    }, []);

    return (
        <LogingOut>
            <TaskList tasks={tasks} />
        </LogingOut>
    )

}

export default LisTask;

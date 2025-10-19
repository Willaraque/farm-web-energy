import React from 'react';
import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { fetchTask, createTask, updateTask, deleteTask } from "../api/Tasks";
import LogingOut from "../router/LogingOut";

function TaskForm() {
  const [name, setName] = useState("");
  const [category, setCategory] = useState("");
  const [price, setPrice] = useState("");
  const [description, setDescription] = useState("");
  const params = useParams();
  const navigate = useNavigate();


  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      if (!params.id) {
        const res = await createTask({ name, category, price, description })
        console.log(res);

      } else {
        const res = await updateTask(params.id, { name, description })
        console.log(res);
        navigate('/productos');
      }

    } catch (error) {
      console.log(error)
    }

    e.target.reset();
    navigate('/');
  };

  useEffect(() => {
    if (params.id) {
      fetchTask(params.id)
        .then(res => {
          setTitle(res.data.title);
          setDescription(res.data.description);
        })
        .catch((err) => console.log(err))
    }
  }, [])

  return (
    <LogingOut>
      <div className="flex items-center justify-center h-[calc(100vh-10rem)]">
        <div>
          <form className="grid items-center bg-violet-600 p-10 rounded" onSubmit={handleSubmit}>
            <h1 className="flex justify-center text-3xl font-bold my-4 ">
              {
                params.id ? "Update" : "Creat"
              }
            </h1>
            <input
              type="text"
              placeholder="name"
              className="block py-2 px-3 mb-4 w-full text-black rounded"
              onChange={(e) => setName(e.target.value)}
              value={name}
              autoFocus
            />
            <input
              type="text"
              placeholder="category"
              className="block py-2 px-3 mb-4 w-full text-black rounded"
              onChange={(e) => setCategory(e.target.value)}
              value={category}
            />
            <input
              type="text"
              placeholder="price"
              className="block py-2 px-3 mb-4 w-full text-black rounded"
              onChange={(e) => setPrice(e.target.value)}
              value={price}
            />
            <textarea
              placeholder="description"
              className="block py-2 px-3 mb-4 w-full text-black rounded"
              // rows={3}
              onChange={(e) => setDescription(e.target.value)}
              value={description}
            ></textarea>
            <button
              className="bg-violet-300 hover:bg-white text-slate-800 py-2 px-2 rounded">
              {params.id ? "Actualizar" : "Crear"}
            </button>
          </form>

          <div className="grid grid-flow-row">
            {
              params.id && (
                <button className="bg-red-500 hover:bg-red-400  justify-center text-white font-bold py-2 px-4 rounded mt-5"
                  onClick={async () => {
                    try {
                      const res = await deleteTask(params.id)
                      console.log(res)
                      navigate("/productos");

                    } catch (error) {
                      console.log(error)
                    }

                  }}
                >
                  Delete
                </button>
              )

            }
            {
              <button className=" bg-violet-500 hover:bg-violet-400  justify-center text-black font-bold py-2 px-4 rounded mt-5 "
                onClick={async () => {
                  navigate("/productos");
                }}
              >
                Back
              </button>
            }

          </div>

        </div>
      </div>
    </LogingOut>
  );
}

export default TaskForm;

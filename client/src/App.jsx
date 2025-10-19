import { BrowserRouter, Routes, Route } from "react-router-dom";
import LisTask from "./pages/LisTask";
import TaskForm from "./pages/TaskForm";
import { useState } from "react";
import axios from "axios";


function App() {
  const [user, setUser] = useState([]);
  return (
    <div className="App">
      {
        !user.length > 0 ? (
          <Formulario setUser={setUser} />
        ) : (
          <BrowserRouter>
            <CollapsibleExample />
            <Routes>
              <Route
                path="/index"
                element={<Home user={user} setUser={setUser} />}
              />
              <Route path="/tasks" element={<LisTask setUser={setUser} />} />
              <Route path="/tasks/:id" element={<TaskForm setUser={setUser}/>} />
              <Route path="/tasks/new" element={<TaskForm setUser={setUser}/>} />
            </Routes>
          </BrowserRouter>
        )
        // <Home user={user} setUser={setUser}/>
      }
    </div>
  );
}

export default App;

// import express from 'express';
// import morgan  from 'morgan';
// import cookieParser from "cookie-parser";

// import authRoutes from './router/AppRouter.jsx';

// const app = express()   //servidor

// app.use(morgan('dev')); //utilizar el modulo morgan con configuraciòn dev
// app.use(express.json());
// app.use(cookieParser());//cookie convertirse en un express Json
// app.use("/api", authRoutes); 


// export default app;

import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./styles.css"; // Estilos globales sencillos

// Punto de entrada: renderiza la aplicación React en el div#root
ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);



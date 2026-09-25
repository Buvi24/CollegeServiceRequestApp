// src/main.jsx
// Entry point — mounts the React app into the #root div.
// Imports Bootstrap CSS globally so all pages can use Bootstrap classes.
import React from 'react'
import ReactDOM from 'react-dom/client'
import 'bootstrap/dist/css/bootstrap.min.css'
import App from './App'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
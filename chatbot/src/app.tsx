//Modules
import React from 'react'
import ReactDOM from 'react-dom/client'

//Components
import Home from '@/pages/Home';

//Style
import '@/styles/global.css';
import { Providers } from './components/Providers';

import { Router, Route, BrowserRouter } from 'react-router-dom';

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <Providers>
      <BrowserRouter>
        <Home />
      </BrowserRouter>
    </Providers>
  </React.StrictMode>,
)

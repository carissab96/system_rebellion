// import { StrictMode } from 'react' - TEMPORARILY DISABLED
import { createRoot } from 'react-dom/client'
import './index.css'

import { Provider } from 'react-redux'

import App from './App.tsx'
import { store } from './store/store.ts'


createRoot(document.getElementById('root')!).render(
  // <StrictMode> - TEMPORARILY DISABLED: Causing modal state reset on first click
    <Provider store={store}>
      <App />
    </Provider>
  // </StrictMode>
);

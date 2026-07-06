import { createBrowserRouter } from 'react-router-dom';
import Layout from '../components/layout/Layout';
import Home from '../pages/Home';
import Chat from '../pages/Chat';
import Explorer from '../pages/Explorer';
import ProtectedRoute from './ProtectedRoute';
import Dashboard from '../pages/Dashboard';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      { index: true, element: <Home /> },
      { path: 'explorer', element: <Explorer /> },
      { 
        path: 'chat', 
        element: <Chat /> 
      },
      {
        path: 'dashboard',
        element: <Dashboard />
      }
    ]
  }
]);

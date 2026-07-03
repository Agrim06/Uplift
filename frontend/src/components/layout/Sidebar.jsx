import React from 'react';
import { NavLink } from 'react-router-dom';
import { FiHome, FiCompass, FiCpu, FiGrid } from 'react-icons/fi';
import { clsx } from 'clsx';

export default function Sidebar() {
  const links = [
    { to: '/', label: 'Home', icon: FiHome },
    { to: '/explorer', label: 'Explorer', icon: FiCompass },
    { to: '/chat', label: 'AI Assistant', icon: FiCpu },
    { to: '/dashboard', label: 'Dashboard', icon: FiGrid },
  ];

  return (
    <aside className="w-64 border-r border-gray-100 bg-white hidden md:flex flex-col p-4 space-y-1">
      {links.map((link) => {
        const Icon = link.icon;
        return (
          <NavLink
            key={link.to}
            to={link.to}
            className={({ isActive }) => clsx(
              "flex items-center space-x-3 px-4 py-3 rounded-xl text-sm font-semibold transition cursor-pointer",
              isActive 
                ? "bg-blue-50/50 text-blue-600 border-r-4 border-blue-600" 
                : "text-gray-500 hover:bg-gray-50 hover:text-gray-700"
            )}
          >
            <Icon className="w-4 h-4 flex-shrink-0" />
            <span>{link.label}</span>
          </NavLink>
        );
      })}
    </aside>
  );
}

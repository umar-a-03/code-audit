import { NavLink } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

const navItems = [
  { path: '/dashboard', icon: 'dashboard', label: 'DASHBOARD' },
  { path: '/audits/new', icon: 'add_circle', label: 'NEW_AUDIT' },
  { path: '/batch', icon: 'workspaces', label: 'BATCH' },
  { path: '/projects', icon: 'folder_open', label: 'PROJECTS' },
  { path: '/settings', icon: 'settings_suggest', label: 'SETTINGS' },
];

const Sidebar = () => {
  const { logout, user } = useAuth();

  const { name = 'Guest', email = '' } = user || {};

  return (
    <aside className="hidden lg:flex flex-col w-64 h-screen bg-oled-black z-40 relative flex-shrink-0">
      {/* Vertical divider glow */}
      <div className="sidebar-divider-glow absolute top-0 bottom-0 right-0 h-full" />

      {/* Logo Section */}
      <div className="p-6 border-b border-white/10 relative">
        <div className="flex items-center gap-3 mb-1">
          <div className="flex items-center justify-center size-8 text-primary border border-primary shadow-neon">
            <span className="material-symbols-outlined text-[20px]">terminal</span>
          </div>
          <div>
            <h1 className="text-lg font-bold tracking-tight text-white terminal-glow">
              CodeAudit<span className="text-primary">.ai</span>
            </h1>
          </div>
        </div>
        <p className="text-[10px] uppercase tracking-widest text-primary font-mono pl-11">
          System: Online
        </p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-6 px-2 space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `${isActive ? 'nav-item-active' : 'text-gray-400 hover:text-primary hover:bg-white/5 border-r-2 border-transparent hover:border-primary/50'} group flex items-center px-4 py-3 text-sm font-medium transition-all duration-200`
            }
          >
            <span className="material-symbols-outlined mr-3 text-gray-500 group-hover:text-primary transition-colors">
              {item.icon}
            </span>
            <span className="font-mono tracking-wide group-hover:text-primary group-hover:shadow-[0_0_10px_rgba(0,255,255,0.3)] transition-all">
              {item.label}
            </span>
          </NavLink>
        ))}
      </nav>

      {/* User Profile */}
      <div className="p-4 border-t border-white/10 bg-black/50">
        <button
          onClick={logout}
          className="flex items-center gap-3 group w-full cursor-pointer"
          title="Logout"
        >
          {/* <div className="size-10 border border-primary/50 overflow-hidden relative shadow-neon-sm">
            <img
              alt="User Avatar"
              className="w-full h-full object-cover grayscale group-hover:grayscale-0 transition-all duration-300"
              src={avatar}
            />
          </div> */}
          <div className="flex-1 min-w-0 text-left">
            <p className="text-sm font-bold text-white leading-none truncate group-hover:text-primary transition-colors">
              {name}
            </p>
            <div className="flex items-center mt-1.5">
              <p className="text-[10px] text-gray-400 font-mono leading-none truncate">
                {email}
              </p>
            </div>
          </div>
          <span className="material-symbols-outlined text-gray-500 group-hover:text-neon-red text-[18px]">
            logout
          </span>
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;

import { useEffect, useState } from 'react';
import AutoMailPage from './components/AutoMailPage';
import ChatPage from './components/Chat/ChatPage';
import SearchPage from './components/Search/SearchPage';
import Login from './pages/Login';
import Register from './pages/Register';
import {
  clearAuthSession,
  getCurrentUser,
  getStoredUser,
  loginUser,
  registerUser,
  setAuthSession,
  TOKEN_STORAGE_KEY,
} from './services/api';

const APP_ROUTES = ['/search', '/chat', '/auto-mail'];

const getCurrentPath = () => {
  const path = window.location.pathname || '/';
  if (path === '/') {
    return '/search';
  }
  return path;
};

function App() {
  const [route, setRoute] = useState(getCurrentPath());
  const [user, setUser] = useState(getStoredUser());
  const [authLoading, setAuthLoading] = useState(true);
  const [submitLoading, setSubmitLoading] = useState(false);

  const navigate = (path, { replace = false } = {}) => {
    if (replace) {
      window.history.replaceState({}, '', path);
    } else if (window.location.pathname !== path) {
      window.history.pushState({}, '', path);
    }
    setRoute(path);
  };

  useEffect(() => {
    const handlePopState = () => setRoute(getCurrentPath());
    const handleUnauthorized = () => {
      clearAuthSession();
      setUser(null);
      navigate('/login', { replace: true });
    };

    window.addEventListener('popstate', handlePopState);
    window.addEventListener('auth:unauthorized', handleUnauthorized);

    return () => {
      window.removeEventListener('popstate', handlePopState);
      window.removeEventListener('auth:unauthorized', handleUnauthorized);
    };
  }, []);

  useEffect(() => {
    const token = localStorage.getItem(TOKEN_STORAGE_KEY);

    if (!token) {
      setAuthLoading(false);
      if (!['/login', '/register'].includes(route)) {
        navigate('/login', { replace: true });
      }
      return;
    }

    const hydrateUser = async () => {
      try {
        const currentUser = await getCurrentUser();
        setUser(currentUser);
        if (['/login', '/register'].includes(route)) {
          navigate('/search', { replace: true });
        }
      } catch {
        clearAuthSession();
        setUser(null);
        navigate('/login', { replace: true });
      } finally {
        setAuthLoading(false);
      }
    };

    hydrateUser();
  }, []);

  useEffect(() => {
    if (authLoading) {
      return;
    }

    const hasToken = Boolean(localStorage.getItem(TOKEN_STORAGE_KEY));

    if (!hasToken && APP_ROUTES.includes(route)) {
      navigate('/login', { replace: true });
    }

    if (hasToken && ['/login', '/register', '/'].includes(route)) {
      navigate('/search', { replace: true });
    }
  }, [route, authLoading]);

  const handleLogin = async ({ email, password }) => {
    setSubmitLoading(true);
    try {
      const payload = await loginUser(email, password);
      setAuthSession(payload.access_token, payload.user);
      setUser(payload.user);
      navigate('/search', { replace: true });
    } finally {
      setSubmitLoading(false);
    }
  };

  const handleRegister = async ({ email, password }) => {
    setSubmitLoading(true);
    try {
      const payload = await registerUser(email, password);
      setAuthSession(payload.access_token, payload.user);
      setUser(payload.user);
      navigate('/search', { replace: true });
    } finally {
      setSubmitLoading(false);
    }
  };

  const handleLogout = () => {
    clearAuthSession();
    setUser(null);
    navigate('/login', { replace: true });
  };

  const renderProtectedContent = () => {
    if (route === '/chat') {
      return <ChatPage />;
    }

    if (route === '/auto-mail') {
      return <AutoMailPage user={user} />;
    }

    return <SearchPage />;
  };

  if (authLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-950 text-white">
        <div className="rounded-3xl border border-white/10 bg-white/5 px-8 py-6 text-center shadow-xl">
          <p className="text-sm uppercase tracking-[0.35em] text-emerald-300">Loading</p>
          <h1 className="mt-3 text-2xl font-bold">Preparing your workspace</h1>
        </div>
      </div>
    );
  }

  if (route === '/login') {
    return (
      <Login
        onSubmit={handleLogin}
        onNavigateRegister={() => navigate('/register')}
        loading={submitLoading}
      />
    );
  }

  if (route === '/register') {
    return (
      <Register
        onSubmit={handleRegister}
        onNavigateLogin={() => navigate('/login')}
        loading={submitLoading}
      />
    );
  }

  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <header className="bg-gradient-to-r from-teal-700 via-emerald-700 to-teal-800 text-white shadow-lg">
        <div className="mx-auto max-w-7xl px-6 py-6">
          <div className="flex flex-col gap-6 xl:flex-row xl:items-center xl:justify-between">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.3em] text-emerald-100">Private Workspace</p>
              <h1 className="mt-2 text-4xl font-bold">Research Paper Assistant</h1>
              <p className="mt-2 text-emerald-50">Search, save, chat, and schedule digests with account-level isolation.</p>
            </div>

            <div className="flex flex-col gap-4 xl:items-end">
              <div className="rounded-2xl bg-white/10 px-4 py-3 text-sm backdrop-blur">
                <p className="text-emerald-100">Signed in as</p>
                <p className="font-semibold text-white">{user.email}</p>
              </div>

              <div className="flex flex-wrap gap-3">
                <button
                  onClick={() => navigate('/search')}
                  className={`rounded-2xl px-5 py-3 font-semibold transition ${
                    route === '/search'
                      ? 'bg-[#DECEAA] text-slate-900 shadow-lg'
                      : 'bg-white/10 text-white hover:bg-white/20'
                  }`}
                >
                  Search Papers
                </button>
                <button
                  onClick={() => navigate('/chat')}
                  className={`rounded-2xl px-5 py-3 font-semibold transition ${
                    route === '/chat'
                      ? 'bg-[#DECEAA] text-slate-900 shadow-lg'
                      : 'bg-white/10 text-white hover:bg-white/20'
                  }`}
                >
                  RAG Chat
                </button>
                <button
                  onClick={() => navigate('/auto-mail')}
                  className={`rounded-2xl px-5 py-3 font-semibold transition ${
                    route === '/auto-mail'
                      ? 'bg-[#DECEAA] text-slate-900 shadow-lg'
                      : 'bg-white/10 text-white hover:bg-white/20'
                  }`}
                >
                  Auto Mail
                </button>
                <button
                  onClick={handleLogout}
                  className="rounded-2xl border border-white/25 px-5 py-3 font-semibold text-white transition hover:bg-white/10"
                >
                  Logout
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-6 py-6">{renderProtectedContent()}</main>

      <footer className="mt-12 bg-slate-900 text-white">
        <div className="mx-auto max-w-7xl px-6 py-4 text-center text-sm text-slate-300">
          Built with React, FastAPI, Tailwind CSS, SQLAlchemy, and JWT auth.
        </div>
      </footer>
    </div>
  );
}

export default App;

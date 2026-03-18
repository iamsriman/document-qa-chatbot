import { useState } from 'react';

function Login({ onSubmit, onNavigateRegister, loading }) {
  const [form, setForm] = useState({ email: '', password: '' });
  const [errors, setErrors] = useState({});
  const [serverError, setServerError] = useState('');

  const validate = () => {
    const nextErrors = {};

    if (!form.email.trim()) {
      nextErrors.email = 'Email is required.';
    } else if (!/^\S+@\S+\.\S+$/.test(form.email)) {
      nextErrors.email = 'Enter a valid email address.';
    }

    if (!form.password) {
      nextErrors.password = 'Password is required.';
    }

    setErrors(nextErrors);
    return Object.keys(nextErrors).length === 0;
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setServerError('');

    if (!validate()) {
      return;
    }

    try {
      await onSubmit(form);
    } catch (error) {
      setServerError(error?.response?.data?.detail || 'Login failed. Please try again.');
    }
  };

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,#d8f3dc,transparent_35%),linear-gradient(135deg,#0f172a,#134e4a_55%,#ecfccb)] px-4 py-10">
      <div className="mx-auto max-w-md rounded-3xl border border-white/20 bg-white/95 p-8 shadow-2xl backdrop-blur">
        <div className="mb-8">
          <p className="text-sm font-semibold uppercase tracking-[0.3em] text-teal-700">Secure Access</p>
          <h1 className="mt-3 text-3xl font-bold text-slate-900">Sign in to Research Paper Assistant</h1>
          <p className="mt-2 text-sm text-slate-600">
            Access your saved papers, chat sessions, and auto-mail settings.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="mb-2 block text-sm font-medium text-slate-700">Email</label>
            <input
              type="email"
              value={form.email}
              onChange={(event) => setForm((current) => ({ ...current, email: event.target.value }))}
              className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 outline-none transition focus:border-teal-500 focus:bg-white focus:ring-2 focus:ring-teal-200"
              placeholder="you@example.com"
            />
            {errors.email && <p className="mt-2 text-sm text-rose-600">{errors.email}</p>}
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium text-slate-700">Password</label>
            <input
              type="password"
              value={form.password}
              onChange={(event) => setForm((current) => ({ ...current, password: event.target.value }))}
              className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 outline-none transition focus:border-teal-500 focus:bg-white focus:ring-2 focus:ring-teal-200"
              placeholder="Enter your password"
            />
            {errors.password && <p className="mt-2 text-sm text-rose-600">{errors.password}</p>}
          </div>

          {serverError && (
            <div className="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
              {serverError}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-2xl bg-slate-900 px-4 py-3 font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-400"
          >
            {loading ? 'Signing in...' : 'Login'}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-slate-600">
          New here?{' '}
          <button type="button" onClick={onNavigateRegister} className="font-semibold text-teal-700 hover:text-teal-800">
            Create an account
          </button>
        </p>
      </div>
    </div>
  );
}

export default Login;

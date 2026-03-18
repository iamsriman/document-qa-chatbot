import { useMemo, useState } from 'react';
import { enableAutoMail, getMailHistory } from '../services/api';

function AutoMailPage({ user }) {
  const [topic, setTopic] = useState('');
  const [frequency, setFrequency] = useState('daily');
  const [sendTime, setSendTime] = useState('');
  const [message, setMessage] = useState('');
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(false);

  const userEmail = useMemo(() => user?.email || '', [user]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setMessage('');

    if (!topic.trim()) {
      setMessage('Please enter a topic.');
      return;
    }

    if (!sendTime) {
      setMessage('Please choose a send time.');
      return;
    }

    setLoading(true);

    try {
      const response = await enableAutoMail({
        email: userEmail,
        topic: topic.trim(),
        frequency,
        send_time: sendTime,
      });
      setMessage(response.message);
    } catch (error) {
      setMessage(error?.response?.data?.detail || 'Something went wrong.');
    } finally {
      setLoading(false);
    }
  };

  const fetchHistory = async () => {
    if (!userEmail) {
      return;
    }

    setHistoryLoading(true);

    try {
      const data = await getMailHistory(userEmail);
      setHistory(data);
    } catch (error) {
      setMessage(error?.response?.data?.detail || 'Failed to fetch history.');
    } finally {
      setHistoryLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-100 via-white to-emerald-50 py-10">
      <div className="mx-auto max-w-3xl rounded-[28px] border border-white bg-white/90 p-8 shadow-xl">
        <div className="mb-8 flex flex-col gap-3 border-b border-slate-100 pb-6 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.25em] text-emerald-700">Auto Mail</p>
            <h2 className="mt-2 text-3xl font-bold text-slate-900">Automated research digest</h2>
            <p className="mt-2 text-sm text-slate-600">
              Receive curated paper updates tied to your logged-in account.
            </p>
          </div>
          <div className="rounded-2xl bg-slate-900 px-4 py-3 text-sm text-white">
            <p className="text-slate-300">Signed in as</p>
            <p className="font-semibold">{userEmail}</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="mb-2 block text-sm font-medium text-slate-700">Email Address</label>
            <input
              type="email"
              value={userEmail}
              readOnly
              className="w-full rounded-2xl border border-slate-200 bg-slate-100 px-4 py-3 text-slate-500 outline-none"
            />
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium text-slate-700">Research Topic</label>
            <input
              type="text"
              className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 outline-none transition focus:border-emerald-500 focus:bg-white focus:ring-2 focus:ring-emerald-200"
              placeholder="RAG, LLMs, AI Agents..."
              value={topic}
              onChange={(event) => setTopic(event.target.value)}
              required
            />
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">Frequency</label>
              <select
                className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 outline-none transition focus:border-emerald-500 focus:bg-white focus:ring-2 focus:ring-emerald-200"
                value={frequency}
                onChange={(event) => setFrequency(event.target.value)}
              >
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
              </select>
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">Send Time</label>
              <input
                type="time"
                className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 outline-none transition focus:border-emerald-500 focus:bg-white focus:ring-2 focus:ring-emerald-200"
                value={sendTime}
                onChange={(event) => setSendTime(event.target.value)}
                required
              />
            </div>
          </div>

          {message && (
            <div className="rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800">
              {message}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-2xl bg-slate-900 py-3 font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-400"
          >
            {loading ? 'Saving...' : 'Enable Auto Mail'}
          </button>
        </form>

        <button
          type="button"
          onClick={fetchHistory}
          disabled={historyLoading}
          className="mt-4 w-full rounded-2xl border border-slate-200 bg-slate-50 py-3 font-medium text-slate-900 transition hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {historyLoading ? 'Loading history...' : 'View Mail History'}
        </button>

        {history.length > 0 && (
          <div className="mt-8">
            <h3 className="mb-4 text-lg font-semibold text-slate-900">Mail History</h3>

            <div className="space-y-4">
              {history.map((item) => (
                <div
                  key={item.id}
                  className="rounded-2xl border border-slate-200 bg-slate-50 p-4"
                >
                  <h4 className="font-semibold text-slate-800">{item.subject}</h4>
                  <p className="mb-3 text-sm text-slate-500">
                    {new Date(item.created_at).toLocaleString()}
                  </p>

                  <button
                    onClick={() => window.open('', '_blank')?.document.write(item.html_content)}
                    className="rounded-xl bg-[#DECEAA] px-3 py-2 text-sm font-medium text-slate-900 transition hover:bg-[#d6c49d]"
                  >
                    View Full Digest
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default AutoMailPage;

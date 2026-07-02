import React, { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Bell, GitBranch, Layers, Radio, RefreshCcw, Send, ShieldCheck } from 'lucide-react';
import { getLogs, sendNotification } from './api/client';
import './styles.css';

const CHANNELS = ['push', 'sms', 'email', 'in-app'];
const DEFAULT_FORM = {
  eventType: 'System Warning',
  message: 'Server health dropped below the safe threshold.',
  email: 'student@example.com',
  phone: '',
  channels: ['push', 'sms', 'email'],
};

function App() {
  const [form, setForm] = useState(DEFAULT_FORM);
  const [result, setResult] = useState(null);
  const [logs, setLogs] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const selectedChannelText = useMemo(() => form.channels.join(' → '), [form.channels]);

  async function refreshLogs() {
    try {
      setLogs(await getLogs());
    } catch {
      setLogs([]);
    }
  }

  useEffect(() => {
    refreshLogs();
  }, []);

  function updateField(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  function toggleChannel(channel) {
    setForm((current) => {
      const channels = current.channels.includes(channel)
        ? current.channels.filter((item) => item !== channel)
        : [...current.channels, channel];
      return { ...current, channels };
    });
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await sendNotification(form);
      setResult(response);
      await refreshLogs();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="page-shell">
      <section className="hero-card">
        <div>
          <p className="eyebrow">Group F Ticket 2 Project Demo</p>
          <h1>Pattern-Based Notification System</h1>
          <p className="hero-text">
            This demo replaces the fragile “one big switch statement” design with Adapter, Observer,
            Decorator, and Chain of Responsibility. The trace below proves the patterns actually run.
          </p>
        </div>
        <Bell aria-hidden="true" size={52} />
      </section>

      <section className="grid-layout">
        <form className="panel" onSubmit={handleSubmit}>
          <h2>Send a Notification</h2>

          <label htmlFor="eventType">Event Type</label>
          <input
            id="eventType"
            value={form.eventType}
            onChange={(event) => updateField('eventType', event.target.value)}
          />

          <label htmlFor="message">Notification Message</label>
          <textarea
            id="message"
            value={form.message}
            onChange={(event) => updateField('message', event.target.value)}
            rows="5"
          />

          <div className="two-columns">
            <div>
              <label htmlFor="email">Email</label>
              <input
                id="email"
                placeholder="name@example.com"
                value={form.email}
                onChange={(event) => updateField('email', event.target.value)}
              />
            </div>
            <div>
              <label htmlFor="phone">Phone</label>
              <input
                id="phone"
                placeholder="+14055551234"
                value={form.phone}
                onChange={(event) => updateField('phone', event.target.value)}
              />
            </div>
          </div>

          <p className="helper-text">Fallback order: {selectedChannelText || 'none selected'}</p>
          <div className="channel-list" aria-label="Notification channels">
            {CHANNELS.map((channel) => (
              <button
                type="button"
                key={channel}
                className={form.channels.includes(channel) ? 'channel active' : 'channel'}
                onClick={() => toggleChannel(channel)}
              >
                {channel}
              </button>
            ))}
          </div>

          <button className="primary-button" disabled={loading}>
            <Send aria-hidden="true" size={18} />
            {loading ? 'Sending...' : 'Run Pattern Demo'}
          </button>

          {error && <p className="error">{error}</p>}
        </form>

        <section className="panel explanation-panel">
          <h2>What the evaluator can see</h2>
          <PatternRow icon={<Layers />} title="Adapter" text="Each vendor-style channel is behind the same send(message) interface." />
          <PatternRow icon={<Radio />} title="Observer" text="Subscribers react when the notification event fires." />
          <PatternRow icon={<RefreshCcw />} title="Decorator" text="Logging and retry wrap the channels instead of being copied into each branch." />
          <PatternRow icon={<GitBranch />} title="Chain of Responsibility" text="Channels are tried in order until one succeeds." />
          <PatternRow icon={<ShieldCheck />} title="GRASP" text="Polymorphism, low coupling, and protected variations keep the design maintainable." />
        </section>
      </section>

      {result && (
        <section className="panel result-panel">
          <h2>Latest Result</h2>
          <p><strong>Status:</strong> {result.status}</p>
          <p><strong>Winning Channel:</strong> {result.winningChannel}</p>
          <p><strong>Detail:</strong> {result.detail}</p>
          <Trace trace={result.trace} />
        </section>
      )}

      <section className="panel">
        <h2>Notification History</h2>
        {logs.length === 0 ? (
          <p>No notifications have been sent yet.</p>
        ) : (
          logs.map((log) => (
            <article className="log-card" key={log.id}>
              <div>
                <strong>{log.eventType}</strong>
                <p>{log.message}</p>
              </div>
              <span>{log.status} through {log.channels}</span>
            </article>
          ))
        )}
      </section>
    </main>
  );
}

function PatternRow({ icon, title, text }) {
  return (
    <div className="pattern-row">
      <span aria-hidden="true">{icon}</span>
      <div>
        <strong>{title}</strong>
        <p>{text}</p>
      </div>
    </div>
  );
}

function Trace({ trace }) {
  return (
    <ol className="trace-list">
      {trace.map((item, index) => (
        <li key={`${item}-${index}`}>{item}</li>
      ))}
    </ol>
  );
}

createRoot(document.getElementById('root')).render(<App />);

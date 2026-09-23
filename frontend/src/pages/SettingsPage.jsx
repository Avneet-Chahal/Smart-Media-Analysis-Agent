import React, { useState, useEffect } from 'react';
import { ArrowLeft, Brain, LayoutDashboard, LogOut } from 'lucide-react';
import ProfileSettings from '../components/ProfileSettings';
import apiService from '../services/api';

export default function SettingsPage({ currentUser = null, onGoHome, onLaunchApp, onLogout }) {
  const [documents, setDocuments] = useState([]);
  const [health, setHealth] = useState(null);

  useEffect(() => {
    apiService
      .listDocuments()
      .then((docs) => setDocuments(docs))
      .catch((err) => console.error('Failed to load documents for settings:', err));

    apiService
      .getHealth()
      .then((h) => setHealth(h))
      .catch((err) => console.error('Failed to load health for settings:', err));
  }, []);

  return (
    <div className="app-container" style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Top Navbar */}
      <header className="glass-panel navbar" style={{ padding: '12px 20px', marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div
            className="brand-icon"
            onClick={onLaunchApp || onGoHome}
            style={{ cursor: 'pointer', width: '38px', height: '38px' }}
            title="Return to Workspace"
          >
            <Brain size={20} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <h1 className="brand-title" style={{ fontSize: '1.05rem', margin: 0 }}>
                Smart Media Analysis Agent
              </h1>
              <span className="badge badge-violet" style={{ fontSize: '0.66rem', padding: '2px 7px' }}>
                Settings
              </span>
            </div>
            <p className="brand-subtitle" style={{ fontSize: '0.72rem', margin: 0 }}>
              Profile, System Preferences & Privacy
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          {onLaunchApp && (
            <button
              onClick={onLaunchApp}
              className="btn-primary"
              style={{ padding: '6px 14px', fontSize: '0.8rem', gap: '6px' }}
            >
              <LayoutDashboard size={14} />
              <span>Open Workspace</span>
            </button>
          )}

          {onGoHome && (
            <button
              onClick={onGoHome}
              className="btn-secondary"
              style={{ padding: '6px 12px', fontSize: '0.8rem', gap: '5px' }}
            >
              <ArrowLeft size={13} />
              <span>Landing Page</span>
            </button>
          )}

          {onLogout && (
            <button
              onClick={onLogout}
              className="btn-secondary"
              style={{ padding: '6px 12px', fontSize: '0.8rem', gap: '5px', color: '#FDA4AF' }}
              title="Sign Out"
            >
              <LogOut size={13} />
              <span>Sign Out</span>
            </button>
          )}
        </div>
      </header>

      {/* Main Settings Body */}
      <main style={{ flex: 1, display: 'flex', alignItems: 'flex-start', justifyContent: 'center', paddingBottom: '32px' }}>
        <ProfileSettings
          currentUser={currentUser}
          documents={documents}
          health={health}
          onClose={onLaunchApp || onGoHome}
          onLogout={onLogout}
        />
      </main>
    </div>
  );
}

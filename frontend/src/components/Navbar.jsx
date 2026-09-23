import React from 'react';
import { Sparkles, Brain, Cpu, FileText, Film, Music, ArrowLeft, User, ShieldCheck, Zap } from 'lucide-react';

export default function Navbar({ health, activeDocument, onGoHome, onOpenSettings }) {
  const getDocIcon = (type) => {
    switch (type) {
      case 'video':
        return <Film size={13} color="#EC4899" />;
      case 'audio':
        return <Music size={13} color="#06B6D4" />;
      default:
        return <FileText size={13} color="#818CF8" />;
    }
  };

  return (
    <header className="glass-panel navbar" style={{ padding: '12px 20px' }}>
      {/* LEFT: Logo & Brand Identity */}
      <div className="brand-section" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div
          className="brand-icon"
          onClick={onGoHome}
          style={{ cursor: onGoHome ? 'pointer' : 'default', width: '38px', height: '38px' }}
          title={onGoHome ? 'Return to Landing Page' : undefined}
        >
          <Brain size={20} />
        </div>
        <div
          onClick={onGoHome}
          style={{ cursor: onGoHome ? 'pointer' : 'default' }}
          title={onGoHome ? 'Return to Landing Page' : undefined}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
            <h1 className="brand-title" style={{ fontSize: '1.02rem', margin: 0 }}>
              Smart Media Analysis Agent
            </h1>
            <span
              className="badge badge-violet"
              style={{
                fontSize: '0.66rem',
                padding: '2px 8px',
                fontWeight: 700,
                letterSpacing: '0.04em',
              }}
            >
              Enterprise AI
            </span>
          </div>
          <p className="brand-subtitle" style={{ fontSize: '0.72rem', margin: 0 }}>
            Multimodal Educational Content Intelligence Platform
          </p>
        </div>
      </div>

      {/* CENTER: Current Active Document Pill */}
      <div className="navbar-center-doc">
        {activeDocument ? (
          <div
            className="infra-chip active-doc-pill"
            style={{
              maxWidth: '320px',
              border: '1px solid rgba(124, 58, 237, 0.4)',
              background: 'rgba(124, 58, 237, 0.1)',
              padding: '6px 14px',
              boxShadow: '0 0 16px rgba(124, 58, 237, 0.15)',
            }}
            title={activeDocument.filename}
          >
            {getDocIcon(activeDocument.media_type)}
            <span style={{ color: 'var(--color-dim)', fontSize: '0.72rem', fontWeight: 600 }}>
              ACTIVE:
            </span>
            <span
              style={{
                fontWeight: 600,
                color: '#ffffff',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
                maxWidth: '180px',
                fontSize: '0.78rem',
              }}
            >
              {activeDocument.filename}
            </span>
          </div>
        ) : (
          <div
            className="infra-chip"
            style={{
              border: '1px dashed var(--border-glass-light)',
              background: 'rgba(255, 255, 255, 0.02)',
              color: 'var(--color-dim)',
              fontSize: '0.74rem',
            }}
          >
            <span style={{ opacity: 0.6 }}>No document selected</span>
          </div>
        )}
      </div>

      {/* RIGHT: Status Badges & Profile */}
      <div
        className="navbar-status-badges"
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          flexWrap: 'wrap',
        }}
      >
        {/* Workspace Ready Status */}
        <div
          className="infra-chip"
          style={{
            border: '1px solid rgba(16, 185, 129, 0.3)',
            background: 'rgba(16, 185, 129, 0.08)',
            padding: '5px 11px',
            fontSize: '0.72rem',
          }}
          title="Multimodal Intelligence Core Ready"
        >
          <div className="pulse-dot-emerald" style={{ width: '6px', height: '6px' }} />
          <span style={{ color: '#6EE7B7', fontWeight: 600 }}>
            Workspace Ready
          </span>
        </div>

        {/* Grounded AI Status */}
        <div
          className="infra-chip"
          style={{
            border: '1px solid rgba(99, 102, 241, 0.3)',
            background: 'rgba(99, 102, 241, 0.08)',
            padding: '5px 11px',
            fontSize: '0.72rem',
          }}
          title="Zero-Hallucination Grounded Content Pipeline"
        >
          <Cpu size={12} color="#A5B4FC" />
          <span
            style={{
              color: '#C7D2FE',
              fontWeight: 600,
            }}
          >
            Grounded AI
          </span>
        </div>

        {/* Return to Landing Page Button */}
        {onGoHome && (
          <button
            onClick={onGoHome}
            className="btn-secondary"
            style={{ padding: '5px 11px', fontSize: '0.76rem', gap: '5px' }}
            title="Return to Landing Page"
          >
            <ArrowLeft size={12} />
            <span>Home</span>
          </button>
        )}

        {/* User Profile & Settings Trigger */}
        <div
          onClick={onOpenSettings}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '3px 10px 3px 4px',
            borderRadius: '20px',
            background: 'rgba(255, 255, 255, 0.04)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            cursor: onOpenSettings ? 'pointer' : 'default',
            transition: 'all var(--transition-fast)',
          }}
          onMouseEnter={(e) => {
            if (onOpenSettings) {
              e.currentTarget.style.background = 'rgba(124, 58, 237, 0.18)';
              e.currentTarget.style.borderColor = 'rgba(124, 58, 237, 0.4)';
            }
          }}
          onMouseLeave={(e) => {
            if (onOpenSettings) {
              e.currentTarget.style.background = 'rgba(255, 255, 255, 0.04)';
              e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.1)';
            }
          }}
          title="Open Profile & Settings"
        >
          <div
            style={{
              width: '26px',
              height: '26px',
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #7C3AED 0%, #6366F1 100%)',
              border: '1px solid rgba(255, 255, 255, 0.2)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#fff',
              fontSize: '0.7rem',
              fontWeight: 700,
              boxShadow: '0 2px 8px rgba(124, 58, 237, 0.3)',
            }}
          >
            AK
          </div>
          <span style={{ fontSize: '0.74rem', color: '#E2E8F0', fontWeight: 600 }}>
            Profile & Settings
          </span>
        </div>
      </div>
    </header>
  );
}

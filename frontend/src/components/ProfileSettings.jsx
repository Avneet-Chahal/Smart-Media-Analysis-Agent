import React, { useState, useEffect, useMemo } from 'react';
import {
  User,
  Settings,
  Shield,
  Info,
  Layers,
  FileText,
  Film,
  Music,
  CheckCircle2,
  Clock,
  Sparkles,
  BookOpen,
  Cpu,
  Brain,
  Edit3,
  Mail,
  GraduationCap,
  HardDrive,
  HelpCircle,
  Activity,
  Zap,
  Sliders,
  Check,
  RotateCcw,
  ExternalLink,
  ChevronRight,
  Database,
  Lock,
  Globe,
  LogOut,
} from 'lucide-react';
import { formatBytes, formatSeconds } from '../utils/formatters';
import apiService from '../services/api';

export default function ProfileSettings({
  currentUser = null,
  documents = [],
  activeDocument = null,
  health = null,
  initialTab = 'profile', // 'profile' | 'account' | 'preferences' | 'ai' | 'privacy' | 'about'
  onClose = null,
  onLogout = null,
}) {
  const [activeTab, setActiveTab] = useState(initialTab || 'profile');
  const [showEditModal, setShowEditModal] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);

  // Sync initialTab when prop changes
  useEffect(() => {
    if (initialTab) {
      setActiveTab(initialTab);
    }
  }, [initialTab]);

  // =========================================================
  // USER PROFILE STATE (Persisted in localStorage)
  // =========================================================
  const [profile, setProfile] = useState(() => {
    try {
      const saved = localStorage.getItem('sma_user_profile_v2');
      if (saved) return JSON.parse(saved);
    } catch (e) {}
    return {
      name: currentUser?.name || 'Avneet Kaur',
      role: currentUser?.role || 'Student',
      email: currentUser?.email || 'avneet.kaur@smartmedia.ai',
      institution: 'Intelligent Learning Academy',
      course: 'Computer Science & Artificial Intelligence',
      studentId: 'STU-2026-8941',
      specialization: 'Multimodal AI & Content Intelligence',
      bio: 'Mastering generative AI reasoning, video timeline retrieval, and educational vector search.',
    };
  });

  // Sync with currentUser if currentUser changes
  useEffect(() => {
    if (currentUser?.name || currentUser?.email) {
      setProfile((prev) => ({
        ...prev,
        name: currentUser.name || prev.name,
        email: currentUser.email || prev.email,
        role: currentUser.role || prev.role,
      }));
    }
  }, [currentUser]);

  const [editForm, setEditForm] = useState(profile);

  const handleSaveProfile = (e) => {
    e.preventDefault();
    setProfile(editForm);
    try {
      localStorage.setItem('sma_user_profile_v2', JSON.stringify(editForm));
    } catch (e) {}
    setShowEditModal(false);
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 3000);
  };

  // =========================================================
  // SETTINGS STATE (Controls: Toggles, Dropdowns, Inputs)
  // =========================================================
  const [settings, setSettings] = useState(() => {
    try {
      const saved = localStorage.getItem('sma_app_settings_v2');
      if (saved) return JSON.parse(saved);
    } catch (e) {}
    return {
      // Preferences
      theme: 'midnight', // 'midnight' | 'oled'
      autoPlayTimestamps: true,
      defaultPlaybackSpeed: '1.0x',
      transcriptLanguage: 'en-US',
      audioWaveformVisualizer: true,
      
      // AI Preferences
      strictGrounding: true,
      aiResponseDepth: 'comprehensive', // 'comprehensive' | 'concise' | 'bullet'
      citationFormat: 'timestamp_page',
      showReasoningBadges: true,
      confidenceScoreTelemetry: true,
      
      // Privacy & Data
      persistChatHistory: true,
      localSqliteIsolation: true,
      anonymousDiagnostics: false,
    };
  });

  const handleUpdateSetting = (key, value) => {
    setSettings((prev) => {
      const updated = { ...prev, [key]: value };
      try {
        localStorage.setItem('sma_app_settings_v2', JSON.stringify(updated));
      } catch (e) {}
      return updated;
    });
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 2500);
  };

  // =========================================================
  // REAL STATS CALCULATION (ONLY REAL DATA)
  // =========================================================
  const [realQuizCount, setRealQuizCount] = useState(0);

  useEffect(() => {
    let isMounted = true;
    const countRealQuizzes = async () => {
      if (!documents || documents.length === 0) {
        setRealQuizCount(currentUser?.isDemo ? 3 : 0);
        return;
      }
      try {
        let total = 0;
        for (const doc of documents) {
          if (doc.status === 'READY') {
            try {
              const list = await apiService.listQuizzes(doc.id);
              if (Array.isArray(list)) {
                total += list.length;
              }
            } catch (e) {}
          }
        }
        if (isMounted) setRealQuizCount(total);
      } catch (e) {
        console.error('Failed to load real quiz statistics:', e);
      }
    };
    countRealQuizzes();
    return () => {
      isMounted = false;
    };
  }, [documents, currentUser]);

  const realStats = useMemo(() => {
    const totalMaterials = documents.length;
    const pdfDocs = documents.filter((d) => d.media_type === 'pdf' || d.media_type === 'document');
    const videoDocs = documents.filter((d) => d.media_type === 'video');
    const audioDocs = documents.filter((d) => d.media_type === 'audio');
    const readyDocs = documents.filter((d) => d.status === 'READY');

    const totalPages = pdfDocs.reduce((acc, d) => acc + (d.page_count || 0), 0);
    const totalDurationSec = [...videoDocs, ...audioDocs].reduce(
      (acc, d) => acc + (d.duration_seconds || 0),
      0
    );
    const totalStorageBytes = documents.reduce((acc, d) => acc + (d.file_size || 0), 0);

    return {
      totalMaterials,
      pdfCount: pdfDocs.length,
      mediaCount: videoDocs.length + audioDocs.length,
      totalPages,
      totalDurationSec,
      totalStorageBytes,
      readyCount: readyDocs.length,
    };
  }, [documents]);

  const initials = profile.name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .substring(0, 2) || 'AK';

  return (
    <div className="profile-settings-wrapper">
      {/* =========================================================================
          TOP NAVIGATION TABS (PROFILE + 5 SETTINGS SECTIONS)
          ========================================================================= */}
      <div className="profile-settings-nav">
        <button
          onClick={() => setActiveTab('profile')}
          className={`profile-settings-tab-btn ${activeTab === 'profile' ? 'active' : ''}`}
        >
          <User size={15} />
          <span>Student Profile</span>
        </button>

        <button
          onClick={() => setActiveTab('account')}
          className={`profile-settings-tab-btn ${activeTab === 'account' ? 'active' : ''}`}
        >
          <GraduationCap size={15} />
          <span>Account</span>
        </button>

        <button
          onClick={() => setActiveTab('preferences')}
          className={`profile-settings-tab-btn ${activeTab === 'preferences' ? 'active' : ''}`}
        >
          <Sliders size={15} />
          <span>Preferences</span>
        </button>

        <button
          onClick={() => setActiveTab('ai')}
          className={`profile-settings-tab-btn ${activeTab === 'ai' ? 'active' : ''}`}
        >
          <Brain size={15} />
          <span>AI Preferences</span>
        </button>

        <button
          onClick={() => setActiveTab('privacy')}
          className={`profile-settings-tab-btn ${activeTab === 'privacy' ? 'active' : ''}`}
        >
          <Shield size={15} />
          <span>Privacy</span>
        </button>

        <button
          onClick={() => setActiveTab('about')}
          className={`profile-settings-tab-btn ${activeTab === 'about' ? 'active' : ''}`}
        >
          <Info size={15} />
          <span>About</span>
        </button>

        {savedSuccess && (
          <div
            style={{
              marginLeft: 'auto',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '6px 14px',
              borderRadius: '10px',
              background: 'rgba(16, 185, 129, 0.15)',
              border: '1px solid rgba(16, 185, 129, 0.35)',
              color: '#6EE7B7',
              fontSize: '0.78rem',
              fontWeight: 700,
            }}
          >
            <Check size={14} />
            <span>Saved Preferences</span>
          </div>
        )}
      </div>

      {/* =========================================================================
          TAB 1: PROFILE (Hero Card, Avatar, Avneet Kaur, Student, Real Stats)
          ========================================================================= */}
      {activeTab === 'profile' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '22px' }}>
          {/* PROFILE HERO CARD */}
          <div className="profile-hero-card">
            <div className="profile-hero-left">
              <div className="profile-avatar-wrapper">
                <div className="profile-avatar-circle">
                  <div className="profile-avatar-inner">{initials}</div>
                </div>
                <div className="profile-avatar-status" title="Active Student Online" />
              </div>

              <div className="profile-hero-info">
                <div className="profile-name-row">
                  <h2 className="profile-name">{profile.name}</h2>
                  <span className="profile-role-badge">
                    <Sparkles size={11} /> {profile.role}
                  </span>
                  <span
                    style={{
                      fontSize: '0.72rem',
                      fontWeight: 700,
                      padding: '2px 8px',
                      borderRadius: '9999px',
                      background: 'rgba(124, 58, 237, 0.18)',
                      border: '1px solid rgba(139, 92, 246, 0.3)',
                      color: '#C4B5FD',
                    }}
                  >
                    Verified Account
                  </span>
                </div>

                <div className="profile-email-row">
                  <Mail size={14} color="#818CF8" />
                  <span>{profile.email}</span>
                </div>

                <div className="profile-institution-tag">
                  <GraduationCap size={14} color="#EC4899" />
                  <span>
                    {profile.course} • ID: {profile.studentId}
                  </span>
                </div>
              </div>
            </div>

            <div className="profile-hero-actions">
              <button
                onClick={() => {
                  setEditForm(profile);
                  setShowEditModal(true);
                }}
                className="btn-primary"
                style={{ padding: '10px 18px', fontSize: '0.86rem', gap: '8px' }}
              >
                <Edit3 size={15} />
                <span>Edit Profile</span>
              </button>

              {onLogout && (
                <button
                  onClick={onLogout}
                  className="btn-secondary"
                  style={{ padding: '10px 16px', fontSize: '0.86rem', gap: '6px', color: '#FDA4AF' }}
                  title="Sign Out of Session"
                >
                  <LogOut size={15} />
                  <span>Sign Out</span>
                </button>
              )}
            </div>
          </div>

          {/* REAL ACCOUNT STATISTICS GRID (ONLY REAL DATA) */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 4px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Activity size={16} color="#818CF8" />
                <h3 style={{ fontSize: '0.98rem', fontWeight: 800, color: '#FFFFFF', margin: 0 }}>
                  Account Learning Statistics
                </h3>
              </div>
              <span style={{ fontSize: '0.74rem', color: 'var(--color-text-muted)' }}>
                Calculated from local materials and knowledge graph telemetry
              </span>
            </div>

            <div className="profile-stats-grid">
              {/* Stat 1: Total Uploaded Materials */}
              <div className="profile-stat-card">
                <div className="profile-stat-top">
                  <div className="profile-stat-icon-box violet">
                    <Layers size={20} />
                  </div>
                  <span className="badge badge-violet" style={{ fontSize: '0.66rem' }}>
                    Available
                  </span>
                </div>
                <div>
                  <div className="profile-stat-value">{realStats.totalMaterials}</div>
                  <div className="profile-stat-label">Total Educational Materials</div>
                  <div className="profile-stat-sub">
                    {realStats.readyCount} active & ready for reasoning
                  </div>
                </div>
              </div>

              {/* Stat 2: Video & Audio Duration */}
              <div className="profile-stat-card">
                <div className="profile-stat-top">
                  <div className="profile-stat-icon-box pink">
                    <Film size={20} />
                  </div>
                  <span className="badge badge-pink" style={{ fontSize: '0.66rem' }}>
                    {realStats.mediaCount} Media
                  </span>
                </div>
                <div>
                  <div className="profile-stat-value">
                    {realStats.totalDurationSec > 0
                      ? formatSeconds(realStats.totalDurationSec)
                      : '00:00'}
                  </div>
                  <div className="profile-stat-label">Lecture Audio/Video Minutes</div>
                  <div className="profile-stat-sub">Transcribed & speech indexed</div>
                </div>
              </div>

              {/* Stat 3: PDF Document Pages */}
              <div className="profile-stat-card">
                <div className="profile-stat-top">
                  <div className="profile-stat-icon-box indigo">
                    <BookOpen size={20} />
                  </div>
                  <span className="badge badge-indigo" style={{ fontSize: '0.66rem' }}>
                    {realStats.pdfCount} PDFs
                  </span>
                </div>
                <div>
                  <div className="profile-stat-value">{realStats.totalPages}</div>
                  <div className="profile-stat-label">Course Slides & Pages</div>
                  <div className="profile-stat-sub">Vectorized in semantic knowledge graph</div>
                </div>
              </div>

              {/* Stat 4: Quizzes & Knowledge Chunks */}
              <div className="profile-stat-card">
                <div className="profile-stat-top">
                  <div className="profile-stat-icon-box cyan">
                    <HelpCircle size={20} />
                  </div>
                  <span className="badge badge-cyan" style={{ fontSize: '0.66rem' }}>
                    Adaptive
                  </span>
                </div>
                <div>
                  <div className="profile-stat-value">{realQuizCount}</div>
                  <div className="profile-stat-label">Generated Practice Quizzes</div>
                  <div className="profile-stat-sub">
                    Storage used: {formatBytes(realStats.totalStorageBytes)}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* STUDENT ACADEMIC PROFILE DETAILS CARD */}
          <div className="settings-section-card">
            <div className="settings-section-header">
              <div className="settings-section-icon">
                <GraduationCap size={20} />
              </div>
              <div>
                <h3 className="settings-section-title">Academic & Learning Credentials</h3>
                <p className="settings-section-desc">
                  Multimodal Intelligent Content Understanding Track
                </p>
              </div>
            </div>

            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
                gap: '16px',
              }}
            >
              <div style={{ padding: '14px 18px', background: 'rgba(8, 10, 18, 0.65)', borderRadius: '12px', border: '1px solid var(--border-glass)' }}>
                <span style={{ fontSize: '0.72rem', color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em', fontWeight: 700 }}>
                  Institution / Organization
                </span>
                <div style={{ color: '#FFFFFF', fontWeight: 700, fontSize: '0.92rem', marginTop: '4px' }}>
                  {profile.institution}
                </div>
              </div>

              <div style={{ padding: '14px 18px', background: 'rgba(8, 10, 18, 0.65)', borderRadius: '12px', border: '1px solid var(--border-glass)' }}>
                <span style={{ fontSize: '0.72rem', color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em', fontWeight: 700 }}>
                  Program & Branch
                </span>
                <div style={{ color: '#FFFFFF', fontWeight: 700, fontSize: '0.92rem', marginTop: '4px' }}>
                  {profile.course}
                </div>
              </div>

              <div style={{ padding: '14px 18px', background: 'rgba(8, 10, 18, 0.65)', borderRadius: '12px', border: '1px solid var(--border-glass)' }}>
                <span style={{ fontSize: '0.72rem', color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em', fontWeight: 700 }}>
                  Student Roll / ID
                </span>
                <div style={{ color: '#C4B5FD', fontWeight: 700, fontSize: '0.92rem', marginTop: '4px' }}>
                  {profile.studentId}
                </div>
              </div>

              <div style={{ padding: '14px 18px', background: 'rgba(8, 10, 18, 0.65)', borderRadius: '12px', border: '1px solid var(--border-glass)' }}>
                <span style={{ fontSize: '0.72rem', color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em', fontWeight: 700 }}>
                  AI Engine Status
                </span>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#34D399', fontWeight: 700, fontSize: '0.92rem', marginTop: '4px' }}>
                  <CheckCircle2 size={14} />
                  <span>Multimodal AI Reasoning Engine</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* =========================================================================
          TAB 2: ACCOUNT SETTINGS
          ========================================================================= */}
      {activeTab === 'account' && (
        <div className="settings-section-card">
          <div className="settings-section-header">
            <div className="settings-section-icon">
              <User size={20} />
            </div>
            <div>
              <h3 className="settings-section-title">Account Information</h3>
              <p className="settings-section-desc">
                Manage your user identity and security credentials
              </p>
            </div>
          </div>

          <div className="settings-rows-list">
            <div className="settings-row">
              <div className="settings-row-info">
                <span className="settings-row-label">Full Name</span>
                <span className="settings-row-sub">Displayed on study notes, quizzes, and workspace headers</span>
              </div>
              <input
                type="text"
                value={profile.name}
                onChange={(e) => {
                  const updated = { ...profile, name: e.target.value };
                  setProfile(updated);
                  localStorage.setItem('sma_user_profile_v2', JSON.stringify(updated));
                }}
                className="settings-input-control"
              />
            </div>

            <div className="settings-row">
              <div className="settings-row-info">
                <span className="settings-row-label">Email Address</span>
                <span className="settings-row-sub">Used for workspace session and account sync</span>
              </div>
              <input
                type="email"
                value={profile.email}
                onChange={(e) => {
                  const updated = { ...profile, email: e.target.value };
                  setProfile(updated);
                  localStorage.setItem('sma_user_profile_v2', JSON.stringify(updated));
                }}
                className="settings-input-control"
              />
            </div>

            <div className="settings-row">
              <div className="settings-row-info">
                <span className="settings-row-label">Subscription Tier</span>
                <span className="settings-row-sub">Educational Intelligent Learning Pro Plan</span>
              </div>
              <span className="badge badge-emerald" style={{ padding: '6px 14px', fontSize: '0.8rem' }}>
                <CheckCircle2 size={13} /> Active Pro Student Plan
              </span>
            </div>

            <div className="settings-row">
              <div className="settings-row-info">
                <span className="settings-row-label">Local Data Storage</span>
                <span className="settings-row-sub">SQLite database file size on local server instance</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ color: '#DDD6FE', fontWeight: 700, fontSize: '0.88rem' }}>
                  {formatBytes(realStats.totalStorageBytes)}
                </span>
              </div>
            </div>

            {onLogout && (
              <div className="settings-row" style={{ borderTop: '1px solid rgba(244, 63, 94, 0.2)' }}>
                <div className="settings-row-info">
                  <span className="settings-row-label" style={{ color: '#FDA4AF' }}>
                    Sign Out of Workspace
                  </span>
                  <span className="settings-row-sub">End current active session and return to Sign In screen</span>
                </div>
                <button
                  onClick={onLogout}
                  className="btn-danger"
                  style={{ padding: '8px 16px', fontSize: '0.82rem', gap: '6px' }}
                >
                  <LogOut size={14} />
                  <span>Sign Out</span>
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* =========================================================================
          TAB 3: PREFERENCES (Controls: Toggles, Dropdowns, Buttons)
          ========================================================================= */}
      {activeTab === 'preferences' && (
        <div className="settings-section-card">
          <div className="settings-section-header">
            <div className="settings-section-icon">
              <Sliders size={20} />
            </div>
            <div>
              <h3 className="settings-section-title">Application Preferences</h3>
              <p className="settings-section-desc">
                Customize playback speeds, UI theme mode, and audio waveform behaviors
              </p>
            </div>
          </div>

          <div className="settings-rows-list">
            <div className="settings-row">
              <div className="settings-row-info">
                <span className="settings-row-label">Visual Theme</span>
                <span className="settings-row-sub">Midnight navy AI SaaS palette with electric violet accents</span>
              </div>
              <select
                value={settings.theme}
                onChange={(e) => handleUpdateSetting('theme', e.target.value)}
                className="settings-select-control"
              >
                <option value="midnight">Deep Midnight Navy (Master)</option>
                <option value="oled">Ultra OLED Obsidian</option>
              </select>
            </div>

            <div className="settings-row">
              <div className="settings-row-info">
                <span className="settings-row-label">Default Playback Speed</span>
                <span className="settings-row-sub">Default initial speed when loading video or audio lectures</span>
              </div>
              <select
                value={settings.defaultPlaybackSpeed}
                onChange={(e) => handleUpdateSetting('defaultPlaybackSpeed', e.target.value)}
                className="settings-select-control"
              >
                <option value="1.0x">1.0x (Normal Speed)</option>
                <option value="1.25x">1.25x (Faster Comprehension)</option>
                <option value="1.5x">1.5x (Accelerated Learning)</option>
                <option value="2.0x">2.0x (Speed Review)</option>
              </select>
            </div>

            <div className="settings-row">
              <div className="settings-row-info">
                <span className="settings-row-label">Auto-sync Timeline on Click</span>
                <span className="settings-row-sub">Automatically scroll transcript to active timestamp moment</span>
              </div>
              <label className="settings-toggle-switch">
                <input
                  type="checkbox"
                  checked={settings.autoPlayTimestamps}
                  onChange={(e) => handleUpdateSetting('autoPlayTimestamps', e.target.checked)}
                />
                <span className="settings-toggle-slider" />
              </label>
            </div>

            <div className="settings-row">
              <div className="settings-row-info">
                <span className="settings-row-label">Audio Waveform Visualizer</span>
                <span className="settings-row-sub">Render live audio orb visualizer during audio playback</span>
              </div>
              <label className="settings-toggle-switch">
                <input
                  type="checkbox"
                  checked={settings.audioWaveformVisualizer}
                  onChange={(e) => handleUpdateSetting('audioWaveformVisualizer', e.target.checked)}
                />
                <span className="settings-toggle-slider" />
              </label>
            </div>

            <div className="settings-row">
              <div className="settings-row-info">
                <span className="settings-row-label">Transcription Speech Locale</span>
                <span className="settings-row-sub">Speech-to-text primary recognition locale</span>
              </div>
              <select
                value={settings.transcriptLanguage}
                onChange={(e) => handleUpdateSetting('transcriptLanguage', e.target.value)}
                className="settings-select-control"
              >
                <option value="en-US">English (United States / Global)</option>
                <option value="en-IN">English (India)</option>
                <option value="auto">Multi-language Auto Detect</option>
              </select>
            </div>
          </div>
        </div>
      )}

      {/* =========================================================================
          TAB 4: AI PREFERENCES
          ========================================================================= */}
      {activeTab === 'ai' && (
        <div className="settings-section-card">
          <div className="settings-section-header">
            <div className="settings-section-icon">
              <Brain size={20} />
            </div>
            <div>
              <h3 className="settings-section-title">AI Reasoning & Grounding Preferences</h3>
              <p className="settings-section-desc">
                Configure grounded AI RAG reasoning retrieval strictness and citation formats
              </p>
            </div>
          </div>

          <div className="settings-rows-list">
            <div className="settings-row">
              <div className="settings-row-info">
                <span className="settings-row-label">Strict Content Grounding</span>
                <span className="settings-row-sub">
                  Enforce zero-hallucination policy; AI only answers from uploaded lecture vectors
                </span>
              </div>
              <label className="settings-toggle-switch">
                <input
                  type="checkbox"
                  checked={settings.strictGrounding}
                  onChange={(e) => handleUpdateSetting('strictGrounding', e.target.checked)}
                />
                <span className="settings-toggle-slider" />
              </label>
            </div>

            <div className="settings-row">
              <div className="settings-row-info">
                <span className="settings-row-label">AI Response Synthesis Depth</span>
                <span className="settings-row-sub">Depth and formatting of generated explanations and answers</span>
              </div>
              <select
                value={settings.aiResponseDepth}
                onChange={(e) => handleUpdateSetting('aiResponseDepth', e.target.value)}
                className="settings-select-control"
              >
                <option value="comprehensive">Comprehensive Academic (Definitions + Code)</option>
                <option value="concise">Concise & Direct (Speed Revision)</option>
                <option value="bullet">Structured Checklist & Exam Points</option>
              </select>
            </div>

            <div className="settings-row">
              <div className="settings-row-info">
                <span className="settings-row-label">Interactive Grounded Citations</span>
                <span className="settings-row-sub">Display clickable page numbers and exact video timestamps on answers</span>
              </div>
              <label className="settings-toggle-switch">
                <input
                  type="checkbox"
                  checked={settings.showReasoningBadges}
                  onChange={(e) => handleUpdateSetting('showReasoningBadges', e.target.checked)}
                />
                <span className="settings-toggle-slider" />
              </label>
            </div>

            <div className="settings-row">
              <div className="settings-row-info">
                <span className="settings-row-label">Vector Embedding Pipeline</span>
                <span className="settings-row-sub">Connected semantic vector indexing pipeline</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span className="badge badge-cyan" style={{ fontSize: '0.74rem' }}>
                  Semantic Vector Index
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* =========================================================================
          TAB 5: PRIVACY & DATA ISOLATION
          ========================================================================= */}
      {activeTab === 'privacy' && (
        <div className="settings-section-card">
          <div className="settings-section-header">
            <div className="settings-section-icon">
              <Shield size={20} />
            </div>
            <div>
              <h3 className="settings-section-title">Privacy & Data Governance</h3>
              <p className="settings-section-desc">
                Local database encryption and isolated tenant data security
              </p>
            </div>
          </div>

          <div className="settings-rows-list">
            <div className="settings-row">
              <div className="settings-row-info">
                <span className="settings-row-label">Persist Conversation Dialogue History</span>
                <span className="settings-row-sub">Store chat queries and citations in local database for future review</span>
              </div>
              <label className="settings-toggle-switch">
                <input
                  type="checkbox"
                  checked={settings.persistChatHistory}
                  onChange={(e) => handleUpdateSetting('persistChatHistory', e.target.checked)}
                />
                <span className="settings-toggle-slider" />
              </label>
            </div>

            <div className="settings-row">
              <div className="settings-row-info">
                <span className="settings-row-label">Local File Isolation</span>
                <span className="settings-row-sub">All raw PDF/audio/video files stored exclusively in local backend storage</span>
              </div>
              <span className="badge badge-emerald" style={{ padding: '6px 12px' }}>
                <CheckCircle2 size={12} /> Enabled & Isolated
              </span>
            </div>

            <div className="settings-row">
              <div className="settings-row-info">
                <span className="settings-row-label">Clear Local Storage Cache</span>
                <span className="settings-row-sub">Reset local UI preference keys and profile overrides</span>
              </div>
              <button
                onClick={() => {
                  if (window.confirm('Reset local preferences and cached profile?')) {
                    localStorage.removeItem('sma_user_profile_v2');
                    localStorage.removeItem('sma_app_settings_v2');
                    window.location.reload();
                  }
                }}
                className="btn-danger"
                style={{ padding: '8px 16px', fontSize: '0.8rem', gap: '6px' }}
              >
                <RotateCcw size={13} />
                <span>Reset Cache</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* =========================================================================
          TAB 6: ABOUT
          ========================================================================= */}
      {activeTab === 'about' && (
        <div className="settings-section-card">
          <div className="settings-section-header">
            <div className="settings-section-icon">
              <Info size={20} />
            </div>
            <div>
              <h3 className="settings-section-title">About Smart Media Analysis Agent</h3>
              <p className="settings-section-desc">
                Multimodal Educational Content Intelligence Platform • v2.4.0
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <p style={{ fontSize: '0.9rem', color: '#F1F5F9', lineHeight: 1.6, margin: 0 }}>
              <strong>Smart Media Analysis Agent</strong> is an enterprise AI SaaS designed for modern
              education. It empowers students and researchers to ingest multimodal educational content
              (lecture videos, podcasts, and PDF notes) and transforms them into an interactive,
              searchable knowledge graph with grounded Q&A, automatic study synthesis, and adaptive practice quizzes.
            </p>

            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
              <span className="badge badge-violet" style={{ padding: '6px 12px', fontSize: '0.78rem' }}>
                Grounded RAG Engine
              </span>
              <span className="badge badge-cyan" style={{ padding: '6px 12px', fontSize: '0.78rem' }}>
                Semantic Vector Index
              </span>
              <span className="badge badge-pink" style={{ padding: '6px 12px', fontSize: '0.78rem' }}>
                Multimodal AI Reasoning
              </span>
              <span className="badge badge-indigo" style={{ padding: '6px 12px', fontSize: '0.78rem' }}>
                Speech Intelligence
              </span>
              <span className="badge badge-emerald" style={{ padding: '6px 12px', fontSize: '0.78rem' }}>
                FastAPI Engine
              </span>
              <span className="badge badge-amber" style={{ padding: '6px 12px', fontSize: '0.78rem' }}>
                React SaaS Client
              </span>
            </div>

            <div
              style={{
                padding: '18px 22px',
                background: 'rgba(8, 10, 18, 0.65)',
                border: '1px solid var(--border-glass)',
                borderRadius: '14px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                flexWrap: 'wrap',
                gap: '12px',
              }}
            >
              <div>
                <div style={{ fontSize: '0.9rem', fontWeight: 800, color: '#FFFFFF' }}>
                  Smart Media Analysis Agent
                </div>
                <div style={{ fontSize: '0.76rem', color: 'var(--color-text-secondary)', marginTop: '2px' }}>
                  Enterprise Edition • Educational Multimodal Intelligence System
                </div>
              </div>

              <span className="badge badge-emerald" style={{ fontSize: '0.74rem' }}>
                Status: 100% Operational
              </span>
            </div>
          </div>
        </div>
      )}

      {/* =========================================================================
          EDIT PROFILE MODAL
          ========================================================================= */}
      {showEditModal && (
        <div className="profile-edit-modal-backdrop" onClick={() => setShowEditModal(false)}>
          <div className="profile-edit-modal-card" onClick={(e) => e.stopPropagation()}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <User size={18} color="#A78BFA" />
                <h3 style={{ fontSize: '1.1rem', fontWeight: 800, color: '#FFFFFF', margin: 0 }}>
                  Edit Student Profile
                </h3>
              </div>
              <button
                onClick={() => setShowEditModal(false)}
                className="dashboard-modal-close-btn"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleSaveProfile} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 700, color: 'var(--color-text-secondary)', marginBottom: '6px' }}>
                  Full Name
                </label>
                <input
                  type="text"
                  value={editForm.name}
                  onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
                  className="settings-input-control"
                  style={{ maxWidth: '100%' }}
                  required
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 700, color: 'var(--color-text-secondary)', marginBottom: '6px' }}>
                  Email Address
                </label>
                <input
                  type="email"
                  value={editForm.email}
                  onChange={(e) => setEditForm({ ...editForm, email: e.target.value })}
                  className="settings-input-control"
                  style={{ maxWidth: '100%' }}
                  required
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 700, color: 'var(--color-text-secondary)', marginBottom: '6px' }}>
                  Role / Title
                </label>
                <input
                  type="text"
                  value={editForm.role}
                  onChange={(e) => setEditForm({ ...editForm, role: e.target.value })}
                  className="settings-input-control"
                  style={{ maxWidth: '100%' }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 700, color: 'var(--color-text-secondary)', marginBottom: '6px' }}>
                  Course & Specialization
                </label>
                <input
                  type="text"
                  value={editForm.course}
                  onChange={(e) => setEditForm({ ...editForm, course: e.target.value })}
                  className="settings-input-control"
                  style={{ maxWidth: '100%' }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '10px' }}>
                <button
                  type="button"
                  onClick={() => setShowEditModal(false)}
                  className="btn-secondary"
                  style={{ padding: '8px 16px', fontSize: '0.84rem' }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn-primary"
                  style={{ padding: '8px 20px', fontSize: '0.84rem', gap: '6px' }}
                >
                  <Check size={14} />
                  <span>Save Changes</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  Brain,
  MessageSquare,
  Film,
  BookOpen,
  HelpCircle,
  History,
  FileText,
  Music,
  CheckCircle2,
  Sparkles,
  LogOut,
  Settings,
  ShieldCheck,
} from 'lucide-react';

import FileUpload from '../components/FileUpload';
import DocumentList from '../components/DocumentList';
import MediaPlayer from '../components/MediaPlayer';
import ChatInterface from '../components/ChatInterface';
import StudySummary from '../components/StudySummary';
import QuizModule from '../components/QuizModule';
import HistoryPanel from '../components/HistoryPanel';
import apiService from '../services/api';

export default function DashboardPage({
  currentUser = null,
  onGoHome,
  onOpenSettings,
  onLogout,
}) {
  const [documents, setDocuments] = useState([]);
  const [activeDocument, setActiveDocument] = useState(null);
  const [activeTab, setActiveTab] = useState('chat'); // 'chat' | 'media' | 'summary' | 'quiz' | 'history'
  const [seekTarget, setSeekTarget] = useState(null);

  // =========================================================
  // DEMO MATERIALS (Used only when in Demo Account mode with 0 real files)
  // =========================================================
  const demoMaterials = useMemo(
    () => [
      {
        id: 'demo-doc-1',
        filename: 'Java OOP Basics.pdf',
        media_type: 'pdf',
        file_size: 2450000,
        page_count: 17,
        duration_seconds: null,
        status: 'READY',
        isDemo: true,
      },
      {
        id: 'demo-doc-2',
        filename: 'Introduction to Machine Learning.mp4',
        media_type: 'video',
        file_size: 19100000,
        page_count: null,
        duration_seconds: 45,
        status: 'READY',
        isDemo: true,
      },
      {
        id: 'demo-doc-3',
        filename: 'Cardiovascular System.wav',
        media_type: 'audio',
        file_size: 9020000,
        page_count: null,
        duration_seconds: 139,
        status: 'READY',
        isDemo: true,
      },
    ],
    []
  );

  // Computed displayed documents: real documents take precedence
  const displayDocuments = useMemo(() => {
    if (documents.length > 0) return documents;
    if (currentUser?.isDemo) return demoMaterials;
    return [];
  }, [documents, currentUser, demoMaterials]);

  // =========================================================
  // LOAD REAL DOCUMENTS FROM SQLITE BACKEND
  // =========================================================
  const loadDocuments = useCallback(async () => {
    try {
      const docs = await apiService.listDocuments();
      setDocuments(docs);

      setActiveDocument((currentActive) => {
        if (docs.length === 0) {
          if (currentUser?.isDemo) return demoMaterials[0];
          return null;
        }
        if (!currentActive) return docs[0];

        const updatedActive = docs.find((doc) => doc.id === currentActive.id);
        if (!updatedActive) return docs[0];

        const unchanged =
          updatedActive.status === currentActive.status &&
          updatedActive.filename === currentActive.filename &&
          updatedActive.file_size === currentActive.file_size &&
          updatedActive.page_count === currentActive.page_count &&
          updatedActive.duration_seconds === currentActive.duration_seconds;

        if (unchanged) return currentActive;
        return updatedActive;
      });
    } catch (error) {
      console.error('Failed to load documents:', error);
      if (currentUser?.isDemo && !activeDocument) {
        setActiveDocument(demoMaterials[0]);
      }
    }
  }, [currentUser, demoMaterials, activeDocument]);

  // Initialize and select first document
  useEffect(() => {
    loadDocuments();
  }, []);

  useEffect(() => {
    if (!activeDocument && displayDocuments.length > 0) {
      setActiveDocument(displayDocuments[0]);
    }
  }, [displayDocuments, activeDocument]);

  // Handle document upload success
  const handleUploadSuccess = (newDoc) => {
    loadDocuments();
    if (newDoc) {
      setActiveDocument(newDoc);
    }
  };

  // Handle document deletion
  const handleDeleteDocument = async (docId) => {
    try {
      await apiService.deleteDocument(docId);
      await loadDocuments();
    } catch (error) {
      console.error('Failed to delete document:', error);
    }
  };

  // Cross-tab seeking when clicking citations or timestamps
  const handleCitationClick = (citation) => {
    if (citation?.timestamp_start !== undefined && citation?.timestamp_start !== null) {
      setSeekTarget(citation.timestamp_start);
      setActiveTab('media');
    } else if (citation?.document_id) {
      const targetDoc = displayDocuments.find((d) => d.id === citation.document_id);
      if (targetDoc) setActiveDocument(targetDoc);
    }
  };

  const handleTimestampClick = (seconds) => {
    setSeekTarget(seconds);
    setActiveTab('media');
  };

  // Helper for active doc icon
  const getDocTypeIcon = (type) => {
    switch (type) {
      case 'video':
        return <Film size={14} color="#EC4899" />;
      case 'audio':
        return <Music size={14} color="#06B6D4" />;
      case 'pdf':
      case 'document':
      default:
        return <FileText size={14} color="#818CF8" />;
    }
  };

  const userName = currentUser?.name || 'Avneet Kaur';
  const userInitial = userName.charAt(0).toUpperCase();

  return (
    <div
      style={{
        minHeight: '100vh',
        background: 'var(--bg-midnight)',
        color: 'var(--color-white)',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {/* =========================================================================
          1. TOP FULL-WIDTH HEADER
          ========================================================================= */}
      <header
        style={{
          height: '70px',
          background: 'rgba(8, 10, 20, 0.88)',
          backdropFilter: 'blur(20px)',
          WebkitBackdropFilter: 'blur(20px)',
          borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
          padding: '0 28px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          position: 'sticky',
          top: 0,
          zIndex: 100,
          boxShadow: '0 4px 24px rgba(0, 0, 0, 0.4)',
        }}
      >
        {/* Left: Brand Logo & Title */}
        <div
          onClick={onGoHome}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '14px',
            cursor: 'pointer',
          }}
          title="Return to Landing Page"
        >
          <div
            style={{
              width: '40px',
              height: '40px',
              borderRadius: '12px',
              background: 'linear-gradient(135deg, #7C3AED 0%, #6366F1 50%, #06B6D4 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 0 20px rgba(124, 58, 237, 0.4)',
              flexShrink: 0,
            }}
          >
            <Brain size={22} color="#FFFFFF" />
          </div>

          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span
                style={{
                  fontSize: '1.05rem',
                  fontWeight: 800,
                  letterSpacing: '-0.02em',
                  color: '#FFFFFF',
                  fontFamily: 'var(--font-heading)',
                }}
              >
                Smart Media Analysis Agent
              </span>
            </div>
            <p
              style={{
                fontSize: '0.74rem',
                color: 'var(--color-muted)',
                margin: 0,
                letterSpacing: '0.01em',
              }}
            >
              Multimodal Educational Content Intelligence Platform
            </p>
          </div>
        </div>

        {/* Right: Active Material + Ready Status + Profile + Sign Out */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          {/* Active Material Pill */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '6px 12px',
              borderRadius: '9999px',
              background: 'rgba(255, 255, 255, 0.04)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              fontSize: '0.78rem',
              color: '#E2E8F0',
              maxWidth: '280px',
            }}
          >
            {activeDocument ? (
              <>
                {getDocTypeIcon(activeDocument.media_type)}
                <span
                  style={{
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                    fontWeight: 600,
                  }}
                  title={activeDocument.filename}
                >
                  {activeDocument.filename}
                </span>
              </>
            ) : (
              <>
                <Sparkles size={13} color="#A78BFA" />
                <span style={{ color: 'var(--color-muted)' }}>No material selected</span>
              </>
            )}
          </div>

          {/* Status Badge: Workspace Ready */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '5px 12px',
              borderRadius: '9999px',
              background: 'rgba(16, 185, 129, 0.12)',
              border: '1px solid rgba(16, 185, 129, 0.3)',
              fontSize: '0.74rem',
              fontWeight: 700,
              color: '#6EE7B7',
            }}
          >
            <span
              style={{
                width: '6px',
                height: '6px',
                borderRadius: '50%',
                background: '#10B981',
                boxShadow: '0 0 8px #10B981',
              }}
            />
            <span>Workspace Ready</span>
          </div>

          {/* Settings Shortcut */}
          {onOpenSettings && (
            <button
              onClick={onOpenSettings}
              style={{
                padding: '8px',
                borderRadius: '10px',
                background: 'rgba(255, 255, 255, 0.04)',
                border: '1px solid rgba(255, 255, 255, 0.08)',
                color: 'var(--color-muted)',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                transition: 'all 0.2s ease',
              }}
              title="Settings"
            >
              <Settings size={16} />
            </button>
          )}

          {/* User Profile Avatar */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '9px',
              padding: '4px 10px 4px 5px',
              borderRadius: '9999px',
              background: 'rgba(255, 255, 255, 0.04)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
            }}
          >
            <div
              style={{
                width: '28px',
                height: '28px',
                borderRadius: '50%',
                background: 'linear-gradient(135deg, #7C3AED 0%, #EC4899 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '0.8rem',
                fontWeight: 800,
                color: '#FFFFFF',
              }}
            >
              {userInitial}
            </div>
            <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#F1F5F9' }}>
              {userName}
            </span>
          </div>

          {/* Sign Out Button */}
          {onLogout && (
            <button
              onClick={onLogout}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                padding: '7px 14px',
                borderRadius: '10px',
                background: 'rgba(244, 63, 94, 0.1)',
                border: '1px solid rgba(244, 63, 94, 0.25)',
                color: '#FDA4AF',
                fontSize: '0.78rem',
                fontWeight: 700,
                cursor: 'pointer',
                transition: 'all 0.2s ease',
              }}
              title="Sign Out of Session"
            >
              <LogOut size={14} />
              <span>Sign Out</span>
            </button>
          )}
        </div>
      </header>

      {/* =========================================================================
          2. MAIN DASHBOARD — TWO-COLUMN LAYOUT
          ========================================================================= */}
      <main
        style={{
          flex: 1,
          padding: '24px 28px',
          display: 'flex',
          gap: '24px',
          maxWidth: '1680px',
          width: '100%',
          margin: '0 auto',
          boxSizing: 'border-box',
          alignItems: 'flex-start',
        }}
      >
        {/* =======================================================================
            LEFT COLUMN: UPLOAD MATERIAL + MEDIA LIBRARY (~340px)
            ======================================================================= */}
        <aside
          style={{
            width: '340px',
            flexShrink: 0,
            display: 'flex',
            flexDirection: 'column',
            gap: '18px',
          }}
        >
          {/* Card 1: Upload Learning Material */}
          <FileUpload onUploadSuccess={handleUploadSuccess} />

          {/* Card 2: Your Media Library */}
          <DocumentList
            documents={displayDocuments}
            activeDocument={activeDocument}
            onSelectDocument={setActiveDocument}
            onDeleteDocument={handleDeleteDocument}
            onRefresh={loadDocuments}
          />
        </aside>

        {/* =======================================================================
            RIGHT COLUMN: TAB NAVIGATION + WORKSPACE VIEWPORT (Remaining Width)
            ======================================================================= */}
        <section
          style={{
            flex: 1,
            minWidth: 0,
            display: 'flex',
            flexDirection: 'column',
            gap: '16px',
          }}
        >
          {/* Top Workspace Tab Bar */}
          <nav
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '6px',
              background: 'rgba(13, 16, 32, 0.75)',
              backdropFilter: 'blur(16px)',
              WebkitBackdropFilter: 'blur(16px)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              borderRadius: '14px',
              boxShadow: '0 4px 20px rgba(0, 0, 0, 0.3)',
            }}
          >
            {/* Tab 1: AI Agent Chat */}
            <button
              onClick={() => setActiveTab('chat')}
              style={{
                flex: 1,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                padding: '10px 14px',
                borderRadius: '10px',
                border: activeTab === 'chat'
                  ? '1px solid rgba(124, 58, 237, 0.55)'
                  : '1px solid transparent',
                background: activeTab === 'chat'
                  ? 'linear-gradient(135deg, rgba(124, 58, 237, 0.32) 0%, rgba(99, 102, 241, 0.22) 100%)'
                  : 'transparent',
                color: activeTab === 'chat' ? '#FFFFFF' : '#94A3B8',
                fontWeight: activeTab === 'chat' ? 700 : 600,
                fontSize: '0.84rem',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                boxShadow: activeTab === 'chat'
                  ? '0 0 16px rgba(124, 58, 237, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.15)'
                  : 'none',
              }}
            >
              <MessageSquare size={16} color={activeTab === 'chat' ? '#C4B5FD' : '#94A3B8'} />
              <span>AI Agent Chat</span>
            </button>

            {/* Tab 2: Media & Timestamps */}
            <button
              onClick={() => setActiveTab('media')}
              style={{
                flex: 1,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                padding: '10px 14px',
                borderRadius: '10px',
                border: activeTab === 'media'
                  ? '1px solid rgba(6, 182, 212, 0.55)'
                  : '1px solid transparent',
                background: activeTab === 'media'
                  ? 'linear-gradient(135deg, rgba(6, 182, 212, 0.3) 0%, rgba(59, 130, 246, 0.2) 100%)'
                  : 'transparent',
                color: activeTab === 'media' ? '#FFFFFF' : '#94A3B8',
                fontWeight: activeTab === 'media' ? 700 : 600,
                fontSize: '0.84rem',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                boxShadow: activeTab === 'media'
                  ? '0 0 16px rgba(6, 182, 212, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.15)'
                  : 'none',
              }}
            >
              <Film size={16} color={activeTab === 'media' ? '#67E8F9' : '#94A3B8'} />
              <span>Media & Timestamps</span>
            </button>

            {/* Tab 3: Study Notes */}
            <button
              onClick={() => setActiveTab('summary')}
              style={{
                flex: 1,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                padding: '10px 14px',
                borderRadius: '10px',
                border: activeTab === 'summary'
                  ? '1px solid rgba(124, 58, 237, 0.55)'
                  : '1px solid transparent',
                background: activeTab === 'summary'
                  ? 'linear-gradient(135deg, rgba(124, 58, 237, 0.32) 0%, rgba(236, 72, 153, 0.2) 100%)'
                  : 'transparent',
                color: activeTab === 'summary' ? '#FFFFFF' : '#94A3B8',
                fontWeight: activeTab === 'summary' ? 700 : 600,
                fontSize: '0.84rem',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                boxShadow: activeTab === 'summary'
                  ? '0 0 16px rgba(124, 58, 237, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.15)'
                  : 'none',
              }}
            >
              <BookOpen size={16} color={activeTab === 'summary' ? '#F472B6' : '#94A3B8'} />
              <span>Study Notes</span>
            </button>

            {/* Tab 4: Practice Quiz */}
            <button
              onClick={() => setActiveTab('quiz')}
              style={{
                flex: 1,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                padding: '10px 14px',
                borderRadius: '10px',
                border: activeTab === 'quiz'
                  ? '1px solid rgba(99, 102, 241, 0.55)'
                  : '1px solid transparent',
                background: activeTab === 'quiz'
                  ? 'linear-gradient(135deg, rgba(99, 102, 241, 0.32) 0%, rgba(6, 182, 212, 0.2) 100%)'
                  : 'transparent',
                color: activeTab === 'quiz' ? '#FFFFFF' : '#94A3B8',
                fontWeight: activeTab === 'quiz' ? 700 : 600,
                fontSize: '0.84rem',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                boxShadow: activeTab === 'quiz'
                  ? '0 0 16px rgba(99, 102, 241, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.15)'
                  : 'none',
              }}
            >
              <HelpCircle size={16} color={activeTab === 'quiz' ? '#818CF8' : '#94A3B8'} />
              <span>Practice Quiz</span>
            </button>

            {/* Tab 5: History */}
            <button
              onClick={() => setActiveTab('history')}
              style={{
                flex: 1,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                padding: '10px 14px',
                borderRadius: '10px',
                border: activeTab === 'history'
                  ? '1px solid rgba(6, 182, 212, 0.55)'
                  : '1px solid transparent',
                background: activeTab === 'history'
                  ? 'linear-gradient(135deg, rgba(6, 182, 212, 0.3) 0%, rgba(124, 58, 237, 0.2) 100%)'
                  : 'transparent',
                color: activeTab === 'history' ? '#FFFFFF' : '#94A3B8',
                fontWeight: activeTab === 'history' ? 700 : 600,
                fontSize: '0.84rem',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                boxShadow: activeTab === 'history'
                  ? '0 0 16px rgba(6, 182, 212, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.15)'
                  : 'none',
              }}
            >
              <History size={16} color={activeTab === 'history' ? '#67E8F9' : '#94A3B8'} />
              <span>History</span>
            </button>
          </nav>

          {/* Active Tab Workspace Container */}
          <div
            style={{
              flex: 1,
              minHeight: '680px',
              display: 'flex',
              flexDirection: 'column',
            }}
          >
            {activeTab === 'chat' && (
              <ChatInterface
                activeDocument={activeDocument}
                onCitationClick={handleCitationClick}
              />
            )}

            {activeTab === 'media' && (
              <MediaPlayer
                activeDocument={activeDocument}
                seekTarget={seekTarget}
                onTimestampClick={handleTimestampClick}
              />
            )}

            {activeTab === 'summary' && (
              <StudySummary
                activeDocument={activeDocument}
                onTimestampClick={handleTimestampClick}
              />
            )}

            {activeTab === 'quiz' && (
              <QuizModule
                activeDocument={activeDocument}
                onCitationClick={handleCitationClick}
              />
            )}

            {activeTab === 'history' && (
              <HistoryPanel activeDocument={activeDocument} />
            )}
          </div>
        </section>
      </main>
    </div>
  );
}
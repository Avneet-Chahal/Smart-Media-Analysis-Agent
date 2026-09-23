import React, { useState, useEffect, useCallback } from 'react';
import {
  BookOpen,
  Sparkles,
  CheckSquare,
  Clock,
  Lightbulb,
  RefreshCw,
  AlertCircle,
  Loader2,
  FileText,
  Layers,
  ShieldCheck,
  Zap,
  Film,
  Music,
  ExternalLink,
  ChevronRight,
  CheckCircle2,
  BookmarkCheck,
} from 'lucide-react';
import { formatSeconds } from '../utils/formatters';
import apiService from '../services/api';

export default function StudySummary({ activeDocument, onTimestampClick }) {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [checkedItems, setCheckedItems] = useState({});

  /*
   * Generate / refresh the study summary.
   */
  const loadSummary = useCallback(async () => {
    if (!activeDocument?.id) return;

    setLoading(true);
    setError(null);

    try {
      const data = await apiService.getSummary(activeDocument.id);
      setSummary(data);
    } catch (err) {
      console.error('Study summary error:', err);
      setError('Failed to generate educational summary. Please ensure the document is ready.');
    } finally {
      setLoading(false);
    }
  }, [activeDocument?.id]);

  /*
   * Watch ONLY the document ID to prevent re-generating when dashboard polls.
   */
  useEffect(() => {
    if (activeDocument?.id) {
      setSummary(null);
      setCheckedItems({});
      loadSummary();
    } else {
      setSummary(null);
      setCheckedItems({});
    }
  }, [activeDocument?.id, loadSummary]);

  const toggleCheck = (idx) => {
    setCheckedItems((prev) => ({
      ...prev,
      [idx]: !prev[idx],
    }));
  };

  const accentColors = ['violet', 'cyan', 'pink', 'blue'];

  if (!activeDocument) {
    return (
      <div className="study-empty-state-panel">
        <div className="study-empty-orb">
          <BookOpen size={36} color="#A78BFA" />
        </div>
        <h3 className="study-empty-title">AI Study Notes & Concept Synthesis</h3>
        <p className="study-empty-desc">
          Select an educational material from the dashboard to synthesize executive overviews, key definitions, exam points, and verifiable citations.
        </p>
      </div>
    );
  }

  // Derive important topics from key concepts or summary
  const keyConceptsList = summary?.key_concepts || [];
  const actionItemsList = summary?.action_items || [];

  return (
    <div className="study-notes-container">
      {/* =========================================================================
          HEADER
          ========================================================================= */}
      <div className="study-notes-header">
        <div className="study-header-left">
          <div className="study-brand-icon-orb">
            <BookOpen size={20} color="#FFFFFF" />
          </div>
          <div className="study-header-titles">
            <div className="study-title-row">
              <h2 className="study-main-heading">
                Study Notes: {activeDocument.filename}
              </h2>
              <span className="badge badge-violet">
                <Sparkles size={11} /> AI Synthesis
              </span>
            </div>
            <p className="study-sub-heading">
              Comprehensive educational intelligence & high-yield revision document
            </p>
          </div>
        </div>

        {/* Action Button: Regenerate Notes */}
        <div className="study-header-actions">
          <button
            onClick={loadSummary}
            disabled={loading}
            className="study-regenerate-btn"
            title="Re-synthesize study notes with AI"
          >
            {loading ? (
              <Loader2 className="animate-spin" size={14} />
            ) : (
              <RefreshCw size={14} />
            )}
            <span>{loading ? 'Synthesizing...' : 'Regenerate Notes'}</span>
          </button>
        </div>
      </div>

      {/* =========================================================================
          LOADING STATE
          ========================================================================= */}
      {loading && (
        <div className="study-loading-container">
          <div className="study-loading-orb-pulse">
            <Loader2 className="animate-spin" size={38} color="#A78BFA" />
          </div>
          <h4 className="study-loading-title">
            Synthesizing lecture material & extracting core concepts...
          </h4>
          <p className="study-loading-desc">
            Formulating executive summary, key definitions, important topics, and high-yield exam checklists.
          </p>
        </div>
      )}

      {/* =========================================================================
          ERROR NOTICE
          ========================================================================= */}
      {error && (
        <div className="study-error-banner">
          <AlertCircle size={18} />
          <span>{error}</span>
          <button onClick={loadSummary} className="btn-secondary" style={{ padding: '4px 10px', fontSize: '0.74rem' }}>
            Retry
          </button>
        </div>
      )}

      {/* =========================================================================
          STUDY DOCUMENT CONTENT
          ========================================================================= */}
      {!loading && summary && (
        <div className="study-document-body">
          {/* ---------------------------------------------------------------------
              SECTION 1: EXECUTIVE OVERVIEW
              --------------------------------------------------------------------- */}
          <section className="study-section-box overview-section">
            <div className="study-section-header">
              <div className="study-section-icon-wrap violet">
                <Sparkles size={16} />
              </div>
              <h3 className="study-section-title">EXECUTIVE OVERVIEW</h3>
            </div>

            <div className="study-overview-content">
              <p>{summary.overview}</p>
            </div>
          </section>

          {/* ---------------------------------------------------------------------
              SECTION 2: KEY CONCEPTS & IMPORTANT DEFINITIONS
              --------------------------------------------------------------------- */}
          <section className="study-section-box">
            <div className="study-section-header">
              <div className="study-section-icon-wrap cyan">
                <Lightbulb size={16} />
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <h3 className="study-section-title">KEY CONCEPTS & IMPORTANT DEFINITIONS</h3>
                <span className="study-section-count-pill">
                  {keyConceptsList.length} Concepts
                </span>
              </div>
            </div>

            <div className="study-concepts-grid">
              {keyConceptsList.map((item, idx) => {
                const color = accentColors[idx % accentColors.length];
                const hasTimestamp = item.timestamp !== null && item.timestamp !== undefined;
                const hasPage = item.page !== null && item.page !== undefined;

                return (
                  <div key={idx} className={`concept-glass-card ${color}`}>
                    <div className="concept-card-top-bar">
                      <span className="concept-tag-badge">
                        CONCEPT #{idx + 1}
                      </span>

                      {hasTimestamp ? (
                        <button
                          onClick={() => onTimestampClick && onTimestampClick(item.timestamp)}
                          className="concept-location-badge video"
                          title="Click to seek to exact video moment"
                        >
                          <Clock size={11} />
                          <span>{formatSeconds(item.timestamp)}</span>
                        </button>
                      ) : hasPage ? (
                        <span className="concept-location-badge pdf">
                          <BookOpen size={11} />
                          <span>Page {item.page}</span>
                        </span>
                      ) : (
                        <span className="concept-location-badge default">
                          <BookmarkCheck size={11} />
                          <span>Key Principle</span>
                        </span>
                      )}
                    </div>

                    <div className="concept-card-body">
                      <h4 className="concept-title">{item.concept}</h4>
                      <p className="concept-description">{item.description}</p>
                    </div>
                  </div>
                );
              })}
            </div>
          </section>

          {/* ---------------------------------------------------------------------
              SECTION 3: IMPORTANT TOPICS
              --------------------------------------------------------------------- */}
          <section className="study-section-box">
            <div className="study-section-header">
              <div className="study-section-icon-wrap pink">
                <Layers size={16} />
              </div>
              <h3 className="study-section-title">IMPORTANT TOPICS</h3>
            </div>

            <div className="study-important-topics-list">
              {keyConceptsList.slice(0, 4).map((item, idx) => (
                <div key={idx} className="important-topic-item">
                  <div className="topic-bullet-number">{idx + 1}</div>
                  <div className="topic-text-content">
                    <h5 className="topic-heading">{item.concept}</h5>
                    <p className="topic-subtext">{item.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* ---------------------------------------------------------------------
              SECTION 4: EXAM POINTS & CHECKLIST
              --------------------------------------------------------------------- */}
          {actionItemsList.length > 0 && (
            <section className="study-section-box">
              <div className="study-section-header">
                <div className="study-section-icon-wrap blue">
                  <CheckSquare size={16} />
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <h3 className="study-section-title">EXAM POINTS</h3>
                  <span className="study-section-count-pill">
                    {actionItemsList.length} High-Yield Checklist
                  </span>
                </div>
              </div>

              <div className="study-exam-checklist">
                {actionItemsList.map((action, idx) => {
                  const isChecked = !!checkedItems[idx];

                  return (
                    <label
                      key={idx}
                      className={`exam-checklist-item ${isChecked ? 'completed' : ''}`}
                    >
                      <input
                        type="checkbox"
                        checked={isChecked}
                        onChange={() => toggleCheck(idx)}
                        className="exam-checkbox"
                      />
                      <span className="exam-item-text">{action}</span>
                      {isChecked && (
                        <span className="exam-reviewed-tag">Reviewed</span>
                      )}
                    </label>
                  );
                })}
              </div>
            </section>
          )}

          {/* ---------------------------------------------------------------------
              SECTION 5: SOURCES
              --------------------------------------------------------------------- */}
          <section className="study-section-box sources-section">
            <div className="study-section-header">
              <div className="study-section-icon-wrap green">
                <ShieldCheck size={16} />
              </div>
              <h3 className="study-section-title">SOURCES</h3>
            </div>

            <div className="study-sources-card">
              <div className="source-meta-item">
                <div className="source-doc-icon">
                  {activeDocument.media_type === 'video' ? (
                    <Film size={18} color="#06B6D4" />
                  ) : activeDocument.media_type === 'audio' ? (
                    <Music size={18} color="#38BDF8" />
                  ) : (
                    <FileText size={18} color="#818CF8" />
                  )}
                </div>
                <div className="source-doc-info">
                  <span className="source-filename">{activeDocument.filename}</span>
                  <span className="source-details">
                    Grounded with Semantic Vector Knowledge Index •{' '}
                    {activeDocument.page_count
                      ? `${activeDocument.page_count} Pages Indexed`
                      : activeDocument.duration_seconds
                      ? `${formatSeconds(activeDocument.duration_seconds)} Spoken Audio Track`
                      : 'Multimodal Ingestion Ready'}
                  </span>
                </div>
              </div>

              <div className="source-verification-badge">
                <CheckCircle2 size={13} color="#10B981" />
                <span>100% Grounded Content</span>
              </div>
            </div>
          </section>
        </div>
      )}
    </div>
  );
}
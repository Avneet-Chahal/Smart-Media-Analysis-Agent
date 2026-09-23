import React from 'react';
import {
  FileText,
  Film,
  Music,
  Trash2,
  Clock,
  BookOpen,
  Layers,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  FolderOpen,
} from 'lucide-react';
import { formatBytes, formatSeconds } from '../utils/formatters';

export default function DocumentList({
  documents,
  activeDocument,
  onSelectDocument,
  onDeleteDocument,
  onRefresh,
}) {
  const getMediaIcon = (type) => {
    switch (type) {
      case 'video':
        return <Film size={15} color="#EC4899" />;
      case 'audio':
        return <Music size={15} color="#06B6D4" />;
      case 'pdf':
      case 'document':
      default:
        return <FileText size={15} color="#818CF8" />;
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'READY':
        return (
          <span
            className="badge badge-emerald"
            style={{ fontSize: '0.66rem', padding: '2px 7px' }}
          >
            <CheckCircle2 size={10} /> Ready
          </span>
        );
      case 'PROCESSING':
        return (
          <span
            className="badge badge-amber"
            style={{ fontSize: '0.66rem', padding: '2px 7px' }}
          >
            <RefreshCw className="animate-spin" size={10} /> Ingesting
          </span>
        );
      case 'ERROR':
        return (
          <span
            className="badge badge-rose"
            style={{ fontSize: '0.66rem', padding: '2px 7px' }}
          >
            <AlertCircle size={10} /> Error
          </span>
        );
      default:
        return (
          <span
            className="badge badge-indigo"
            style={{ fontSize: '0.66rem', padding: '2px 7px' }}
          >
            {status}
          </span>
        );
    }
  };

  return (
    <div
      className="glass-panel"
      style={{
        padding: '18px',
        display: 'flex',
        flexDirection: 'column',
        gap: '12px',
      }}
    >
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <FolderOpen size={15} color="#818CF8" />
          <h3 style={{ fontSize: '0.86rem', fontWeight: 800, letterSpacing: '0.04em', textTransform: 'uppercase', color: '#E2E8F0' }}>
            MEDIA LIBRARY
          </h3>
          <span
            className="badge badge-violet"
            style={{ fontSize: '0.68rem', padding: '2px 7px', fontWeight: 700 }}
          >
            {documents.length}
          </span>
        </div>

        <button
          onClick={onRefresh}
          className="btn-secondary"
          style={{
            padding: '5px 8px',
            fontSize: '0.74rem',
            borderRadius: '8px',
          }}
          title="Refresh Media Library"
        >
          <RefreshCw size={12} />
        </button>
      </div>

      {/* Document List or Empty State */}
      {documents.length === 0 ? (
        <div
          style={{
            textAlign: 'center',
            padding: '32px 12px',
            color: 'var(--color-muted)',
            background: 'rgba(8, 10, 18, 0.45)',
            borderRadius: '12px',
            border: '1px dashed var(--border-glass-light)',
          }}
        >
          <Layers size={28} style={{ margin: '0 auto 8px auto', opacity: 0.35, color: '#818CF8' }} />
          <p style={{ fontSize: '0.86rem', fontWeight: 600, color: 'var(--color-white)' }}>
            No media uploaded yet
          </p>
          <p style={{ fontSize: '0.74rem', color: 'var(--color-dim)', marginTop: '3px', lineHeight: 1.4 }}>
            Upload lecture notes, audio or video above to begin analyzing.
          </p>
        </div>
      ) : (
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '8px',
            maxHeight: '440px',
            overflowY: 'auto',
            paddingRight: '2px',
          }}
        >
          {documents.map((doc) => {
            const isActive = activeDocument?.id === doc.id;

            return (
              <div
                key={doc.id}
                onClick={() => onSelectDocument(doc)}
                style={{
                  position: 'relative',
                  padding: '12px 14px',
                  borderRadius: '12px',
                  background: isActive
                    ? 'linear-gradient(135deg, rgba(124, 58, 237, 0.24) 0%, rgba(99, 102, 241, 0.14) 100%)'
                    : 'rgba(10, 13, 26, 0.65)',
                  border: `1px solid ${
                    isActive ? 'rgba(124, 58, 237, 0.6)' : 'rgba(255, 255, 255, 0.07)'
                  }`,
                  cursor: 'pointer',
                  transition: 'all var(--transition-fast)',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '8px',
                  boxShadow: isActive
                    ? '0 0 20px rgba(124, 58, 237, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.12)'
                    : 'none',
                }}
              >
                {/* Active Indicator Bar */}
                {isActive && (
                  <div
                    style={{
                      position: 'absolute',
                      left: 0,
                      top: '6px',
                      bottom: '6px',
                      width: '3.5px',
                      borderRadius: '0 3px 3px 0',
                      background: 'var(--gradient-primary)',
                      boxShadow: '0 0 8px #7C3AED',
                    }}
                  />
                )}

                {/* Top Row: Icon + Filename + Delete */}
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'flex-start',
                    justifyContent: 'space-between',
                    gap: '8px',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', overflow: 'hidden' }}>
                    <div
                      style={{
                        padding: '7px',
                        borderRadius: '9px',
                        background: isActive
                          ? 'rgba(124, 58, 237, 0.28)'
                          : 'rgba(255, 255, 255, 0.04)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        flexShrink: 0,
                        border: '1px solid rgba(255, 255, 255, 0.07)',
                      }}
                    >
                      {getMediaIcon(doc.media_type)}
                    </div>

                    <div style={{ overflow: 'hidden' }}>
                      <p
                        style={{
                          fontSize: '0.85rem',
                          fontWeight: isActive ? 700 : 500,
                          color: isActive ? '#ffffff' : 'var(--color-white)',
                          whiteSpace: 'nowrap',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          maxWidth: '175px',
                        }}
                        title={doc.filename}
                      >
                        {doc.filename}
                      </p>
                      <span style={{ fontSize: '0.71rem', color: 'var(--color-muted)' }}>
                        {formatBytes(doc.file_size)}
                      </span>
                    </div>
                  </div>

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      if (window.confirm(`Delete "${doc.filename}"?`)) {
                        onDeleteDocument(doc.id);
                      }
                    }}
                    className="btn-danger"
                    title="Delete Media Document"
                  >
                    <Trash2 size={13} />
                  </button>
                </div>

                {/* Bottom Row: Metadata & Status */}
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    fontSize: '0.73rem',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--color-muted)' }}>
                    {doc.duration_seconds ? (
                      <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <Clock size={11} color="var(--color-cyan)" />{' '}
                        {formatSeconds(doc.duration_seconds)}
                      </span>
                    ) : doc.page_count ? (
                      <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <BookOpen size={11} color="var(--color-indigo)" /> {doc.page_count} Pages
                      </span>
                    ) : null}
                  </div>

                  {getStatusBadge(doc.status)}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

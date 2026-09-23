import React, { useState, useRef } from 'react';
import { UploadCloud, FileText, Film, Music, AlertTriangle, Loader2, Plus, Sparkles } from 'lucide-react';
import apiService from '../services/api';

export default function FileUpload({ onUploadSuccess }) {
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileSelected(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelected = async (file) => {
    if (!file) return;
    setError(null);
    setUploading(true);
    setProgress(0);

    try {
      const doc = await apiService.uploadFile(file, (progressEvent) => {
        const percent = Math.round((progressEvent.loaded * 100) / (progressEvent.total || 100));
        setProgress(percent);
      });
      setUploading(false);
      setProgress(100);
      if (onUploadSuccess) {
        onUploadSuccess(doc);
      }
    } catch (err) {
      setUploading(false);
      setError(err.response?.data?.detail || 'Upload failed. Please verify the file format and try again.');
    }
  };

  return (
    <div className="glass-panel" style={{ padding: '18px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
      {/* Card Header */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <h3
            style={{
              fontSize: '0.82rem',
              fontWeight: 800,
              letterSpacing: '0.06em',
              textTransform: 'uppercase',
              color: '#F1F5F9',
              margin: 0,
            }}
          >
            UPLOAD LEARNING MATERIAL
          </h3>

          <span className="badge badge-violet" style={{ fontSize: '0.65rem', padding: '1px 7px' }}>
            Multimodal
          </span>
        </div>
        <p style={{ fontSize: '0.74rem', color: 'var(--color-muted)', marginTop: '4px', marginBottom: 0 }}>
          Ingest course notes, audio & video lectures
        </p>
      </div>

      {/* Hidden File Input */}
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.docx,.doc,.txt,.mp3,.wav,.m4a,.mp4,.mov,.webm"
        style={{ display: 'none' }}
        disabled={uploading}
        onChange={(e) => {
          if (e.target.files && e.target.files.length > 0) {
            handleFileSelected(e.target.files[0]);
          }
        }}
      />

      {/* Drag & Drop Area */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !uploading && fileInputRef.current?.click()}
        style={{
          position: 'relative',
          border: `1.5px dashed ${
            isDragging ? 'var(--color-violet)' : 'rgba(255, 255, 255, 0.14)'
          }`,
          borderRadius: '14px',
          padding: '22px 14px',
          textAlign: 'center',
          cursor: uploading ? 'default' : 'pointer',
          background: isDragging
            ? 'radial-gradient(ellipse at center, rgba(124, 58, 237, 0.24) 0%, rgba(13, 16, 32, 0.9) 100%)'
            : 'rgba(8, 10, 20, 0.55)',
          transition: 'all var(--transition-normal)',
          boxShadow: isDragging ? '0 0 24px rgba(124, 58, 237, 0.35)' : 'none',
        }}
      >
        {/* Upload Icon Container */}
        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '10px' }}>
          <div
            style={{
              width: '46px',
              height: '46px',
              borderRadius: '13px',
              background: uploading
                ? 'rgba(124, 58, 237, 0.25)'
                : 'linear-gradient(135deg, rgba(124, 58, 237, 0.25) 0%, rgba(99, 102, 241, 0.15) 100%)',
              border: '1px solid rgba(124, 58, 237, 0.4)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#C4B5FD',
              boxShadow: '0 4px 14px rgba(124, 58, 237, 0.2)',
            }}
          >
            {uploading ? (
              <Loader2 className="animate-spin" size={22} color="#C4B5FD" />
            ) : (
              <UploadCloud size={22} />
            )}
          </div>
        </div>

        <p style={{ fontWeight: 700, fontSize: '0.88rem', color: '#FFFFFF', marginBottom: '3px' }}>
          {uploading ? 'Vectorizing Lecture Content...' : 'Drag & drop your lecture file here'}
        </p>
        <p style={{ fontSize: '0.75rem', color: '#94A3B8', marginBottom: '12px' }}>
          {uploading ? 'Extracting speech transcripts & semantic chunks' : 'or browse from your device'}
        </p>

        {/* Format Badges */}
        <div style={{ display: 'flex', justifyContent: 'center', gap: '6px', flexWrap: 'wrap' }}>
          <span className="badge badge-indigo" style={{ fontSize: '0.66rem', padding: '3px 8px', fontWeight: 700 }}>
            <FileText size={10} /> PDF
          </span>
          <span className="badge badge-cyan" style={{ fontSize: '0.66rem', padding: '3px 8px', fontWeight: 700 }}>
            <Music size={10} /> AUDIO
          </span>
          <span className="badge badge-pink" style={{ fontSize: '0.66rem', padding: '3px 8px', fontWeight: 700 }}>
            <Film size={10} /> VIDEO
          </span>
        </div>

        {/* Upload & Indexing Progress */}
        {uploading && (
          <div style={{ marginTop: '12px' }}>
            <div
              style={{
                width: '100%',
                height: '4px',
                background: 'rgba(255, 255, 255, 0.08)',
                borderRadius: '9999px',
                overflow: 'hidden',
              }}
            >
              <div
                style={{
                  width: `${progress}%`,
                  height: '100%',
                  background: 'var(--gradient-primary)',
                  borderRadius: '9999px',
                  transition: 'width 0.2s ease',
                  boxShadow: '0 0 10px rgba(124, 58, 237, 0.6)',
                }}
              />
            </div>
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                marginTop: '5px',
                fontSize: '0.7rem',
                color: 'var(--color-muted)',
              }}
            >
              <span>Ingesting & Indexing</span>
              <span style={{ fontWeight: 700, color: '#C4B5FD' }}>{progress}%</span>
            </div>
          </div>
        )}
      </div>

      {/* Error Notice */}
      {error && (
        <div
          style={{
            padding: '9px 12px',
            borderRadius: '9px',
            background: 'rgba(244, 63, 94, 0.12)',
            border: '1px solid rgba(244, 63, 94, 0.3)',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontSize: '0.76rem',
            color: '#FDA4AF',
          }}
        >
          <AlertTriangle size={14} style={{ flexShrink: 0 }} />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
}

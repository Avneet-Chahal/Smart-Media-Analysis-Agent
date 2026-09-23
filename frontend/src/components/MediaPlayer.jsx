import React, { useRef, useEffect, useState, useMemo } from 'react';
import {
  Play,
  Pause,
  Volume2,
  Film,
  Music,
  FileText,
  Bookmark,
  Clock,
  Layers,
  Search,
  CheckCircle2,
  ExternalLink,
  Sparkles,
  Zap,
  Radio,
  FileSpreadsheet,
  Maximize2,
} from 'lucide-react';
import { formatSeconds } from '../utils/formatters';
import apiService from '../services/api';

export default function MediaPlayer({
  activeDocument,
  seekTarget,
  onTimestampClick,
}) {
  const mediaRef = useRef(null);
  const transcriptContainerRef = useRef(null);
  const activeChunkRef = useRef(null);

  const [chunks, setChunks] = useState([]);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackRate, setPlaybackRate] = useState(1);
  const [transcriptSearch, setTranscriptSearch] = useState('');

  // =========================================================
  // LOAD TRANSCRIPT CHUNKS
  // =========================================================
  useEffect(() => {
    if (!activeDocument?.id) {
      setChunks([]);
      return;
    }

    apiService
      .getDocumentChunks(activeDocument.id)
      .then((data) => {
        const sortedChunks = [...data]
          .filter(
            (chunk) =>
              chunk.timestamp_start !== null &&
              chunk.timestamp_start !== undefined
          )
          .sort(
            (a, b) =>
              Number(a.timestamp_start) -
              Number(b.timestamp_start)
          );

        setChunks(sortedChunks);
      })
      .catch((err) => {
        console.error('Failed to load chunks', err);
        setChunks([]);
      });
  }, [activeDocument]);

  // =========================================================
  // RESET PLAYER WHEN DOCUMENT CHANGES
  // =========================================================
  useEffect(() => {
    setCurrentTime(0);
    setDuration(0);
    setIsPlaying(false);
    setTranscriptSearch('');

    if (mediaRef.current) {
      mediaRef.current.pause();
      mediaRef.current.currentTime = 0;
    }
  }, [activeDocument]);

  // =========================================================
  // HANDLE EXTERNAL SEEK
  // =========================================================
  useEffect(() => {
    if (
      seekTarget !== null &&
      seekTarget !== undefined &&
      mediaRef.current
    ) {
      const targetSec = Number(seekTarget);
      mediaRef.current.currentTime = targetSec;
      setCurrentTime(targetSec);

      mediaRef.current
        .play()
        .then(() => {
          setIsPlaying(true);
        })
        .catch(() => {
          // Browser may block autoplay
        });
    }
  }, [seekTarget]);

  // =========================================================
  // FIND CURRENT TRANSCRIPT CHUNK
  // =========================================================
  const getCurrentChunk = () => {
    if (!chunks.length) return null;

    const matchingChunk = chunks.find((chunk) => {
      const start = Number(chunk.timestamp_start);
      const end =
        chunk.timestamp_end !== null && chunk.timestamp_end !== undefined
          ? Number(chunk.timestamp_end)
          : null;

      if (end !== null) {
        return currentTime >= start && currentTime <= end;
      }
      return currentTime >= start;
    });

    if (matchingChunk) return matchingChunk;

    let previousChunk = null;
    for (const chunk of chunks) {
      if (Number(chunk.timestamp_start) <= currentTime) {
        previousChunk = chunk;
      } else {
        break;
      }
    }

    return previousChunk;
  };

  const currentChunk = getCurrentChunk();

  // =========================================================
  // AUTO-SCROLL CURRENT TRANSCRIPT
  // =========================================================
  useEffect(() => {
    if (
      !isPlaying ||
      !currentChunk ||
      !activeChunkRef.current ||
      !transcriptContainerRef.current
    ) {
      return;
    }

    const container = transcriptContainerRef.current;
    const activeElement = activeChunkRef.current;

    const containerRect = container.getBoundingClientRect();
    const elementRect = activeElement.getBoundingClientRect();

    const isOutsideTop = elementRect.top < containerRect.top;
    const isOutsideBottom = elementRect.bottom > containerRect.bottom;

    if (isOutsideTop || isOutsideBottom) {
      activeElement.scrollIntoView({
        behavior: 'smooth',
        block: 'center',
      });
    }
  }, [currentChunk, isPlaying]);

  // Filtered transcript chunks based on search
  const filteredChunks = useMemo(() => {
    if (!transcriptSearch.trim()) return chunks;
    const query = transcriptSearch.toLowerCase();
    return chunks.filter((chunk) =>
      chunk.content.toLowerCase().includes(query)
    );
  }, [chunks, transcriptSearch]);

  // =========================================================
  // NO DOCUMENT SELECTED
  // =========================================================
  if (!activeDocument) {
    return (
      <div className="media-empty-placeholder-panel">
        <div className="media-empty-icon-orb">
          <Film size={34} color="#06B6D4" />
        </div>
        <h3 className="media-empty-title">Media & Timeline Intelligence</h3>
        <p className="media-empty-desc">
          Select a lecture video, audio recording, or PDF from the dashboard to explore AI-indexed timestamps and grounded transcripts.
        </p>
      </div>
    );
  }

  const streamUrl = `/api/media/${activeDocument.id}/stream`;
  const isVideo = activeDocument.media_type === 'video';
  const isAudio = activeDocument.media_type === 'audio';
  const isPdf =
    activeDocument.media_type === 'pdf' ||
    activeDocument.media_type === 'document';

  const handleTimeUpdate = () => {
    if (mediaRef.current) {
      setCurrentTime(mediaRef.current.currentTime);
    }
  };

  const handleLoadedMetadata = () => {
    if (mediaRef.current) {
      setDuration(mediaRef.current.duration || activeDocument.duration_seconds || 0);
    }
  };

  const handlePlay = () => setIsPlaying(true);
  const handlePause = () => setIsPlaying(false);

  const togglePlayPause = () => {
    if (!mediaRef.current) return;
    if (isPlaying) {
      mediaRef.current.pause();
    } else {
      mediaRef.current.play().catch(() => {});
    }
  };

  const handleRateChange = (rate) => {
    setPlaybackRate(rate);
    if (mediaRef.current) {
      mediaRef.current.playbackRate = rate;
    }
  };

  const jumpTo = (timeSec) => {
    if (!mediaRef.current || timeSec === null || timeSec === undefined) return;

    const targetTime = Number(timeSec);
    mediaRef.current.currentTime = targetTime;

    mediaRef.current
      .play()
      .then(() => setIsPlaying(true))
      .catch(() => {});

    setCurrentTime(targetTime);

    if (onTimestampClick) {
      onTimestampClick(targetTime);
    }
  };

  const getTimeRange = (chunk) => {
    const start = Number(chunk.timestamp_start);
    if (chunk.timestamp_end !== null && chunk.timestamp_end !== undefined) {
      const end = Number(chunk.timestamp_end);
      return `${formatSeconds(start)} - ${formatSeconds(end)}`;
    }
    return formatSeconds(start);
  };

  return (
    <div className="media-intelligence-container">
      {/* =========================================================================
          HEADER
          ========================================================================= */}
      <div className="media-header-bar">
        <div className="media-header-left">
          <div className={`media-header-type-icon ${isVideo ? 'video' : isAudio ? 'audio' : 'pdf'}`}>
            {isVideo ? (
              <Film size={20} color="#06B6D4" />
            ) : isAudio ? (
              <Music size={20} color="#38BDF8" />
            ) : (
              <FileText size={20} color="#818CF8" />
            )}
          </div>

          <div className="media-header-text">
            <h2 className="media-header-title">Media & Timeline Intelligence</h2>
            <div className="media-header-filename-row">
              <span className="media-header-filename" title={activeDocument.filename}>
                {activeDocument.filename}
              </span>
              {activeDocument.status === 'READY' && (
                <span className="badge badge-emerald" style={{ fontSize: '0.64rem', padding: '2px 7px' }}>
                  <CheckCircle2 size={10} /> Processed
                </span>
              )}
            </div>
          </div>
        </div>

        <div className="media-header-right">
          <span
            className={`media-type-badge ${
              isVideo ? 'video' : isAudio ? 'audio' : 'pdf'
            }`}
          >
            {isVideo ? 'VIDEO' : isAudio ? 'AUDIO' : 'PDF'}
          </span>
        </div>
      </div>

      {/* =========================================================================
          PDF WORKSPACE
          ========================================================================= */}
      {isPdf ? (
        <div className="pdf-workspace-wrapper">
          <div className="pdf-workspace-toolbar">
            <div className="pdf-toolbar-left">
              <FileText size={16} color="#818CF8" />
              <span className="pdf-toolbar-label">
                Interactive Document Viewer
                {activeDocument.page_count ? ` • ${activeDocument.page_count} Pages` : ''}
              </span>
            </div>
            <a
              href={streamUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="btn-secondary"
              style={{ padding: '5px 12px', fontSize: '0.76rem', gap: '6px' }}
            >
              <ExternalLink size={12} />
              <span>Open in New Tab</span>
            </a>
          </div>

          <div className="pdf-iframe-container">
            <iframe
              src={streamUrl}
              title={activeDocument.filename}
              className="pdf-iframe-view"
            />
          </div>
        </div>
      ) : (
        /* =========================================================================
            VIDEO / AUDIO: TWO-COLUMN WORKSPACE (LEFT 65% / RIGHT 35%)
            ========================================================================= */
        <div className="media-workspace-grid-65-35">
          {/* -----------------------------------------------------------------------
              LEFT 65%: LARGE PREMIUM MEDIA PLAYER
              ----------------------------------------------------------------------- */}
          <div className="media-player-column">
            <div className={`media-player-screen-box ${isVideo ? 'video' : 'audio'}`}>
              {isVideo && (
                <video
                  ref={mediaRef}
                  src={streamUrl}
                  controls
                  onTimeUpdate={handleTimeUpdate}
                  onLoadedMetadata={handleLoadedMetadata}
                  onPlay={handlePlay}
                  onPause={handlePause}
                  className="media-video-element"
                />
              )}

              {isAudio && (
                <div className="audio-visualizer-card">
                  <div className="audio-waveform-orb">
                    <Radio size={32} color="#06B6D4" />
                    <div className="audio-pulse-ring" />
                  </div>
                  <div className="audio-meta-text">
                    <h4 className="audio-now-playing-title">{activeDocument.filename}</h4>
                    <p className="audio-now-playing-sub">Speech-to-Text Multi-Track Index</p>
                  </div>

                  <audio
                    ref={mediaRef}
                    src={streamUrl}
                    controls
                    onTimeUpdate={handleTimeUpdate}
                    onLoadedMetadata={handleLoadedMetadata}
                    onPlay={handlePlay}
                    onPause={handlePause}
                    onEnded={() => setIsPlaying(false)}
                    className="audio-html-element"
                  />
                </div>
              )}
            </div>

            {/* Media Player Controls & Telemetry Bar */}
            <div className="media-telemetry-bar">
              <div className="media-telemetry-left">
                <button
                  onClick={togglePlayPause}
                  className="media-play-pause-btn"
                  title={isPlaying ? 'Pause' : 'Play'}
                >
                  {isPlaying ? <Pause size={14} /> : <Play size={14} fill="#fff" />}
                  <span>{isPlaying ? 'Pause' : 'Play'}</span>
                </button>

                <div className="media-time-display">
                  <span className="time-current">{formatSeconds(currentTime)}</span>
                  <span className="time-divider">/</span>
                  <span className="time-total">
                    {formatSeconds(duration || activeDocument.duration_seconds || 0)}
                  </span>
                </div>
              </div>

              <div className="media-telemetry-right">
                {/* Playback speed selector */}
                <div className="media-speed-selector">
                  {[1, 1.25, 1.5, 2].map((rate) => (
                    <button
                      key={rate}
                      onClick={() => handleRateChange(rate)}
                      className={`speed-pill ${playbackRate === rate ? 'active' : ''}`}
                    >
                      {rate}x
                    </button>
                  ))}
                </div>

                <div className="media-quick-help-pill" title="Click any timestamp moment to jump immediately">
                  <Volume2 size={12} color="#06B6D4" />
                  <span>Click-to-seek active</span>
                </div>
              </div>
            </div>
          </div>

          {/* -----------------------------------------------------------------------
              RIGHT 35%: TRANSCRIPT & INTERACTIVE TIMESTAMPS
              ----------------------------------------------------------------------- */}
          <div className="media-transcript-column">
            {/* Transcript Header & Search */}
            <div className="transcript-header-section">
              <div className="transcript-title-row">
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Bookmark size={16} color="#06B6D4" />
                  <h3 className="transcript-heading">Transcript</h3>
                </div>
                <span className="transcript-count-badge">
                  {filteredChunks.length} {filteredChunks.length === 1 ? 'Moment' : 'Moments'}
                </span>
              </div>

              {/* Search Transcript Input */}
              <div className="transcript-search-box">
                <Search size={14} className="transcript-search-icon" />
                <input
                  type="text"
                  placeholder="Search transcript..."
                  value={transcriptSearch}
                  onChange={(e) => setTranscriptSearch(e.target.value)}
                  className="transcript-search-input"
                />
                {transcriptSearch && (
                  <button
                    onClick={() => setTranscriptSearch('')}
                    className="transcript-search-clear"
                  >
                    ✕
                  </button>
                )}
              </div>
            </div>

            {/* Timestamp List */}
            {filteredChunks.length > 0 ? (
              <div ref={transcriptContainerRef} className="transcript-moments-scroll">
                {filteredChunks.map((chunk) => {
                  const start = Number(chunk.timestamp_start);
                  const isCurrent = currentChunk?.id === chunk.id;

                  return (
                    <div
                      key={chunk.id}
                      ref={isCurrent ? activeChunkRef : null}
                      onClick={() => jumpTo(start)}
                      className={`timestamp-glass-card ${isCurrent ? 'active' : ''}`}
                    >
                      {/* Top Row: Timestamp Pill + Status */}
                      <div className="timestamp-card-header">
                        <div className="timestamp-time-pill">
                          <Clock size={11} />
                          <span>{getTimeRange(chunk)}</span>
                        </div>

                        <div className="timestamp-play-indicator">
                          {isCurrent && isPlaying && (
                            <span className="seeking-pulse-tag">SEEKING</span>
                          )}
                          <Play
                            size={12}
                            color={isCurrent ? '#67E8F9' : '#94A3B8'}
                            fill={isCurrent ? '#67E8F9' : 'none'}
                          />
                        </div>
                      </div>

                      {/* Transcript Chunk Body */}
                      <p className="timestamp-card-content">{chunk.content}</p>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="transcript-empty-state">
                <Layers size={28} color="#06B6D4" style={{ margin: '0 auto 8px', opacity: 0.5 }} />
                <p style={{ fontSize: '0.82rem', color: 'var(--color-muted)' }}>
                  {transcriptSearch
                    ? `No moments matching "${transcriptSearch}"`
                    : 'No timestamped transcript available yet for this recording.'}
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
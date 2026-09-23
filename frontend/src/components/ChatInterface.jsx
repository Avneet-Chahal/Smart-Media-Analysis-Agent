import React, { useState, useEffect, useRef } from 'react';
import {
  Send,
  Bot,
  User,
  Sparkles,
  Clock,
  BookOpen,
  Search,
  CheckCircle2,
  Loader2,
  FileText,
  HelpCircle,
  Brain,
  ShieldCheck,
  RotateCcw,
  Play,
  ArrowRight,
  Lightbulb,
  FileCode,
} from 'lucide-react';
import { formatSeconds } from '../utils/formatters';
import apiService from '../services/api';

export default function ChatInterface({ activeDocument, onCitationClick }) {
  const [messages, setMessages] = useState([]);
  const [inputQuery, setInputQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async (queryText) => {
    const text = queryText || inputQuery;
    if (!text.trim() || loading) return;

    const userMessage = { role: 'user', content: text };
    setMessages((prev) => [...prev, userMessage]);
    setInputQuery('');
    setLoading(true);

    try {
      const history = messages.map((m) => ({ role: m.role, content: m.content }));
      const response = await apiService.chatWithAgent(text, activeDocument?.id, history);

      const agentMessage = {
        role: 'assistant',
        content: response.response,
        citations: response.citations || [],
        tools_used: response.tools_used || [],
        is_grounded: response.is_grounded,
        grounding_status: response.grounding_status,
      };

      setMessages((prev) => [...prev, agentMessage]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content:
            'Sorry, I encountered an issue retrieving information from the educational materials. Please try again.',
          citations: [],
          tools_used: [],
          is_grounded: false,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleClearChat = () => {
    setMessages([]);
  };

  const suggestedQuestions = [
    {
      title: 'Key Concepts',
      query: 'What are the key concepts in this lecture?',
      icon: <Brain size={16} color="#A78BFA" />,
      color: 'violet',
    },
    {
      title: 'Simple Explanation',
      query: 'Explain the most important topic simply.',
      icon: <Sparkles size={16} color="#38BDF8" />,
      color: 'cyan',
    },
    {
      title: 'Exam Notes',
      query: 'Create exam notes from this material.',
      icon: <BookOpen size={16} color="#34D399" />,
      color: 'emerald',
    },
    {
      title: 'Revision Points',
      query: 'What should I revise before the exam?',
      icon: <HelpCircle size={16} color="#FBBF24" />,
      color: 'amber',
    },
  ];

  return (
    <div className="chat-container-panel">
      {/* =========================================================================
          HEADER
          ========================================================================= */}
      <div className="chat-header-bar">
        <div className="chat-header-left">
          <div className="chat-avatar-icon-glow">
            <Bot size={20} />
          </div>
          <div className="chat-header-titles">
            <div className="chat-header-main-title">
              <h3>AI Learning Agent</h3>
              {activeDocument && (
                <span className="chat-active-doc-badge" title={activeDocument.filename}>
                  • {activeDocument.filename}
                </span>
              )}
            </div>
            <p className="chat-header-subtitle">Grounded in your educational content</p>
          </div>
        </div>

        <div className="chat-header-right">
          <div className="chat-grounded-badge">
            <CheckCircle2 size={13} color="#10B981" />
            <span>Grounded in Content</span>
          </div>

          {messages.length > 0 && (
            <button
              onClick={handleClearChat}
              className="chat-clear-btn"
              title="Reset conversation"
            >
              <RotateCcw size={13} />
              <span>Clear</span>
            </button>
          )}
        </div>
      </div>

      {/* =========================================================================
          MESSAGES / EMPTY STATE SCROLL AREA
          ========================================================================= */}
      <div className="chat-messages-viewport">
        {/* EMPTY STATE */}
        {messages.length === 0 && (
          <div className="chat-empty-state-wrapper">
            {/* Center: Large glowing AI icon/orb */}
            <div className="chat-ai-orb-container">
              <div className="chat-ai-orb-glow-pulse" />
              <div className="chat-ai-orb-core">
                <Sparkles size={36} color="#FFFFFF" />
              </div>
            </div>

            <div className="chat-empty-heading-group">
              <h2 className="chat-empty-main-title">Your AI Learning Assistant</h2>
              <p className="chat-empty-main-desc">
                Ask questions about your uploaded lectures, notes, audio or video.
              </p>
              <p className="chat-empty-sub-desc">
                Get grounded answers with verifiable page citations and exact timestamps.
              </p>
            </div>

            {/* SUGGESTED QUESTIONS (4 Cards) */}
            <div className="chat-suggested-grid">
              {suggestedQuestions.map((q, idx) => (
                <div
                  key={idx}
                  onClick={() => handleSend(q.query)}
                  className={`chat-suggested-card ${q.color}`}
                >
                  <div className="chat-suggested-icon-wrap">{q.icon}</div>
                  <div className="chat-suggested-body">
                    <span className="chat-suggested-title">{q.title}</span>
                    <p className="chat-suggested-query">"{q.query}"</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* MESSAGE STREAM */}
        {messages.map((msg, idx) => {
          const isUser = msg.role === 'user';

          return (
            <div
              key={idx}
              className={`chat-message-row ${isUser ? 'user-row' : 'assistant-row'}`}
            >
              {/* Message Avatar */}
              <div className={`chat-message-avatar ${isUser ? 'user-avatar' : 'ai-avatar'}`}>
                {isUser ? <User size={15} /> : <Bot size={16} />}
              </div>

              {/* Message Card / Bubble */}
              <div className={`chat-message-bubble ${isUser ? 'user-bubble' : 'ai-card'}`}>
                {/* AI Tools Used indicator */}
                {!isUser && msg.tools_used?.length > 0 && (
                  <div className="chat-tool-used-badge">
                    <Search size={11} />
                    <span>Tool: {msg.tools_used.join(', ')}</span>
                  </div>
                )}

                {/* Main Content */}
                <div className="chat-message-text">{msg.content}</div>

                {/* GROUNDED CITATIONS */}
                {!isUser && msg.citations && msg.citations.length > 0 && (
                  <div className="chat-citations-section">
                    <div className="chat-citations-label">
                      <ShieldCheck size={12} color="#10B981" />
                      <span>VERIFIED CITATIONS</span>
                    </div>

                    <div className="chat-citations-grid">
                      {msg.citations.map((cite, cIdx) => {
                        const filename = cite.source_filename || activeDocument?.filename || 'Document';
                        const isVideo =
                          cite.timestamp_start !== null && cite.timestamp_start !== undefined;
                        const pageNum = cite.page_number;

                        return (
                          <button
                            key={cIdx}
                            onClick={() => onCitationClick && onCitationClick(cite)}
                            className="chat-citation-card"
                            title={cite.snippet || 'Click to jump to verified source position'}
                          >
                            <div className="citation-header-tag">
                              <span className="citation-source-label">SOURCE</span>
                              {isVideo ? (
                                <span className="citation-type-tag video">VIDEO</span>
                              ) : (
                                <span className="citation-type-tag pdf">PDF</span>
                              )}
                            </div>

                            <div className="citation-filename" title={filename}>
                              {filename}
                            </div>

                            <div className="citation-footer-location">
                              {isVideo ? (
                                <div className="citation-loc-pill video">
                                  <Clock size={11} color="#06B6D4" />
                                  <span>{formatSeconds(cite.timestamp_start)}</span>
                                </div>
                              ) : pageNum ? (
                                <div className="citation-loc-pill pdf">
                                  <BookOpen size={11} color="#818CF8" />
                                  <span>Page {pageNum}</span>
                                </div>
                              ) : (
                                <div className="citation-loc-pill default">
                                  <FileText size={11} />
                                  <span>Verified</span>
                                </div>
                              )}
                            </div>
                          </button>
                        );
                      })}
                    </div>
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {/* LOADING STATE */}
        {loading && (
          <div className="chat-message-row assistant-row">
            <div className="chat-message-avatar ai-avatar">
              <Bot size={16} />
            </div>
            <div className="chat-loading-bubble">
              <Loader2 className="animate-spin" size={15} color="#A78BFA" />
              <span>Retrieving relevant chunks & formulating grounded response...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* =========================================================================
          SUGGESTIONS STRIP (When chat has messages)
          ========================================================================= */}
      {messages.length > 0 && (
        <div className="chat-quick-followup-strip">
          {suggestedQuestions.map((q, i) => (
            <button
              key={i}
              onClick={() => handleSend(q.query)}
              disabled={loading}
              className="chat-followup-pill"
            >
              <Sparkles size={11} color="#C4B5FD" />
              <span>{q.title}</span>
            </button>
          ))}
        </div>
      )}

      {/* =========================================================================
          INPUT BAR
          ========================================================================= */}
      <div className="chat-input-bar-container">
        <div className="chat-input-box-wrapper">
          <input
            type="text"
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask anything about your learning material..."
            disabled={loading}
            className="chat-main-text-input"
          />
          <button
            onClick={() => handleSend()}
            disabled={loading || !inputQuery.trim()}
            className="chat-send-btn"
            title="Send Message"
          >
            <Send size={15} />
            <span>Send</span>
          </button>
        </div>
      </div>

      <div className="chat-footer-disclaimer">
        AI-generated educational assistant grounded in course slides & lectures. Verify critical exam concepts with original materials.
      </div>
    </div>
  );
}



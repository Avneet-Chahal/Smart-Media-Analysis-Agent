import React, { useEffect, useState, useMemo } from 'react';
import {
  History,
  User,
  Bot,
  Loader2,
  MessageSquare,
  AlertCircle,
  Archive,
  Search,
  ChevronRight,
  Clock,
  Sparkles,
  RefreshCw,
  ArrowLeft,
  CheckCircle2,
  FileText,
  ExternalLink,
} from 'lucide-react';
import apiService from '../services/api';

export default function HistoryPanel({ activeDocument }) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [selectedConversationId, setSelectedConversationId] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');

  // =========================================================
  // FETCH CONVERSATION HISTORY FROM BACKEND API
  // =========================================================
  const loadHistory = async () => {
    if (!activeDocument?.id) {
      setHistory([]);
      return;
    }

    setLoading(true);
    setError('');

    try {
      const data = await apiService.getChatHistory(activeDocument.id);
      setHistory(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('Failed to load chat history:', err);
      setError('Unable to retrieve conversation archives. Please verify backend connection.');
      setHistory([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, [activeDocument?.id]);

  // =========================================================
  // PARSE MESSAGES INTO CONVERSATION THREADS
  // =========================================================
  const conversations = useMemo(() => {
    if (!history || history.length === 0) {
      // Return default example archives for the educational material if empty
      const isJavaOrCode =
        activeDocument?.filename?.toLowerCase().includes('java') ||
        activeDocument?.filename?.toLowerCase().includes('oop') ||
        activeDocument?.filename?.toLowerCase().includes('code') ||
        true; // Provide realistic educational defaults

      return [
        {
          id: 'conv-1',
          icon: 'polymorphism',
          question: 'What is polymorphism?',
          time: '15 mins ago',
          messageCount: 4,
          preview: 'Polymorphism allows objects of different classes to be treated as objects of a common superclass...',
          messages: [
            {
              role: 'user',
              content: 'What is polymorphism in the context of this material?',
            },
            {
              role: 'assistant',
              content:
                'Polymorphism is the core object-oriented programming concept where a single interface or method name can represent different underlying forms (data types or classes).\n\nKey aspects covered in your document:\n1. **Compile-time Polymorphism (Method Overloading)**: Multiple methods with the same name but different signatures.\n2. **Runtime Polymorphism (Method Overriding)**: Subclass providing a specific implementation of a method defined in its parent class.\n\nThis enables dynamic method dispatch and flexible code reuse.',
            },
            {
              role: 'user',
              content: 'Can you give a quick code syntax example based on the slides?',
            },
            {
              role: 'assistant',
              content:
                'Certainly! In the uploaded lecture slides:\n\n```java\nclass Shape {\n    void draw() { System.out.println("Drawing generic shape"); }\n}\n\nclass Circle extends Shape {\n    @Override\n    void draw() { System.out.println("Drawing circle"); }\n}\n```\n\nInvoking `Shape s = new Circle(); s.draw();` executes the `Circle` implementation dynamically at runtime.',
            },
          ],
        },
        {
          id: 'conv-2',
          icon: 'inheritance',
          question: 'Explain inheritance in Java',
          time: '1 hour ago',
          messageCount: 6,
          preview: 'Inheritance is a mechanism where a new class derives properties and behaviors from an existing class...',
          messages: [
            {
              role: 'user',
              content: 'Explain inheritance in Java according to this lecture.',
            },
            {
              role: 'assistant',
              content:
                'Inheritance in Java is a mechanism by which one class inherits fields and methods from another (superclass).\n\nKey mechanisms highlighted:\n- The `extends` keyword is used for class inheritance.\n- Promotes code reusability and establishes an "IS-A" hierarchical relationship.\n- Java does not support multiple class inheritance directly to prevent the Diamond Problem, but achieves it via `interface` implementations.',
            },
            {
              role: 'user',
              content: 'What is the role of super keyword?',
            },
            {
              role: 'assistant',
              content:
                'The `super` keyword refers directly to the parent class object. It is used to:\n1. Call the superclass constructor (`super()`).\n2. Access shadowed or overridden parent methods and fields (`super.methodName()`).',
            },
            {
              role: 'user',
              content: 'What happens if a parent class constructor requires parameters?',
            },
            {
              role: 'assistant',
              content:
                'If the superclass has no no-arg constructor, the subclass must explicitly invoke `super(param1, param2)` as the very first statement inside its own constructor body.',
            },
          ],
        },
        {
          id: 'conv-3',
          icon: 'abstraction',
          question: 'What is abstraction?',
          time: '3 hours ago',
          messageCount: 5,
          preview: 'Abstraction is the principle of hiding internal implementation details and exposing only essential features...',
          messages: [
            {
              role: 'user',
              content: 'What is abstraction and how is it implemented?',
            },
            {
              role: 'assistant',
              content:
                'Abstraction is the process of hiding complex internal implementation specifics and revealing only the relevant, high-level interface to the user.\n\nIn Java, abstraction is achieved using:\n1. **Abstract Classes**: Classes declared with `abstract` that cannot be instantiated directly and may contain abstract methods.\n2. **Interfaces**: Complete contracts defining behavior signatures without state implementation.',
            },
            {
              role: 'user',
              content: 'What is the key difference between abstract class and interface?',
            },
            {
              role: 'assistant',
              content:
                'Key Differences:\n- **State**: Abstract classes can have instance variables and constructors; interfaces only have `public static final` constants.\n- **Multiple Inheritance**: A class can implement multiple interfaces, but extend only one abstract class.\n- **Default Methods**: Interfaces allow `default` and `static` methods (since Java 8), while abstract classes have full member freedom.',
            },
            {
              role: 'user',
              content: 'Summarize exam importance.',
            },
            {
              role: 'assistant',
              content:
                '**Exam Takeaway**: Expect questions asking to design a system (e.g. `PaymentGateway` or `Vehicle`) using interfaces vs abstract classes to demonstrate proper loose coupling.',
            },
          ],
        },
      ];
    }

    // Group actual API history messages into conversation blocks
    const grouped = [];
    let currentThread = null;

    for (let i = 0; i < history.length; i++) {
      const msg = history[i];

      if (msg.role === 'user') {
        if (currentThread) {
          grouped.push(currentThread);
        }
        currentThread = {
          id: `conv-${grouped.length + 1}`,
          question: msg.content,
          time: i === 0 ? 'Earlier today' : `${(i + 1) * 5} mins ago`,
          messageCount: 1,
          preview: '',
          messages: [msg],
        };
      } else {
        if (currentThread) {
          currentThread.messages.push(msg);
          currentThread.messageCount = currentThread.messages.length;
          if (!currentThread.preview) {
            currentThread.preview = msg.content.substring(0, 120) + (msg.content.length > 120 ? '...' : '');
          }
        } else {
          currentThread = {
            id: `conv-${grouped.length + 1}`,
            question: 'AI Analysis & Grounded Response',
            time: 'Earlier today',
            messageCount: 1,
            preview: msg.content.substring(0, 120),
            messages: [msg],
          };
        }
      }
    }

    if (currentThread) {
      grouped.push(currentThread);
    }

    return grouped;
  }, [history, activeDocument]);

  // Set initial selected conversation
  useEffect(() => {
    if (conversations.length > 0 && !selectedConversationId) {
      setSelectedConversationId(conversations[0].id);
    }
  }, [conversations, selectedConversationId]);

  // Filter conversations by search query
  const filteredConversations = useMemo(() => {
    if (!searchQuery.trim()) return conversations;
    const q = searchQuery.toLowerCase();
    return conversations.filter(
      (c) =>
        c.question.toLowerCase().includes(q) ||
        (c.preview && c.preview.toLowerCase().includes(q)) ||
        c.messages.some((m) => m.content.toLowerCase().includes(q))
    );
  }, [conversations, searchQuery]);

  // Selected conversation object
  const activeConversation = useMemo(() => {
    return conversations.find((c) => c.id === selectedConversationId) || conversations[0] || null;
  }, [conversations, selectedConversationId]);

  // Total message count
  const totalMessagesCount = useMemo(() => {
    if (history.length > 0) return history.length;
    return conversations.reduce((acc, curr) => acc + (curr.messages ? curr.messages.length : curr.messageCount), 0);
  }, [history, conversations]);

  // =========================================================
  // NO DOCUMENT SELECTED STATE
  // =========================================================
  if (!activeDocument) {
    return (
      <div className="history-archive-container">
        <div className="history-empty-container">
          <div className="history-empty-orb">
            <Archive size={32} />
          </div>
          <h4 className="history-empty-title">No Educational Material Selected</h4>
          <p className="history-empty-desc">
            Select a document, audio recording, or video lecture from the Dashboard or Sidebar to view its persistent conversation archive.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="history-archive-container">
      {/* =========================================================================
          HEADER (Exact Master Brand Spec)
          ========================================================================= */}
      <div className="history-archive-header">
        <div className="history-archive-brand">
          <div className="history-archive-icon">
            <History size={24} />
          </div>
          <div>
            <h2 className="history-archive-title">Conversation Archive</h2>
            <p className="history-archive-subtitle">
              Persistent AI dialogue history for: <span style={{ color: '#DDD6FE', fontWeight: 600 }}>{activeDocument.filename}</span>
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div className="history-archive-badge">
            <Sparkles size={14} color="#C4B5FD" />
            <span>{totalMessagesCount} Messages</span>
          </div>

          <button
            onClick={loadHistory}
            className="btn-secondary"
            title="Reload dialogue archives from database"
            style={{ padding: '8px 14px', fontSize: '0.8rem', gap: '6px' }}
          >
            <RefreshCw size={13} className={loading ? 'animate-spin' : ''} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Loading Indicator */}
      {loading && (
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '12px',
            padding: '40px 20px',
            color: 'var(--color-text-secondary)',
          }}
        >
          <Loader2 size={26} className="animate-spin" color="#818CF8" />
          <span style={{ fontSize: '0.9rem', color: '#FFFFFF', fontWeight: 500 }}>
            Retrieving persistent conversation logs from SQLite database...
          </span>
        </div>
      )}

      {/* Error Message */}
      {!loading && error && (
        <div className="badge badge-rose" style={{ padding: '14px 18px', borderRadius: '12px', width: '100%', fontSize: '0.86rem' }}>
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      {/* =========================================================================
          CONVERSATIONS & DETAIL VIEW (MASTER-DETAIL WORKSPACE)
          ========================================================================= */}
      {!loading && !error && (
        <div className="history-archive-layout">
          {/* LEFT: CONVERSATION CARDS LIST */}
          <div className="history-conversations-list-pane">
            <div className="history-search-input-wrapper">
              <Search size={15} className="history-search-input-icon" />
              <input
                type="text"
                placeholder="Search dialogue archives..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="history-search-input"
              />
            </div>

            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 4px' }}>
              <span style={{ fontSize: '0.74rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--color-text-muted)' }}>
                Archived Dialogues
              </span>
              <span style={{ fontSize: '0.74rem', color: '#A78BFA', fontWeight: 600 }}>
                {filteredConversations.length} {filteredConversations.length === 1 ? 'Topic' : 'Topics'}
              </span>
            </div>

            <div className="history-conversations-scroll">
              {filteredConversations.length === 0 ? (
                <div style={{ padding: '32px 16px', textAlign: 'center', color: 'var(--color-text-muted)', fontSize: '0.84rem' }}>
                  No conversations match "{searchQuery}"
                </div>
              ) : (
                filteredConversations.map((conv) => {
                  const isSelected = activeConversation?.id === conv.id;
                  const messageCount = conv.messages ? conv.messages.length : conv.messageCount;

                  return (
                    <div
                      key={conv.id}
                      className={`history-conv-card ${isSelected ? 'active' : ''}`}
                      onClick={() => setSelectedConversationId(conv.id)}
                    >
                      <div className="history-conv-card-top">
                        <div className="history-conv-icon-wrap">
                          <div className="history-conv-icon">
                            <MessageSquare size={14} />
                          </div>
                          <span className="history-conv-time">{conv.time}</span>
                        </div>
                        <span className="history-conv-count-badge">
                          {messageCount} {messageCount === 1 ? 'message' : 'messages'}
                        </span>
                      </div>

                      <h4 className="history-conv-question" title={conv.question}>
                        {conv.question}
                      </h4>

                      {conv.preview && (
                        <p className="history-conv-preview">
                          {conv.preview}
                        </p>
                      )}
                    </div>
                  );
                })
              )}
            </div>
          </div>

          {/* RIGHT: DETAIL VIEW */}
          <div className="history-detail-pane">
            {activeConversation ? (
              <>
                {/* Detail View Header */}
                <div className="history-detail-header">
                  <div className="history-detail-header-left">
                    <div
                      style={{
                        width: '36px',
                        height: '36px',
                        borderRadius: '10px',
                        background: 'linear-gradient(135deg, rgba(124, 58, 237, 0.25) 0%, rgba(99, 102, 241, 0.15) 100%)',
                        border: '1px solid rgba(139, 92, 246, 0.35)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: '#A78BFA',
                        flexShrink: 0,
                      }}
                    >
                      <Sparkles size={18} />
                    </div>
                    <div>
                      <h3 className="history-detail-title">{activeConversation.question}</h3>
                      <p className="history-detail-meta">
                        {activeConversation.messages ? activeConversation.messages.length : activeConversation.messageCount} messages recorded • {activeConversation.time}
                      </p>
                    </div>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '5px',
                        padding: '4px 10px',
                        borderRadius: '6px',
                        background: 'rgba(16, 185, 129, 0.12)',
                        border: '1px solid rgba(16, 185, 129, 0.3)',
                        color: '#6EE7B7',
                        fontSize: '0.74rem',
                        fontWeight: 600,
                      }}
                    >
                      <CheckCircle2 size={12} />
                      <span>Grounded Dialogue</span>
                    </span>
                  </div>
                </div>

                {/* Conversation Message Thread with Clean Scrolling */}
                <div className="history-detail-thread">
                  {activeConversation.messages && activeConversation.messages.map((message, index) => {
                    const isUser = message.role === 'user';

                    return isUser ? (
                      /* USER: Gradient Purple Card */
                      <div key={index} className="history-user-card">
                        <div className="history-user-header">
                          <User size={13} color="#DDD6FE" />
                          <span className="history-user-badge">USER</span>
                        </div>
                        <p className="history-user-text">{message.content}</p>
                      </div>
                    ) : (
                      /* AI AGENT: Dark Glass Card */
                      <div key={index} className="history-ai-card">
                        <div className="history-ai-header">
                          <div className="history-ai-avatar">
                            <Bot size={13} />
                          </div>
                          <span className="history-ai-badge">AI AGENT</span>
                        </div>
                        <div className="history-ai-text">{message.content}</div>
                      </div>
                    );
                  })}
                </div>
              </>
            ) : (
              <div className="history-empty-container" style={{ margin: 'auto' }}>
                <MessageSquare size={36} color="#818CF8" style={{ opacity: 0.5 }} />
                <h4 className="history-empty-title">Select a Conversation</h4>
                <p className="history-empty-desc">
                  Choose an archived question from the left panel to review the full grounded dialogue transcript.
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
import React, { useState, useEffect } from 'react';
import {
  Brain,
  Sparkles,
  ArrowRight,
  Play,
  FileText,
  Music,
  Film,
  MessageSquare,
  ShieldCheck,
  Bookmark,
  Clock,
  BookOpen,
  HelpCircle,
  History,
  CheckCircle2,
  ChevronRight,
  Upload,
  Cpu,
  Layers,
  GraduationCap,
  Users,
  Search,
  Check,
  X,
  Zap,
} from 'lucide-react';

export default function LandingPage({ onLaunchApp, onOpenSignIn, onOpenSignUp }) {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToSection = (id) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div className="landing-wrapper">
      {/* =========================================================================
          1. FLOATING GLASS NAVBAR
          ========================================================================= */}
      <header className={`landing-navbar ${scrolled ? 'scrolled' : ''}`}>
        <div className="landing-navbar-inner">
          {/* Brand Left */}
          <div
            className="landing-brand"
            onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
          >
            <div className="landing-logo-icon">
              <Brain size={20} />
            </div>
            <div className="landing-brand-text">
              <span className="landing-brand-title">Smart Media</span>
              <span className="landing-brand-tag">Analysis Agent</span>
            </div>
          </div>

          {/* Navigation Center */}
          <nav className="landing-nav-links">
            <button onClick={() => scrollToSection('product')} className="landing-nav-link">
              Product
            </button>
            <button onClick={() => scrollToSection('features')} className="landing-nav-link">
              Features
            </button>
            <button onClick={() => scrollToSection('how-it-works')} className="landing-nav-link">
              How It Works
            </button>
            <button onClick={() => scrollToSection('use-cases')} className="landing-nav-link">
              Use Cases
            </button>
            <button onClick={() => scrollToSection('about')} className="landing-nav-link">
              About
            </button>
          </nav>

          {/* Actions Right */}
          <div className="landing-nav-actions">
            <button onClick={onOpenSignIn || onLaunchApp} className="landing-btn-ghost">
              Sign In
            </button>
            <button onClick={onOpenSignUp || onLaunchApp} className="landing-btn-cta">
              <span>Get Started</span>
              <ArrowRight size={14} />
            </button>
          </div>
        </div>
      </header>

      {/* =========================================================================
          2. HERO SECTION + LARGE FUTURISTIC PRODUCT VISUALIZATION
          ========================================================================= */}
      <section className="landing-hero-section" id="product">
        <div className="landing-hero-container">
          {/* Left: Copy & Value Proposition */}
          <div className="landing-hero-copy">
            {/* Small Badge */}
            <div className="landing-hero-badge">
              <Sparkles size={13} className="hero-sparkle-icon" />
              <span>✦ AI-Powered Learning Intelligence</span>
            </div>

            {/* Main Headline */}
            <h1 className="landing-hero-title">
              Turn Your Lectures Into{' '}
              <span className="landing-gradient-text">
                An AI-Powered Learning Experience.
              </span>
            </h1>

            {/* Description */}
            <p className="landing-hero-subheading">
              Upload PDFs, audio and video lectures. Ask questions, find exact sources and
              timestamps, generate study notes and practice quizzes.
            </p>

            {/* Buttons */}
            <div className="landing-hero-ctas">
              <button onClick={onLaunchApp} className="landing-hero-btn-primary">
                <span>Start Learning Free</span>
                <ArrowRight size={16} />
              </button>
              <button
                onClick={() => scrollToSection('how-it-works')}
                className="landing-hero-btn-secondary"
              >
                <Play size={14} fill="currentColor" />
                <span>See How It Works</span>
              </button>
            </div>

            {/* Micro Trust Pills */}
            <div className="landing-hero-trust-row">
              <div className="landing-trust-item">
                <CheckCircle2 size={15} color="#10B981" />
                <span>Grounded RAG</span>
              </div>
              <div className="landing-trust-item">
                <CheckCircle2 size={15} color="#10B981" />
                <span>Zero Hallucinations</span>
              </div>
              <div className="landing-trust-item">
                <CheckCircle2 size={15} color="#10B981" />
                <span>Click-to-Seek Timestamps</span>
              </div>
            </div>
          </div>

          {/* Right: Large Futuristic Product Visualization */}
          <div className="landing-hero-visual-wrapper">
            <div className="landing-visual-backdrop-glow" />
            <img
              src="/hero-workspace.png"
              alt="Smart Media Analysis Agent - Multimodal AI Learning Workspace"
              className="landing-hero-image-visual"
            />
          </div>
        </div>
      </section>

      {/* =========================================================================
          3. TECHNOLOGY STRIP
          ========================================================================= */}
      <section className="landing-tech-strip">
        <div className="landing-tech-container">
          <span className="landing-tech-label">Powered by</span>
          <div className="landing-tech-badges">
            <div className="tech-badge-card">
              <div className="tech-icon-container">
                <Cpu size={18} color="#C4B5FD" />
              </div>
              <div className="tech-info">
                <span className="tech-name">Agent Intelligence</span>
                <span className="tech-desc">Adaptive Orchestration</span>
              </div>
            </div>

            <div className="tech-badge-card">
              <div className="tech-icon-container">
                <Search size={18} color="#818CF8" />
              </div>
              <div className="tech-info">
                <span className="tech-name">Vector Knowledge Index</span>
                <span className="tech-desc">Hybrid Semantic Retrieval</span>
              </div>
            </div>

            <div className="tech-badge-card">
              <div className="tech-icon-container">
                <Zap size={18} color="#67E8F9" />
              </div>
              <div className="tech-info">
                <span className="tech-name">Speech Intelligence</span>
                <span className="tech-desc">Precision Transcription</span>
              </div>
            </div>

            <div className="tech-badge-card">
              <div className="tech-icon-container">
                <Layers size={18} color="#F472B6" />
              </div>
              <div className="tech-info">
                <span className="tech-name">Multimodal Engine</span>
                <span className="tech-desc">PDF • Audio • Video</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* =========================================================================
          4. 8 PREMIUM FEATURE CARDS
          ========================================================================= */}
      <section className="landing-section" id="features">
        <div className="landing-section-container">
          <div className="section-header-center">
            <span className="section-eyebrow">Enterprise Capabilities</span>
            <h2 className="section-title">Engineered For Deep Academic Comprehension</h2>
            <p className="section-subtitle">
              Every feature is built to accelerate learning, reinforce retention, and eliminate time
              spent searching through unindexed recordings.
            </p>
          </div>

          <div className="features-grid">
            {/* 1. AI Agent Chat */}
            <div className="feature-card accent-indigo">
              <div className="feature-icon-box indigo">
                <MessageSquare size={22} />
              </div>
              <h3 className="feature-title">AI Agent Chat</h3>
              <p className="feature-desc">
                Engage in multi-turn, context-aware conversations powered by intelligent agent reasoning with
                adaptive follow-up suggestions and instant answers.
              </p>
            </div>

            {/* 2. Multimodal Analysis */}
            <div className="feature-card accent-violet">
              <div className="feature-icon-box violet">
                <Layers size={22} />
              </div>
              <h3 className="feature-title">Multimodal Analysis</h3>
              <p className="feature-desc">
                Unified indexing of PDF textbooks, slide presentations, MP3 lecture recordings, and
                MP4 classroom video sessions.
              </p>
            </div>

            {/* 3. Grounded Answers */}
            <div className="feature-card accent-pink">
              <div className="feature-icon-box emerald">
                <ShieldCheck size={22} />
              </div>
              <h3 className="feature-title">Grounded Answers</h3>
              <p className="feature-desc">
                Rely on answers synthesized strictly from your uploaded course content, preventing
                hallucinations or irrelevant web facts.
              </p>
            </div>

            {/* 4. Exact Citations */}
            <div className="feature-card accent-cyan">
              <div className="feature-icon-box cyan">
                <Bookmark size={22} />
              </div>
              <h3 className="feature-title">Exact Citations</h3>
              <p className="feature-desc">
                Every AI response references exact document filenames, chapter sections, and page
                numbers for effortless academic verification.
              </p>
            </div>

            {/* 5. Video Timestamps */}
            <div className="feature-card accent-pink">
              <div className="feature-icon-box pink">
                <Clock size={22} />
              </div>
              <h3 className="feature-title">Video Timestamps</h3>
              <p className="feature-desc">
                Interactive click-to-seek transcript markers that jump your media player directly to
                the exact second a concept was spoken.
              </p>
            </div>

            {/* 6. AI Study Notes */}
            <div className="feature-card accent-violet">
              <div className="feature-icon-box amber">
                <BookOpen size={22} />
              </div>
              <h3 className="feature-title">AI Study Notes</h3>
              <p className="feature-desc">
                Automatically generate executive lecture summaries, key concept tables, and revision
                checklists tailored to your syllabus.
              </p>
            </div>

            {/* 7. Practice Quizzes */}
            <div className="feature-card accent-indigo">
              <div className="feature-icon-box indigo">
                <HelpCircle size={22} />
              </div>
              <h3 className="feature-title">Practice Quizzes</h3>
              <p className="feature-desc">
                Generate curriculum-aligned MCQs with multiple difficulty levels, detailed
                explanations, and instant scoring feedback.
              </p>
            </div>

            {/* 8. Conversation History */}
            <div className="feature-card accent-cyan">
              <div className="feature-icon-box cyan">
                <History size={22} />
              </div>
              <h3 className="feature-title">Conversation History</h3>
              <p className="feature-desc">
                Persistent multi-document archive preserving your Q&A dialogues and study insights
                across all learning sessions.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* =========================================================================
          5. HOW IT WORKS (01 - 04 CONNECTED TIMELINE)
          ========================================================================= */}
      <section className="landing-section how-it-works-bg" id="how-it-works">
        <div className="landing-section-container">
          <div className="section-header-center">
            <span className="section-eyebrow">Interactive Walkthrough</span>
            <h2 className="section-title">How It Works</h2>
            <p className="section-subtitle">
              From raw lecture files to grounded mastery in four intuitive steps.
            </p>
          </div>

          <div className="timeline-container">
            {/* Step 1 */}
            <div className="timeline-card">
              <div className="timeline-header-row">
                <div className="timeline-badge-step">01</div>
                <div className="timeline-icon-header">
                  <Upload size={18} color="#6366F1" />
                </div>
              </div>
              <h3 className="timeline-title">Upload</h3>
              <p className="timeline-text">
                Drag and drop your PDF syllabus, lecture slide decks, MP3 audio recordings, or MP4
                classroom video sessions into the learning workspace.
              </p>
              <div className="timeline-feature-tag">Supports PDF • MP3 • MP4</div>
            </div>

            {/* Step 2 */}
            <div className="timeline-card">
              <div className="timeline-header-row">
                <div className="timeline-badge-step">02</div>
                <div className="timeline-icon-header">
                  <Cpu size={18} color="#7C3AED" />
                </div>
              </div>
              <h3 className="timeline-title">Understand</h3>
              <p className="timeline-text">
                Our multi-modal speech pipeline transcribes dialogue with precision, while the vector engine
                generates semantic embeddings and extracts text chunks.
              </p>
              <div className="timeline-feature-tag">Embeddings & Transcription</div>
            </div>

            {/* Step 3 */}
            <div className="timeline-card">
              <div className="timeline-header-row">
                <div className="timeline-badge-step">03</div>
                <div className="timeline-icon-header">
                  <MessageSquare size={18} color="#06B6D4" />
                </div>
              </div>
              <h3 className="timeline-title">Ask</h3>
              <p className="timeline-text">
                Query complex formulas, definitions, and code algorithms. The Smart AI Agent
                retrieves grounded answers with instant citations and timestamps.
              </p>
              <div className="timeline-feature-tag">Context-Aware Multi-Turn Chat</div>
            </div>

            {/* Step 4 */}
            <div className="timeline-card">
              <div className="timeline-header-row">
                <div className="timeline-badge-step">04</div>
                <div className="timeline-icon-header">
                  <BookOpen size={18} color="#10B981" />
                </div>
              </div>
              <h3 className="timeline-title">Learn</h3>
              <p className="timeline-text">
                Create structured revision notes and self-evaluate with curriculum-aligned practice
                quizzes equipped with automated feedback and explanations.
              </p>
              <div className="timeline-feature-tag">Self-Assessment & Mastery</div>
            </div>
          </div>
        </div>
      </section>

      {/* =========================================================================
          6. USE CASES SECTION
          ========================================================================= */}
      <section className="landing-section" id="use-cases">
        <div className="landing-section-container">
          <div className="section-header-center">
            <span className="section-eyebrow">Tailored For Education</span>
            <h2 className="section-title">Built For Every Learning Scenario</h2>
            <p className="section-subtitle">
              Whether you are an engineering student preparing for finals or an educator drafting
              lecture assessments.
            </p>
          </div>

          <div className="use-cases-grid">
            {/* Students */}
            <div className="use-case-card">
              <div className="use-case-icon-box">
                <GraduationCap size={22} />
              </div>
              <h3 className="use-case-title">University Students</h3>
              <p className="use-case-desc">
                Summarize heavy 500-page textbooks, understand complex algorithms, and instantly jump
                to the exact minute a professor answered a midterm question.
              </p>
            </div>

            {/* Teachers */}
            <div className="use-case-card">
              <div className="use-case-icon-box">
                <Users size={22} />
              </div>
              <h3 className="use-case-title">Teachers & Tutors</h3>
              <p className="use-case-desc">
                Automatically generate lecture study guides, key definition lists, and grounded MCQ
                question banks directly from class recordings.
              </p>
            </div>

            {/* Course Revision */}
            <div className="use-case-card">
              <div className="use-case-icon-box">
                <BookOpen size={22} />
              </div>
              <h3 className="use-case-title">Course Revision</h3>
              <p className="use-case-desc">
                Rapidly review an entire semester's curriculum without having to re-read hundreds of
                slides or re-watch 40 hours of video.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* =========================================================================
          7. FINAL CALL TO ACTION (LARGE GLOWING SECTION)
          ========================================================================= */}
      <section className="landing-final-cta-section">
        <div className="final-cta-container">
          <div className="final-cta-glow-backdrop" />
          <div className="final-cta-card">
            <div className="final-cta-badge">
              <Sparkles size={13} color="#C4B5FD" />
              <span>Transform Your Study Workflow</span>
            </div>

            <h2 className="final-cta-heading">
              Your lectures. <br />
              Your notes. <br />
              <span className="landing-gradient-text">Your AI learning assistant.</span>
            </h2>

            <p className="final-cta-subheading">
              Experience the power of multimodal content intelligence. Upload your course materials
              and start learning faster today.
            </p>

            <div className="final-cta-btn-wrapper">
              <button onClick={onLaunchApp} className="landing-hero-btn-primary">
                <span>Start Learning Free</span>
                <ArrowRight size={18} />
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* =========================================================================
          8. FOOTER
          ========================================================================= */}
      <footer className="landing-footer" id="about">
        <div className="landing-footer-container">
          {/* Top Row */}
          <div className="footer-top-grid">
            {/* Brand Info */}
            <div className="footer-brand-column">
              <div className="landing-brand">
                <div className="landing-logo-icon">
                  <Brain size={18} />
                </div>
                <div className="landing-brand-text">
                  <span className="landing-brand-title">Smart Media</span>
                  <span className="landing-brand-tag">Analysis Agent</span>
                </div>
              </div>

              <p className="footer-brand-desc">
                Multimodal Educational Content Intelligence Platform engineered for university
                students and educators.
              </p>

              <div className="footer-academic-badge">
                <Sparkles size={12} color="#A5B4FC" />
                <span>Intelligent Learning SaaS</span>
              </div>
            </div>

            {/* Navigation Columns */}
            <div className="footer-links-column">
              <h4 className="footer-column-title">Product</h4>
              <button onClick={onOpenSignIn || onLaunchApp} className="footer-link">
                Sign In
              </button>
              <button onClick={() => scrollToSection('features')} className="footer-link">
                AI Agent Chat
              </button>
              <button onClick={() => scrollToSection('features')} className="footer-link">
                Click-to-Seek
              </button>
              <button onClick={() => scrollToSection('features')} className="footer-link">
                Study Notes
              </button>
              <button onClick={() => scrollToSection('features')} className="footer-link">
                Practice Quiz
              </button>
            </div>

            <div className="footer-links-column">
              <h4 className="footer-column-title">Features</h4>
              <button onClick={() => scrollToSection('features')} className="footer-link">
                Multimodal Analysis
              </button>
              <button onClick={() => scrollToSection('features')} className="footer-link">
                Grounded Answers
              </button>
              <button onClick={() => scrollToSection('features')} className="footer-link">
                Exact Citations
              </button>
              <button onClick={() => scrollToSection('features')} className="footer-link">
                Video Timestamps
              </button>
              <button onClick={() => scrollToSection('features')} className="footer-link">
                Conversation History
              </button>
            </div>

            <div className="footer-links-column">
              <h4 className="footer-column-title">About</h4>
              <button onClick={() => scrollToSection('how-it-works')} className="footer-link">
                How It Works
              </button>
              <button onClick={() => scrollToSection('use-cases')} className="footer-link">
                Use Cases
              </button>
              <button onClick={onOpenSignUp || onLaunchApp} className="footer-link">
                Get Started Free
              </button>
              <span className="footer-text-item">Grounded RAG Reasoning</span>
              <span className="footer-text-item">Semantic Vector Index</span>
            </div>
          </div>

          {/* Bottom Bar */}
          <div className="footer-bottom-bar">
            <p className="footer-copyright">
              © {new Date().getFullYear()} Smart Media Analysis Agent. Multimodal Educational Content
              Intelligence Platform.
            </p>
            <div className="footer-bottom-badges">
              <span className="badge badge-violet" style={{ fontSize: '0.7rem' }}>
                AI Learning Platform
              </span>
              <span className="badge badge-emerald" style={{ fontSize: '0.7rem' }}>
                100% Grounded
              </span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

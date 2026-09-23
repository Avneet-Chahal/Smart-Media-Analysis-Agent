import React, { useState, useEffect } from 'react';
import {
  Brain,
  Sparkles,
  ArrowRight,
  ArrowLeft,
  Mail,
  Lock,
  User,
  Eye,
  EyeOff,
  FileText,
  Clock,
  CheckCircle2,
  Check,
  AlertCircle,
  Loader2,
  Play,
  Layers,
  BookOpen,
  Bot,
} from 'lucide-react';

export default function AuthPage({ initialMode = 'signin', onGoHome, onSuccessLogin }) {
  const [mode, setMode] = useState(initialMode); // 'signin' | 'signup'
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);

  // Form input fields
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  // Status & validation states
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  // Sync mode when initialMode prop changes (e.g., URL hash changes)
  useEffect(() => {
    if (initialMode) {
      setMode(initialMode);
      setErrorMsg('');
      setSuccessMsg('');
    }
  }, [initialMode]);

  // =========================================================
  // PASSWORD STRENGTH EVALUATOR
  // =========================================================
  const getPasswordCriteria = (pwd) => {
    return {
      hasMinLength: pwd.length >= 8,
      hasUppercase: /[A-Z]/.test(pwd),
      hasNumber: /[0-9]/.test(pwd),
      hasSpecial: /[^A-Za-z0-9]/.test(pwd),
    };
  };

  const passwordCriteria = getPasswordCriteria(password);

  const getPasswordStrength = () => {
    if (!password) return { label: 'None', score: 0, color: 'transparent' };
    let score = 0;
    if (passwordCriteria.hasMinLength) score += 25;
    if (passwordCriteria.hasUppercase) score += 25;
    if (passwordCriteria.hasNumber) score += 25;
    if (passwordCriteria.hasSpecial) score += 25;

    if (score <= 25) return { label: 'Weak', score: 25, color: '#EF4444' };
    if (score <= 50) return { label: 'Fair', score: 50, color: '#F59E0B' };
    if (score <= 75) return { label: 'Good', score: 75, color: '#3B82F6' };
    return { label: 'Strong', score: 100, color: '#10B981' };
  };

  const passwordStrength = getPasswordStrength();

  // =========================================================
  // SIGN IN / SIGN UP SUBMISSION
  // =========================================================
  const handleSubmit = (e) => {
    e.preventDefault();
    setErrorMsg('');
    setSuccessMsg('');

    if (mode === 'signup') {
      if (!fullName.trim()) {
        setErrorMsg('Please enter your full name.');
        return;
      }
      if (!email.trim() || !email.includes('@')) {
        setErrorMsg('Please enter a valid email address.');
        return;
      }
      if (!passwordCriteria.hasMinLength || !passwordCriteria.hasUppercase || !passwordCriteria.hasNumber) {
        setErrorMsg('Please fulfill all password requirements below.');
        return;
      }
      if (password !== confirmPassword) {
        setErrorMsg('Passwords do not match. Please re-enter.');
        return;
      }

      setLoading(true);
      setTimeout(() => {
        setLoading(false);
        setSuccessMsg('Account created successfully! Initializing workspace...');
        setTimeout(() => {
          onSuccessLogin({
            name: fullName.trim(),
            email: email.trim().toLowerCase(),
            role: 'Student',
            isDemo: false,
          });
        }, 600);
      }, 700);
    } else {
      // Sign In mode
      if (!email.trim()) {
        setErrorMsg('Please enter your email address.');
        return;
      }
      if (!password) {
        setErrorMsg('Please enter your password.');
        return;
      }

      setLoading(true);
      setTimeout(() => {
        setLoading(false);
        setSuccessMsg('Signed in successfully! Opening workspace...');
        setTimeout(() => {
          onSuccessLogin({
            name: fullName || email.split('@')[0] || 'Student User',
            email: email.trim().toLowerCase(),
            role: 'Student',
            isDemo: false,
          });
        }, 500);
      }, 600);
    }
  };

  // =========================================================
  // ONE-CLICK DEMO ACCOUNT LOGIN
  // =========================================================
  const handleUseDemoAccount = () => {
    setErrorMsg('');
    setLoading(true);
    setEmail('demo@smartmedia.ai');
    setPassword('Demo@123');

    setTimeout(() => {
      setLoading(false);
      setSuccessMsg('Demo credentials authenticated! Opening workspace with sample learning data...');
      setTimeout(() => {
        onSuccessLogin({
          name: 'Demo Student',
          email: 'demo@smartmedia.ai',
          role: 'Student (Demo Access)',
          isDemo: true,
        });
      }, 500);
    }, 600);
  };

  const switchMode = (newMode) => {
    setMode(newMode);
    setErrorMsg('');
    setSuccessMsg('');
    window.location.hash = newMode;
  };

  return (
    <div className="auth-page-wrapper">
      {/* Ambient background lighting */}
      <div className="auth-ambient-glow auth-glow-left" />
      <div className="auth-ambient-glow auth-glow-right" />

      {/* Top Navigation */}
      <header className="auth-top-nav">
        <button onClick={onGoHome} className="auth-nav-back-btn" title="Return to Landing Page">
          <ArrowLeft size={15} />
          <span>Back to Home</span>
        </button>

        <div className="landing-brand" onClick={onGoHome} style={{ cursor: 'pointer' }}>
          <div className="landing-logo-icon">
            <Brain size={18} />
          </div>
          <div className="landing-brand-text">
            <span className="landing-brand-title">Smart Media</span>
          </div>
        </div>
      </header>

      {/* Main Two-Column Auth Container (50% Left Composition / 40% Right Form) */}
      <main className="auth-split-container">
        {/* =========================================================================
            LEFT COLUMN: SINGLE MINIMAL AI LEARNING WORKSPACE COMPOSITION
            ========================================================================= */}
        <section className="auth-visual-column">
          <div className="auth-visual-header">
            <div className="landing-hero-badge">
              <Sparkles size={13} className="hero-sparkle-icon" />
              <span>✦ Intelligent Learning Platform</span>
            </div>
          </div>

          <div className="auth-visual-headings">
            <h1 className="auth-visual-title">
              Your Learning, <br />
              <span className="landing-gradient-text">Powered By AI.</span>
            </h1>
            <p className="auth-visual-desc">
              Turn your educational content into searchable, intelligent knowledge.
            </p>
          </div>

          {/* SINGLE ELEGANT FUTURISTIC WORKSPACE PREVIEW (2-3 FLOATING CHIPS ONLY) */}
          <div className="auth-single-workspace-card">
            {/* Header bar of visual preview */}
            <div className="auth-workspace-card-header">
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#10B981' }} />
                <span style={{ fontSize: '0.74rem', fontWeight: 700, color: '#FFFFFF' }}>
                  AI Learning Assistant
                </span>
              </div>
              <span style={{ fontSize: '0.68rem', color: '#A78BFA', fontWeight: 600 }}>
                Grounded Q&A
              </span>
            </div>

            {/* AI Interaction Preview */}
            <div className="auth-workspace-dialogue-box">
              <div className="auth-workspace-user-snippet">
                <span className="auth-snippet-label">Question</span>
                <p style={{ margin: 0, fontSize: '0.82rem', color: '#FFFFFF', fontWeight: 500 }}>
                  "Explain encapsulation and runtime polymorphism in Java."
                </p>
              </div>

              <div className="auth-workspace-ai-snippet">
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px' }}>
                  <div className="auth-ai-dot" />
                  <span style={{ fontSize: '0.7rem', fontWeight: 700, color: '#6EE7B7' }}>
                    AI Analysis Agent
                  </span>
                </div>
                <p style={{ margin: 0, fontSize: '0.8rem', color: '#E2E8F0', lineHeight: 1.5 }}>
                  Encapsulation bundles data and methods to restrict direct unauthorized access.
                </p>
              </div>
            </div>

            {/* Floating Element 1: Source Citation */}
            <div className="auth-floating-chip chip-citation">
              <BookOpen size={13} color="#818CF8" />
              <div>
                <div style={{ fontSize: '0.66rem', color: '#94A3B8', fontWeight: 600, textTransform: 'uppercase' }}>
                  Verified Source
                </div>
                <div style={{ fontSize: '0.74rem', color: '#FFFFFF', fontWeight: 700 }}>
                  Lecture Notes • Page 14
                </div>
              </div>
            </div>

            {/* Floating Element 2: Study Notes Synthesis */}
            <div className="auth-floating-chip chip-notes">
              <Layers size={13} color="#EC4899" />
              <div>
                <div style={{ fontSize: '0.66rem', color: '#94A3B8', fontWeight: 600, textTransform: 'uppercase' }}>
                  AI Study Notes
                </div>
                <div style={{ fontSize: '0.74rem', color: '#FFFFFF', fontWeight: 700 }}>
                  12 Key Concepts Synthesized
                </div>
              </div>
            </div>

            {/* Floating Element 3: Video Timestamp Moment */}
            <div className="auth-floating-chip chip-timestamp">
              <Clock size={13} color="#06B6D4" />
              <div>
                <div style={{ fontSize: '0.66rem', color: '#94A3B8', fontWeight: 600, textTransform: 'uppercase' }}>
                  Video Moment
                </div>
                <div style={{ fontSize: '0.74rem', color: '#FFFFFF', fontWeight: 700 }}>
                  02:31 Runtime Dispatch
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* =========================================================================
            RIGHT COLUMN: PREMIUM GLASS AUTHENTICATION CARD
            ========================================================================= */}
        <section className="auth-form-column">
          <div className="auth-glass-card">
            {/* Logo & Card Header */}
            <div className="auth-card-brand-row">
              <div className="auth-card-logo">
                <Brain size={20} />
              </div>
              <span className="auth-card-product-name">Smart Media Analysis Agent</span>
            </div>

            {mode === 'signin' ? (
              <>
                <h2 className="auth-card-title">Welcome Back</h2>
                <p className="auth-card-subtitle">
                  Continue your learning journey with AI.
                </p>
              </>
            ) : (
              <>
                <h2 className="auth-card-title">Create Your Learning Workspace</h2>
                <p className="auth-card-subtitle">
                  Start your AI-powered learning journey.
                </p>
              </>
            )}

            {/* Inline Notifications */}
            {errorMsg && (
              <div className="auth-inline-alert error">
                <AlertCircle size={15} style={{ flexShrink: 0 }} />
                <span>{errorMsg}</span>
              </div>
            )}

            {successMsg && (
              <div className="auth-inline-alert success">
                <CheckCircle2 size={15} style={{ flexShrink: 0 }} />
                <span>{successMsg}</span>
              </div>
            )}

            {/* Main Form */}
            <form onSubmit={handleSubmit} className="auth-fields-form">
              {mode === 'signup' && (
                <div className="auth-input-group">
                  <label className="auth-label">Full Name</label>
                  <div className="auth-input-wrapper">
                    <User size={16} className="auth-input-icon" />
                    <input
                      type="text"
                      placeholder="e.g. Avneet Kaur"
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      className="auth-input-field"
                      required
                    />
                  </div>
                </div>
              )}

              <div className="auth-input-group">
                <label className="auth-label">Email Address</label>
                <div className="auth-input-wrapper">
                  <Mail size={16} className="auth-input-icon" />
                  <input
                    type="email"
                    placeholder="name@example.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="auth-input-field"
                    required
                  />
                </div>
              </div>

              <div className="auth-input-group">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <label className="auth-label">Password</label>
                  {mode === 'signin' && (
                    <button
                      type="button"
                      onClick={() => setErrorMsg('Password reset link sent to your email (if registered).')}
                      className="auth-forgot-btn"
                    >
                      Forgot password?
                    </button>
                  )}
                </div>
                <div className="auth-input-wrapper">
                  <Lock size={16} className="auth-input-icon" />
                  <input
                    type={showPassword ? 'text' : 'password'}
                    placeholder={mode === 'signup' ? 'Create a strong password' : 'Enter your password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="auth-input-field"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="auth-eye-toggle-btn"
                  >
                    {showPassword ? <EyeOff size={15} /> : <Eye size={15} />}
                  </button>
                </div>

                {/* Password Strength Indicator for Sign Up */}
                {mode === 'signup' && password && (
                  <div className="auth-password-strength-container">
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                      <span style={{ fontSize: '0.72rem', color: '#94A3B8' }}>Strength</span>
                      <span style={{ fontSize: '0.72rem', fontWeight: 700, color: passwordStrength.color }}>
                        {passwordStrength.label}
                      </span>
                    </div>
                    <div className="auth-strength-track">
                      <div
                        className="auth-strength-fill"
                        style={{ width: `${passwordStrength.score}%`, background: passwordStrength.color }}
                      />
                    </div>
                  </div>
                )}
              </div>

              {mode === 'signup' && (
                <div className="auth-input-group">
                  <label className="auth-label">Confirm Password</label>
                  <div className="auth-input-wrapper">
                    <Lock size={16} className="auth-input-icon" />
                    <input
                      type={showConfirmPassword ? 'text' : 'password'}
                      placeholder="Re-enter your password"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      className="auth-input-field"
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      className="auth-eye-toggle-btn"
                    >
                      {showConfirmPassword ? <EyeOff size={15} /> : <Eye size={15} />}
                    </button>
                  </div>
                </div>
              )}

              {/* Password Requirements Checklist for Sign Up */}
              {mode === 'signup' && (
                <div className="auth-requirements-box">
                  <span style={{ fontSize: '0.74rem', fontWeight: 700, color: '#C4B5FD', display: 'block', marginBottom: '6px' }}>
                    Password requirements:
                  </span>
                  <div className="auth-requirement-item">
                    <div className={`auth-req-dot ${passwordCriteria.hasMinLength ? 'met' : ''}`} />
                    <span style={{ color: passwordCriteria.hasMinLength ? '#10B981' : '#94A3B8' }}>
                      At least 8 characters
                    </span>
                  </div>
                  <div className="auth-requirement-item">
                    <div className={`auth-req-dot ${passwordCriteria.hasUppercase ? 'met' : ''}`} />
                    <span style={{ color: passwordCriteria.hasUppercase ? '#10B981' : '#94A3B8' }}>
                      One uppercase letter (A-Z)
                    </span>
                  </div>
                  <div className="auth-requirement-item">
                    <div className={`auth-req-dot ${passwordCriteria.hasNumber ? 'met' : ''}`} />
                    <span style={{ color: passwordCriteria.hasNumber ? '#10B981' : '#94A3B8' }}>
                      One number (0-9)
                    </span>
                  </div>
                </div>
              )}

              {mode === 'signin' && (
                <div className="auth-remember-row">
                  <label className="auth-checkbox-label">
                    <input
                      type="checkbox"
                      checked={rememberMe}
                      onChange={(e) => setRememberMe(e.target.checked)}
                      className="auth-checkbox"
                    />
                    <span>Remember me for 30 days</span>
                  </label>
                </div>
              )}

              {/* Primary CTA Submit Button */}
              <button type="submit" disabled={loading} className="auth-primary-submit-btn">
                {loading ? (
                  <>
                    <Loader2 size={16} className="animate-spin" />
                    <span>{mode === 'signin' ? 'Signing In...' : 'Creating Account...'}</span>
                  </>
                ) : (
                  <>
                    <span>{mode === 'signin' ? 'Sign In' : 'Create Account'}</span>
                    <ArrowRight size={16} />
                  </>
                )}
              </button>
            </form>

            {/* DEMO ACCOUNT BOX (For Instant Presentation) */}
            {mode === 'signin' && (
              <div className="auth-demo-section">
                <div className="auth-divider-row">
                  <div className="auth-divider-line" />
                  <span className="auth-divider-text">OR</span>
                  <div className="auth-divider-line" />
                </div>

                <div className="auth-demo-box">
                  <div className="auth-demo-header">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <Sparkles size={14} color="#A78BFA" />
                      <span style={{ fontSize: '0.84rem', fontWeight: 800, color: '#FFFFFF' }}>
                        Try Demo Account
                      </span>
                    </div>
                    <span className="badge badge-violet" style={{ fontSize: '0.64rem', padding: '1px 6px' }}>
                      1-Click Login
                    </span>
                  </div>

                  <div className="auth-demo-credentials-row">
                    <div>
                      <span style={{ fontSize: '0.7rem', color: '#94A3B8', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                        Email
                      </span>
                      <div style={{ fontSize: '0.8rem', color: '#C4B5FD', fontWeight: 600 }}>
                        demo@smartmedia.ai
                      </div>
                    </div>
                    <div>
                      <span style={{ fontSize: '0.7rem', color: '#94A3B8', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                        Password
                      </span>
                      <div style={{ fontSize: '0.8rem', color: '#C4B5FD', fontWeight: 600 }}>
                        Demo@123
                      </div>
                    </div>
                  </div>

                  <button
                    type="button"
                    onClick={handleUseDemoAccount}
                    disabled={loading}
                    className="auth-demo-action-btn"
                  >
                    <span>Use Demo Account →</span>
                  </button>
                </div>
              </div>
            )}

            {/* Switch Mode Footer */}
            <div className="auth-bottom-switch">
              {mode === 'signin' ? (
                <p style={{ margin: 0, fontSize: '0.84rem', color: 'var(--color-text-secondary)' }}>
                  Don't have an account?{' '}
                  <button onClick={() => switchMode('signup')} className="auth-switch-link">
                    Create Account
                  </button>
                </p>
              ) : (
                <p style={{ margin: 0, fontSize: '0.84rem', color: 'var(--color-text-secondary)' }}>
                  Already have an account?{' '}
                  <button onClick={() => switchMode('signin')} className="auth-switch-link">
                    Sign In
                  </button>
                </p>
              )}
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}

import React, { useState, useEffect, useCallback } from 'react';
import LandingPage from './pages/LandingPage';
import DashboardPage from './pages/DashboardPage';
import AuthPage from './pages/AuthPage';
import SettingsPage from './pages/SettingsPage';

export default function App() {
  // =========================================================
  // AUTHENTICATION & SESSION STATE
  // =========================================================
  const [currentUser, setCurrentUser] = useState(() => {
    try {
      const saved = localStorage.getItem('sma_auth_user');
      if (saved) return JSON.parse(saved);
    } catch (e) {
      console.error('Failed to parse auth user:', e);
    }
    return null;
  });

  // Determine active view based on URL hash & auth state
  const getInitialView = () => {
    const hash = window.location.hash.toLowerCase();
    const isAuthed = Boolean(localStorage.getItem('sma_auth_user'));

    if (hash === '#signin') {
      return isAuthed ? 'workspace' : 'signin';
    }
    if (hash === '#signup') {
      return isAuthed ? 'workspace' : 'signup';
    }
    if (hash === '#workspace' || hash === '#app') {
      return isAuthed ? 'workspace' : 'signin';
    }
    if (hash === '#settings' || hash === '#profile') {
      return isAuthed ? 'settings' : 'signin';
    }
    return 'landing';
  };

  const [view, setView] = useState(getInitialView);

  // Sync route on hash change and protect routes
  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash.toLowerCase();
      const isAuthed = Boolean(currentUser);

      if (hash === '#workspace' || hash === '#app') {
        if (!isAuthed) {
          window.location.hash = 'signin';
          setView('signin');
        } else {
          setView('workspace');
        }
      } else if (hash === '#signin') {
        if (isAuthed) {
          window.location.hash = 'workspace';
          setView('workspace');
        } else {
          setView('signin');
        }
      } else if (hash === '#signup') {
        if (isAuthed) {
          window.location.hash = 'workspace';
          setView('workspace');
        } else {
          setView('signup');
        }
      } else if (hash === '#settings' || hash === '#profile') {
        if (!isAuthed) {
          window.location.hash = 'signin';
          setView('signin');
        } else {
          setView('settings');
        }
      } else {
        setView('landing');
      }
    };

    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, [currentUser]);

  // =========================================================
  // AUTH ACTION HANDLERS
  // =========================================================
  const handleLogin = useCallback((userData) => {
    setCurrentUser(userData);
    try {
      localStorage.setItem('sma_auth_user', JSON.stringify(userData));
    } catch (e) {
      console.error('Failed to persist user session:', e);
    }
    window.location.hash = 'workspace';
    setView('workspace');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, []);

  const handleLogout = useCallback(() => {
    setCurrentUser(null);
    try {
      localStorage.removeItem('sma_auth_user');
    } catch (e) {
      console.error('Failed to clear user session:', e);
    }
    window.location.hash = 'signin';
    setView('signin');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, []);

  // Navigation callbacks
  const handleGoHome = useCallback(() => {
    window.location.hash = '';
    setView('landing');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, []);

  const handleOpenSignIn = useCallback(() => {
    if (currentUser) {
      window.location.hash = 'workspace';
      setView('workspace');
    } else {
      window.location.hash = 'signin';
      setView('signin');
    }
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, [currentUser]);

  const handleOpenSignUp = useCallback(() => {
    if (currentUser) {
      window.location.hash = 'workspace';
      setView('workspace');
    } else {
      window.location.hash = 'signup';
      setView('signup');
    }
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, [currentUser]);

  const handleOpenSettings = useCallback(() => {
    if (!currentUser) {
      window.location.hash = 'signin';
      setView('signin');
    } else {
      window.location.hash = 'settings';
      setView('settings');
    }
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, [currentUser]);

  const handleLaunchWorkspace = useCallback(() => {
    if (!currentUser) {
      window.location.hash = 'signin';
      setView('signin');
    } else {
      window.location.hash = 'workspace';
      setView('workspace');
    }
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, [currentUser]);

  // =========================================================
  // VIEW ROUTING
  // =========================================================
  if (view === 'settings') {
    if (!currentUser) {
      return (
        <AuthPage
          initialMode="signin"
          onGoHome={handleGoHome}
          onSuccessLogin={handleLogin}
        />
      );
    }
    return (
      <SettingsPage
        currentUser={currentUser}
        onGoHome={handleGoHome}
        onLaunchApp={handleLaunchWorkspace}
        onLogout={handleLogout}
      />
    );
  }

  if (view === 'workspace') {
    if (!currentUser) {
      return (
        <AuthPage
          initialMode="signin"
          onGoHome={handleGoHome}
          onSuccessLogin={handleLogin}
        />
      );
    }
    return (
      <DashboardPage
        currentUser={currentUser}
        onGoHome={handleGoHome}
        onOpenSettings={handleOpenSettings}
        onLogout={handleLogout}
      />
    );
  }

  if (view === 'signin') {
    return (
      <AuthPage
        initialMode="signin"
        onGoHome={handleGoHome}
        onSuccessLogin={handleLogin}
      />
    );
  }

  if (view === 'signup') {
    return (
      <AuthPage
        initialMode="signup"
        onGoHome={handleGoHome}
        onSuccessLogin={handleLogin}
      />
    );
  }

  // Default: Landing Page
  return (
    <LandingPage
      currentUser={currentUser}
      onLaunchApp={handleLaunchWorkspace}
      onOpenSignIn={handleOpenSignIn}
      onOpenSignUp={handleOpenSignUp}
      onOpenSettings={handleOpenSettings}
      onLogout={handleLogout}
    />
  );
}

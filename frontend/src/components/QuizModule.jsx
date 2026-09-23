import React, { useState, useEffect } from 'react';
import {
  HelpCircle,
  CheckCircle2,
  XCircle,
  Award,
  Sparkles,
  RefreshCw,
  AlertCircle,
  Loader2,
  ArrowLeft,
  ArrowRight,
  ShieldCheck,
  ChevronRight,
  BookOpen,
  Clock,
  RotateCcw,
  Zap,
} from 'lucide-react';
import confetti from 'canvas-confetti';
import { formatSeconds } from '../utils/formatters';
import apiService from '../services/api';

export default function QuizModule({ activeDocument, onCitationClick }) {
  const [quiz, setQuiz] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [showResults, setShowResults] = useState(false);
  const [difficulty, setDifficulty] = useState('medium');
  const [numQuestions, setNumQuestions] = useState(5);
  const [currentQuestionIdx, setCurrentQuestionIdx] = useState(0);

  const generateQuiz = async () => {
    if (!activeDocument?.id) return;
    setLoading(true);
    setError(null);
    setSelectedAnswers({});
    setShowResults(false);
    setCurrentQuestionIdx(0);

    try {
      const data = await apiService.generateQuiz(activeDocument.id, numQuestions, difficulty);
      setQuiz(data);
    } catch (err) {
      setError('Failed to generate interactive quiz. Please verify backend connection.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeDocument?.id) {
      setSelectedAnswers({});
      setShowResults(false);
      setCurrentQuestionIdx(0);
      apiService
        .listQuizzes(activeDocument.id)
        .then((quizzes) => {
          if (quizzes.length > 0) {
            setQuiz(quizzes[0]);
          } else {
            setQuiz(null);
          }
        })
        .catch(() => setQuiz(null));
    }
  }, [activeDocument]);

  const handleSelectOption = (questionId, optionIndex) => {
    if (showResults) return;
    setSelectedAnswers((prev) => ({
      ...prev,
      [questionId]: optionIndex,
    }));
  };

  const handleSubmitQuiz = () => {
    setShowResults(true);
    if (!quiz) return;

    let score = 0;
    quiz.questions.forEach((q) => {
      if (selectedAnswers[q.id] === q.correct_answer_index) {
        score += 1;
      }
    });

    if (score / quiz.questions.length >= 0.7) {
      confetti({
        particleCount: 90,
        spread: 80,
        origin: { y: 0.6 },
      });
    }
  };

  const handleRetakeQuiz = () => {
    setSelectedAnswers({});
    setShowResults(false);
    setCurrentQuestionIdx(0);
  };

  if (!activeDocument) {
    return (
      <div className="quiz-empty-state-panel">
        <div className="quiz-empty-orb">
          <HelpCircle size={36} color="#A78BFA" />
        </div>
        <h3 className="quiz-empty-title">Interactive Practice Quiz</h3>
        <p className="quiz-empty-desc">
          Select an educational material to generate curriculum-aligned practice quizzes with automatic grounding and score evaluation.
        </p>
      </div>
    );
  }

  const questions = quiz?.questions || [];
  const totalCount = questions.length;
  const currentQuestion = questions[currentQuestionIdx];
  const answeredCount = Object.keys(selectedAnswers).length;

  let totalScore = 0;
  if (showResults && quiz) {
    quiz.questions.forEach((q) => {
      if (selectedAnswers[q.id] === q.correct_answer_index) {
        totalScore += 1;
      }
    });
  }

  const progressPercent = totalCount > 0 ? ((currentQuestionIdx + 1) / totalCount) * 100 : 0;

  return (
    <div className="quiz-module-container">
      {/* =========================================================================
          HEADER
          ========================================================================= */}
      <div className="quiz-header-bar">
        <div className="quiz-header-left">
          <div className="quiz-brand-orb">
            <HelpCircle size={22} color="#FFFFFF" />
          </div>

          <div className="quiz-header-titles">
            <div className="quiz-title-row">
              <h2 className="quiz-main-heading">Interactive Practice Quiz</h2>
              <span className="badge badge-violet">
                <Sparkles size={11} /> Grounded MCQs
              </span>
            </div>
            <p className="quiz-sub-heading">
              Test your understanding of {activeDocument.filename}
            </p>
          </div>
        </div>

        {/* Right side: Difficulty dropdown, Questions dropdown, Generate New Quiz */}
        <div className="quiz-header-controls">
          <select
            value={difficulty}
            onChange={(e) => setDifficulty(e.target.value)}
            disabled={loading}
            className="quiz-control-select"
          >
            <option value="easy">Easy</option>
            <option value="medium">Medium</option>
            <option value="hard">Hard</option>
          </select>

          <select
            value={numQuestions}
            onChange={(e) => setNumQuestions(Number(e.target.value))}
            disabled={loading}
            className="quiz-control-select"
          >
            <option value={3}>3 Questions</option>
            <option value={5}>5 Questions</option>
            <option value={8}>8 Questions</option>
            <option value={10}>10 Questions</option>
          </select>

          <button
            onClick={generateQuiz}
            disabled={loading}
            className="quiz-generate-btn"
            title="Generate a new AI practice quiz"
          >
            {loading ? <Loader2 className="animate-spin" size={14} /> : <Sparkles size={14} />}
            <span>{loading ? 'Generating...' : 'Generate New Quiz'}</span>
          </button>
        </div>
      </div>

      {/* =========================================================================
          LOADING STATE
          ========================================================================= */}
      {loading && (
        <div className="quiz-loading-container">
          <div className="quiz-loading-pulse">
            <Loader2 className="animate-spin" size={38} color="#A78BFA" />
          </div>
          <h4 className="quiz-loading-title">Formulating Grounded Questions...</h4>
          <p className="quiz-loading-desc">
            Extracting key topics, generating plausible distractors, and preparing verified explanations with page citations.
          </p>
        </div>
      )}

      {/* =========================================================================
          ERROR STATE
          ========================================================================= */}
      {error && (
        <div className="quiz-error-banner">
          <AlertCircle size={18} />
          <span>{error}</span>
          <button onClick={generateQuiz} className="btn-secondary" style={{ padding: '4px 10px', fontSize: '0.74rem' }}>
            Retry
          </button>
        </div>
      )}

      {/* =========================================================================
          EMPTY STATE
          ========================================================================= */}
      {!loading && !quiz && (
        <div className="quiz-not-generated-panel">
          <p className="quiz-not-generated-text">
            No practice quiz has been generated for this material yet.
          </p>
          <button onClick={generateQuiz} className="btn-primary">
            <Sparkles size={15} />
            <span>Generate Practice Quiz Now</span>
          </button>
        </div>
      )}

      {/* =========================================================================
          ACTIVE QUIZ WORKSPACE
          ========================================================================= */}
      {!loading && quiz && totalCount > 0 && (
        <div className="quiz-active-workspace">
          {/* ---------------------------------------------------------------------
              SCORE RESULTS BANNER (When submitted)
              --------------------------------------------------------------------- */}
          {showResults && (
            <div
              className={`quiz-score-card ${
                totalScore / totalCount >= 0.7 ? 'success' : 'review'
              }`}
            >
              <div className="score-card-left">
                <div className="score-badge-orb">
                  <Award size={26} />
                </div>
                <div>
                  <h3 className="score-title">
                    Quiz Score: {totalScore} / {totalCount} Correct (
                    {Math.round((totalScore / totalCount) * 100)}%)
                  </h3>
                  <p className="score-subtitle">
                    {totalScore / totalCount >= 0.7
                      ? 'Outstanding work! You have demonstrated strong mastery of these concepts.'
                      : 'Review the explanations below to reinforce your understanding of these topics.'}
                  </p>
                </div>
              </div>

              <div className="score-card-actions">
                <button onClick={handleRetakeQuiz} className="btn-secondary">
                  <RotateCcw size={14} />
                  <span>Retake Quiz</span>
                </button>
                <button onClick={generateQuiz} className="btn-primary">
                  <Sparkles size={14} />
                  <span>New Quiz</span>
                </button>
              </div>
            </div>
          )}

          {/* ---------------------------------------------------------------------
              PROGRESS BAR SECTION
              --------------------------------------------------------------------- */}
          <div className="quiz-progress-section">
            <div className="quiz-progress-header">
              <span className="quiz-progress-label">
                Question {currentQuestionIdx + 1} of {totalCount}
              </span>
              <div className="quiz-progress-step-pills">
                {questions.map((_, idx) => {
                  const isAnswered = selectedAnswers[questions[idx].id] !== undefined;
                  const isCurrent = idx === currentQuestionIdx;
                  return (
                    <button
                      key={idx}
                      onClick={() => setCurrentQuestionIdx(idx)}
                      className={`quiz-step-dot ${isCurrent ? 'current' : isAnswered ? 'answered' : ''}`}
                      title={`Jump to Question ${idx + 1}`}
                    >
                      {idx + 1}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Violet → Cyan Gradient Progress Bar */}
            <div className="quiz-progress-track">
              <div
                className="quiz-progress-fill"
                style={{ width: `${progressPercent}%` }}
              />
            </div>
          </div>

          {/* ---------------------------------------------------------------------
              MAIN QUESTION CARD
              --------------------------------------------------------------------- */}
          {currentQuestion && (
            <div className="quiz-main-question-card">
              {/* Question Header & Title */}
              <div className="quiz-question-header">
                <div className="question-number-tag">Q{currentQuestionIdx + 1}.</div>
                <h3 className="quiz-question-text">{currentQuestion.question}</h3>
              </div>

              {/* Options List (A, B, C, D) */}
              <div className="quiz-options-list">
                {currentQuestion.options.map((opt, optIndex) => {
                  const isSelected = selectedAnswers[currentQuestion.id] === optIndex;
                  const isCorrect = optIndex === currentQuestion.correct_answer_index;

                  let optionStateClass = '';
                  if (showResults) {
                    if (isCorrect) {
                      optionStateClass = 'correct';
                    } else if (isSelected && !isCorrect) {
                      optionStateClass = 'incorrect';
                    }
                  } else if (isSelected) {
                    optionStateClass = 'selected';
                  }

                  return (
                    <div
                      key={optIndex}
                      onClick={() => handleSelectOption(currentQuestion.id, optIndex)}
                      className={`quiz-option-row ${optionStateClass}`}
                    >
                      <div className="option-letter-badge">
                        {String.fromCharCode(65 + optIndex)}
                      </div>
                      <span className="option-text-label">{opt}</span>

                      {showResults && (
                        <div className="option-feedback-icon">
                          {isCorrect ? (
                            <CheckCircle2 size={16} color="#34D399" />
                          ) : isSelected && !isCorrect ? (
                            <XCircle size={16} color="#F87171" />
                          ) : null}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>

              {/* Explanation & Citations (Visible after submission) */}
              {showResults && (
                <div className="quiz-explanation-box">
                  <div className="explanation-header">
                    <ShieldCheck size={14} color="#818CF8" />
                    <span>VERIFIED EXPLANATION</span>
                  </div>
                  <p className="explanation-text">{currentQuestion.explanation}</p>

                  {/* Grounded Citation if present */}
                  {currentQuestion.citation && (
                    <div className="explanation-citation-row">
                      <span className="citation-label">SOURCE:</span>
                      <button
                        onClick={() =>
                          onCitationClick && onCitationClick(currentQuestion.citation)
                        }
                        className="source-citation-badge"
                      >
                        {currentQuestion.citation.timestamp_start !== null &&
                        currentQuestion.citation.timestamp_start !== undefined ? (
                          <>
                            <Clock size={11} color="var(--color-cyan)" />
                            <span>
                              {formatSeconds(currentQuestion.citation.timestamp_start)}
                            </span>
                          </>
                        ) : (
                          <>
                            <BookOpen size={11} color="var(--color-indigo)" />
                            <span>
                              Page {currentQuestion.citation.page_number || '1'}
                            </span>
                          </>
                        )}
                      </button>
                    </div>
                  )}
                </div>
              )}

              {/* -----------------------------------------------------------------
                  BUTTONS: PREVIOUS / NEXT → / SUBMIT
                  ----------------------------------------------------------------- */}
              <div className="quiz-nav-footer">
                <button
                  onClick={() => setCurrentQuestionIdx((prev) => Math.max(0, prev - 1))}
                  disabled={currentQuestionIdx === 0}
                  className="quiz-nav-prev-btn"
                >
                  <ArrowLeft size={15} />
                  <span>Previous</span>
                </button>

                <div className="quiz-nav-right-actions">
                  {currentQuestionIdx < totalCount - 1 ? (
                    <button
                      onClick={() =>
                        setCurrentQuestionIdx((prev) => Math.min(totalCount - 1, prev + 1))
                      }
                      className="btn-primary"
                      style={{ padding: '10px 22px' }}
                    >
                      <span>Next</span>
                      <ArrowRight size={15} />
                    </button>
                  ) : !showResults ? (
                    <button
                      onClick={handleSubmitQuiz}
                      disabled={answeredCount === 0}
                      className="btn-primary"
                      style={{ padding: '10px 24px', background: 'linear-gradient(135deg, #10B981 0%, #06B6D4 100%)' }}
                    >
                      <span>Submit Answers ({answeredCount}/{totalCount})</span>
                      <CheckCircle2 size={16} />
                    </button>
                  ) : (
                    <button
                      onClick={handleRetakeQuiz}
                      className="btn-secondary"
                      style={{ padding: '10px 20px' }}
                    >
                      <RotateCcw size={14} />
                      <span>Retake Quiz</span>
                    </button>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}


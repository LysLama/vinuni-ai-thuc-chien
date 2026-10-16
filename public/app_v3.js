window.onerror = function(msg, url, line, col, error) {
  console.log("GLOBAL_ERROR_DETAIL:", msg, "AT", url, ":", line, ":", col, "STACK:", error ? error.stack : "NO_STACK");
};

// Purge stale Service Workers and old caches when running inside file:/// or WebView
if (window.location.protocol === "file:" || !window.location.protocol.startsWith("http")) {
  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.getRegistrations().then(registrations => {
      for (const registration of registrations) {
        registration.unregister();
      }
    });
  }
  if ("caches" in window) {
    caches.keys().then(keys => {
      for (const key of keys) {
        caches.delete(key);
      }
    });
  }
}

// Module Names Mapping
const MODULE_NAMES = {
  A: "Module A: Nền tảng Toán học & Định lượng",
  B: "Module B: Kỹ thuật Lập trình & Xử lý dữ liệu",
  C: "Module C: Kiến thức AI & Tư duy sản phẩm AI",
  D: "Module D: Tư duy Logic, Đạo đức & Hành vi",
};

// Global State
const state = {
  currentTab: "exam", // 'exam', 'practice', 'docs', 'results'
  allQuestions: { A: [], B: [], C: [], D: [] },
  isLoaded: false,

  // Exam Mode State
  examQuestions: [],
  currentIndex: 0,
  userAnswers: {},
  flaggedQuestions: new Set(),
  examSubmitted: false,
  timerSeconds: 90 * 60,
  timerInterval: null,
  examResults: null,

  // Practice Mode State
  practiceModule: "A",
  practiceDifficulty: "all",
  practiceQuestions: [],
  practiceIndex: 0,
  practiceFeedback: {},
  practiceShowAllExplanations: false,
  practiceExpanded: new Set(),

  // Docs Mode State
  currentDoc: "KINH_NGHIEM_THI_THUC_CHIEN_VINUNI.md",
};

// Initialize Application
document.addEventListener("DOMContentLoaded", async () => {
  setupNavigation();
  setupKeyboardShortcuts();
  await loadQuestionBanks();
  loadSavedExamState();
  initPracticeView();
  renderMathAndCode();
  if (window.lucide) window.lucide.createIcons();
});

// Load question banks (via prebundled embedded script, static JSON fallback, or API)
async function loadQuestionBanks() {
  // 1. Instant offline load if prebundled into window.EMBEDDED_QUESTIONS
  if (window.EMBEDDED_QUESTIONS && window.EMBEDDED_QUESTIONS.A && window.EMBEDDED_QUESTIONS.A.length > 0) {
    state.allQuestions = window.EMBEDDED_QUESTIONS;
    state.isLoaded = true;
    updateStatsHeader();
    return;
  }

  // 2. Fetch fallback
  const modules = ["a", "b", "c", "d"];
  try {
    for (const mod of modules) {
      const code = mod.toUpperCase();
      let res;
      try {
        const fileUrl = `data/module_${mod}_${getModuleFileSuffix(code)}.json?v=${Date.now()}`;
        res = await fetch(fileUrl, { cache: "no-store" });
        if (!res.ok) throw new Error("Fallback to API");
        state.allQuestions[code] = await res.json();
      } catch (e) {
        // Fallback to API if static fetch fails
        const apiRes = await fetch(`/api/questions?module=${code}&v=${Date.now()}`, { cache: "no-store" });
        const apiData = await apiRes.json();
        state.allQuestions[code] = apiData.questions || [];
      }
    }
    state.isLoaded = true;
    updateStatsHeader();
  } catch (err) {
    console.error("Error loading question banks:", err);
  }
}

function getModuleFileSuffix(code) {
  if (code === "A") return "toan_dinh_luong";
  if (code === "B") return "lap_trinh_du_lieu";
  if (code === "C") return "kien_thuc_san_pham_ai";
  if (code === "D") return "logic_dao_duc_hanh_vi";
  return "";
}

function updateStatsHeader() {
  const total = Object.values(state.allQuestions).reduce((acc, q) => acc + q.length, 0);
  const statsEl = document.getElementById("bank-total-stat");
  if (statsEl) statsEl.textContent = `${total} câu`;
}

// Navigation between Tabs (Desktop header tabs + Mobile bottom navigation)
function setupNavigation() {
  const tabButtons = document.querySelectorAll(".nav-tab-btn, .mobile-nav-btn");
  tabButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      const tab = btn.dataset.tab;
      if (tab) switchTab(tab);
    });
  });
}

function switchTab(tabName) {
  state.currentTab = tabName;
  document.querySelectorAll(".nav-tab-btn, .mobile-nav-btn").forEach(b => {
    b.classList.toggle("active", b.dataset.tab === tabName);
  });

  const examView = document.getElementById("view-exam");
  const practiceView = document.getElementById("view-practice");
  const docsView = document.getElementById("view-docs");
  const resultView = document.getElementById("view-results");
  const examBar = document.getElementById("exam-control-bar");
  const mobileResultsBtn = document.getElementById("mobile-nav-btn-results");

  if (mobileResultsBtn) {
    mobileResultsBtn.style.display = (tabName === "results" || state.examSubmitted) ? "flex" : "none";
  }

  examView.style.display = tabName === "exam" && !state.examSubmitted ? "block" : "none";
  resultView.style.display = tabName === "results" || (tabName === "exam" && state.examSubmitted) ? "block" : "none";
  practiceView.style.display = tabName === "practice" ? "block" : "none";
  docsView.style.display = tabName === "docs" ? "block" : "none";

  if (examBar) {
    examBar.style.display = tabName === "exam" && !state.examSubmitted ? "flex" : "none";
  }

  toggleMobilePalette(false);

  if (tabName === "exam" && state.examQuestions.length === 0) {
    startNewExam();
  } else if (tabName === "practice") {
    initPracticeView();
  } else if (tabName === "docs") {
    loadDocumentContent(state.currentDoc);
  }

  renderMathAndCode();
}

// ------------------------------------------------------------------
// EXAM MODE ENGINE (90 Mins, 20 Questions, 100 Points)
// ------------------------------------------------------------------
function startNewExam() {
  if (!state.isLoaded) {
    setTimeout(startNewExam, 200);
    return;
  }

  // Generate 20 questions: 5 per module (4 MC + 1 Scenario)
  state.examQuestions = [];
  ["A", "B", "C", "D"].forEach(mod => {
    const list = [...state.allQuestions[mod]];
    const mc = list.filter(q => q.type === "multiple_choice").sort(() => 0.5 - Math.random());
    const sc = list.filter(q => q.type === "scenario").sort(() => 0.5 - Math.random());

    const picked = [...mc.slice(0, 4), ...(sc.length ? sc.slice(0, 1) : mc.slice(4, 5))];
    picked.forEach(q => {
      const qCopy = { ...q, points: 5 };
      state.examQuestions.push(qCopy);
    });
  });

  state.currentIndex = 0;
  state.userAnswers = {};
  state.flaggedQuestions = new Set();
  state.examSubmitted = false;
  state.timerSeconds = 90 * 60;

  // Clear previous stored session
  localStorage.removeItem("vinuni_exam_active_v3");
  localStorage.removeItem("vinuni_exam_active");
  localStorage.removeItem("vinuni_exam_active_v2");

  startTimer();
  renderCurrentQuestion();
  renderQuestionPalette();
}

function loadSavedExamState() {
  localStorage.removeItem("vinuni_exam_active");
  localStorage.removeItem("vinuni_exam_active_v2");
  const saved = localStorage.getItem("vinuni_exam_active_v3");
  if (saved) {
    try {
      const parsed = JSON.parse(saved);
      if (parsed.examQuestions && parsed.examQuestions.length === 20 && !parsed.examSubmitted) {
        // Always sync questions with the latest question bank data
        const validated = parsed.examQuestions.map(q => {
          const mod = q.module;
          const fresh = (state.allQuestions[mod] || []).find(item => item.id === q.id);
          return fresh ? { ...fresh, points: q.points || fresh.points || 5 } : (q && q.question ? q : null);
        });

        if (validated.every(item => item && item.question)) {
          state.examQuestions = validated;
          state.currentIndex = parsed.currentIndex || 0;
          state.userAnswers = parsed.userAnswers || {};
          state.flaggedQuestions = new Set(parsed.flaggedQuestions || []);
          state.timerSeconds = parsed.timerSeconds || 90 * 60;
          startTimer();
          renderCurrentQuestion();
          renderQuestionPalette();
          return;
        }
      }
    } catch (e) {
      console.warn("Could not resume saved exam:", e);
    }
  }
  startNewExam();
}

function saveExamState() {
  if (state.examSubmitted) return;
  const payload = {
    examQuestions: state.examQuestions,
    currentIndex: state.currentIndex,
    userAnswers: state.userAnswers,
    flaggedQuestions: Array.from(state.flaggedQuestions),
    timerSeconds: state.timerSeconds,
    examSubmitted: state.examSubmitted,
  };
  localStorage.setItem("vinuni_exam_active_v3", JSON.stringify(payload));
}

function startTimer() {
  if (state.timerInterval) clearInterval(state.timerInterval);
  updateTimerDisplay();

  state.timerInterval = setInterval(() => {
    if (state.timerSeconds > 0) {
      state.timerSeconds--;
      updateTimerDisplay();
      if (state.timerSeconds % 10 === 0) saveExamState();
    } else {
      clearInterval(state.timerInterval);
      alert("Hết giờ làm bài! Hệ thống đang tự động nộp bài thi của bạn.");
      submitExam();
    }
  }, 1000);
}

function updateTimerDisplay() {
  const timerEl = document.getElementById("exam-timer-display");
  if (!timerEl) return;
  const mins = Math.floor(state.timerSeconds / 60);
  const secs = state.timerSeconds % 60;
  timerEl.textContent = `${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;

  const timerBox = document.getElementById("exam-timer-box");
  if (timerBox) {
    timerBox.classList.toggle("warning", state.timerSeconds <= 10 * 60);
  }
}

// Render active question in viewport
function renderCurrentQuestion() {
  const q = state.examQuestions[state.currentIndex];
  if (!q) return;

  const idxEl = document.getElementById("q-index-label");
  const modBadge = document.getElementById("q-module-badge");
  const diffBadge = document.getElementById("q-diff-badge");
  const textEl = document.getElementById("q-text-body");
  const optsContainer = document.getElementById("q-options-container");
  const flagBtn = document.getElementById("btn-flag-toggle");
  const prevBtn = document.getElementById("btn-prev-q");
  const nextBtn = document.getElementById("btn-next-q");

  idxEl.textContent = `Câu ${state.currentIndex + 1} / ${state.examQuestions.length}`;
  modBadge.textContent = MODULE_NAMES[q.module];
  diffBadge.textContent = q.difficulty || "Trung bình";
  diffBadge.className = `difficulty-badge ${getDiffClass(q.difficulty)}`;

  const qText = q.question || q.prompt || q.title || "";
  textEl.innerHTML = formatMathText(qText);

  // Render Flag button state
  const isFlagged = state.flaggedQuestions.has(q.id);
  flagBtn.classList.toggle("flagged", isFlagged);
  flagBtn.innerHTML = isFlagged
    ? `<i data-lucide="flag" style="width:16px;height:16px;fill:#b45309"></i> Đã đánh dấu xem lại`
    : `<i data-lucide="flag" style="width:16px;height:16px"></i> Đánh dấu xem lại (F)`;

  // Render Options or Scenario textarea
  optsContainer.innerHTML = "";
  if (q.type === "multiple_choice") {
    const selectedAns = state.userAnswers[q.id] || "";
    const list = document.createElement("div");
    list.className = "options-list";

    if (q.options && typeof q.options === "object") {
      Object.entries(q.options).forEach(([key, val]) => {
        const item = document.createElement("div");
        item.className = `option-item ${selectedAns === key ? "selected" : ""}`;
        item.innerHTML = `
          <div class="option-key">${escapeHtml(key)}</div>
          <div class="option-text">${formatMathText(String(val ?? ""))}</div>
        `;
        item.addEventListener("click", () => {
          selectOption(q.id, key);
        });
        list.appendChild(item);
      });
    }
    optsContainer.appendChild(list);
  } else {
    // Scenario / Short Answer
    const currentAns = state.userAnswers[q.id] || "";
    optsContainer.innerHTML = `
      <div style="margin-top: 16px;">
        <label style="font-weight: 600; font-size: 13px; color: var(--text-muted); display: block; margin-bottom: 8px;">
          Phương án giải quyết của bạn (Bài tập tình huống):
        </label>
        <textarea id="scenario-input-${q.id}" class="form-textarea" rows="6" 
          placeholder="Trình bày giải pháp kỹ thuật, lý do lựa chọn kiến trúc, các bước khắc phục..."
          style="width: 100%; padding: 12px; border: 1px solid var(--border-strong); border-radius: var(--radius-md); font-family: var(--font-sans); font-size: 14px; line-height: 1.5;">${escapeHtml(currentAns)}</textarea>
      </div>
    `;
    const textarea = document.getElementById(`scenario-input-${q.id}`);
    textarea.addEventListener("input", e => {
      state.userAnswers[q.id] = e.target.value.trim();
      saveExamState();
      renderQuestionPalette();
    });
  }

  prevBtn.disabled = state.currentIndex === 0;
  nextBtn.textContent = state.currentIndex === state.examQuestions.length - 1 ? "Xem lại đề thi" : "Câu tiếp theo → (N)";

  renderQuestionPalette();
  renderMathAndCode();
  if (window.lucide) window.lucide.createIcons();
}

function selectOption(qId, key) {
  state.userAnswers[qId] = key;
  saveExamState();
  renderCurrentQuestion();
  renderQuestionPalette();
}

function toggleFlag() {
  const q = state.examQuestions[state.currentIndex];
  if (!q) return;
  if (state.flaggedQuestions.has(q.id)) {
    state.flaggedQuestions.delete(q.id);
  } else {
    state.flaggedQuestions.add(q.id);
  }
  saveExamState();
  renderCurrentQuestion();
  renderQuestionPalette();
}

function prevQuestion() {
  if (state.currentIndex > 0) {
    state.currentIndex--;
    renderCurrentQuestion();
  }
}

function nextQuestion() {
  if (state.currentIndex < state.examQuestions.length - 1) {
    state.currentIndex++;
    renderCurrentQuestion();
  }
}

// Right Sidebar Question Navigator Palette
function renderQuestionPalette() {
  const palette = document.getElementById("exam-palette-grid");
  if (!palette) return;
  palette.innerHTML = "";

  state.examQuestions.forEach((q, idx) => {
    const btn = document.createElement("button");
    btn.className = "q-cell-btn tabular-nums";
    btn.textContent = idx + 1;

    const isCurrent = idx === state.currentIndex;
    const isAnswered = Boolean(state.userAnswers[q.id] && state.userAnswers[q.id].length > 0);
    const isFlagged = state.flaggedQuestions.has(q.id);

    if (isCurrent) btn.classList.add("active");
    if (isAnswered) btn.classList.add("answered");
    if (isFlagged) btn.classList.add("flagged");

    btn.title = `Câu ${idx + 1} [${q.id}] - ${MODULE_NAMES[q.module]}`;
    btn.addEventListener("click", () => {
      state.currentIndex = idx;
      renderCurrentQuestion();
      toggleMobilePalette(false);
    });

    palette.appendChild(btn);
  });

  // Update counts
  const answeredCount = Object.keys(state.userAnswers).filter(k => state.userAnswers[k].length > 0).length;
  const progressText = document.getElementById("answered-progress-stat");
  if (progressText) {
    progressText.textContent = `${answeredCount} / ${state.examQuestions.length} câu`;
  }
}

// Mobile Palette Drawer Toggle
function toggleMobilePalette(force) {
  const palette = document.querySelector(".nav-palette-card");
  const backdrop = document.getElementById("mobile-palette-backdrop");
  if (!palette) return;

  const isCurrentlyOpen = palette.classList.contains("drawer-open");
  const shouldOpen = typeof force === "boolean" ? force : !isCurrentlyOpen;

  palette.classList.toggle("drawer-open", shouldOpen);
  if (backdrop) {
    backdrop.classList.toggle("active", shouldOpen);
  }
}
window.toggleMobilePalette = toggleMobilePalette;

// Submit & Grade Exam
function submitExam() {
  const answeredCount = Object.keys(state.userAnswers).filter(k => state.userAnswers[k].length > 0).length;
  const totalCount = state.examQuestions.length;

  if (answeredCount < totalCount) {
    const proceed = confirm(`Bạn mới trả lời ${answeredCount}/${totalCount} câu hỏi. Bạn có chắc chắn muốn nộp bài thi ngay không?`);
    if (!proceed) return;
  } else {
    const proceed = confirm("Bạn có chắc chắn muốn nộp bài thi và kết thúc 90 phút làm bài?");
    if (!proceed) return;
  }

  clearInterval(state.timerInterval);
  state.examSubmitted = true;
  localStorage.removeItem("vinuni_exam_active_v3");
  localStorage.removeItem("vinuni_exam_active");

  const elapsed = 90 * 60 - state.timerSeconds;
  gradeExamLocally(elapsed);
  switchTab("results");
}

function gradeExamLocally(elapsedSeconds) {
  let totalScore = 0;
  const maxScore = state.examQuestions.reduce((acc, q) => acc + (q.points || 5), 0);
  const moduleScores = {
    A: { earned: 0, max: 0, name: MODULE_NAMES.A },
    B: { earned: 0, max: 0, name: MODULE_NAMES.B },
    C: { earned: 0, max: 0, name: MODULE_NAMES.C },
    D: { earned: 0, max: 0, name: MODULE_NAMES.D },
  };

  const details = [];

  state.examQuestions.forEach(q => {
    const mod = q.module;
    const pts = q.points || 5;
    moduleScores[mod].max += pts;

    const userAns = (state.userAnswers[q.id] || "").trim();
    let isCorrect = false;

    if (q.type === "multiple_choice") {
      isCorrect = userAns.toUpperCase() === q.correct_answer.toUpperCase();
    } else {
      isCorrect = userAns.length >= 30;
    }

    if (isCorrect) {
      totalScore += pts;
      moduleScores[mod].earned += pts;
    }

    details.push({
      ...q,
      userAns,
      isCorrect,
      earned: isCorrect ? pts : 0,
    });
  });

  const percentage = Math.round((totalScore / maxScore) * 100);
  const isPassed = percentage >= 65;

  state.examResults = {
    totalScore,
    maxScore,
    percentage,
    isPassed,
    elapsedSeconds,
    moduleScores,
    details,
  };

  renderResultsView();
}

function renderResultsView() {
  const res = state.examResults;
  if (!res) return;

  const totalEl = document.getElementById("res-total-score");
  const pctEl = document.getElementById("res-percentage");
  const timeEl = document.getElementById("res-time-elapsed");
  const verdictEl = document.getElementById("res-verdict-badge");
  const modulesContainer = document.getElementById("res-modules-breakdown");
  const reviewContainer = document.getElementById("res-review-accordion");

  totalEl.textContent = `${res.totalScore} / ${res.maxScore}`;
  pctEl.textContent = `${res.percentage}%`;
  const m = Math.floor(res.elapsedSeconds / 60);
  const s = res.elapsedSeconds % 60;
  timeEl.textContent = `${m}p ${s}s`;

  if (res.isPassed) {
    verdictEl.textContent = " ĐẠT YÊU CẦU ĐẦU VÀO";
    verdictEl.style.backgroundColor = "var(--status-success-bg)";
    verdictEl.style.color = "var(--status-success)";
    verdictEl.style.border = "1px solid var(--status-success-border)";
  } else {
    verdictEl.textContent = "⚠️ CẦN RÀ SOÁT LẠI NỀN TẢNG";
    verdictEl.style.backgroundColor = "var(--status-warning-bg)";
    verdictEl.style.color = "var(--status-warning)";
    verdictEl.style.border = "1px solid var(--status-warning-border)";
  }

  // Render Module Breakdown
  modulesContainer.innerHTML = "";
  Object.entries(res.moduleScores).forEach(([modKey, data]) => {
    const pct = data.max > 0 ? Math.round((data.earned / data.max) * 100) : 0;
    const card = document.createElement("div");
    card.className = "module-perf-card";
    card.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
        <span style="font-weight: 700; font-size: 14px;">${data.name}</span>
        <span class="tabular-nums" style="font-weight: 700; color: var(--accent-primary);">${data.earned}/${data.max} đ (${pct}%)</span>
      </div>
      <div class="progress-track">
        <div class="progress-fill" style="width: ${pct}%;"></div>
      </div>
    `;
    modulesContainer.appendChild(card);
  });

  // Render Question Details Accordion
  renderReviewList("all");
}

function renderReviewList(filter) {
  const container = document.getElementById("res-review-accordion");
  if (!container || !state.examResults) return;
  container.innerHTML = "";

  state.examResults.details.forEach((item, idx) => {
    if (filter === "wrong" && item.isCorrect) return;
    if (filter === "correct" && !item.isCorrect) return;

    const acc = document.createElement("div");
    acc.className = "review-item";

    const icon = item.isCorrect ? "✅" : "❌";
    const statusText = item.isCorrect ? "Đúng (+5đ)" : "Sai (0đ)";

    acc.innerHTML = `
      <div class="review-item-header">
        <span>${icon} Câu ${idx + 1} [${item.id}] - ${MODULE_NAMES[item.module]} (${statusText})</span>
        <i data-lucide="chevron-down" style="width: 16px; height: 16px;"></i>
      </div>
      <div class="review-item-body">
        <p style="font-weight: 600; margin-bottom: 12px; color: var(--text-main);">${formatMathText(item.question)}</p>
        
        ${item.type === "multiple_choice" ? `
          <div style="font-size: 13px; margin-bottom: 12px; padding: 10px; background: #f8fafc; border-radius: 4px;">
            <p><strong>Lựa chọn của bạn:</strong> <span style="color: ${item.isCorrect ? 'var(--status-success)' : 'var(--status-danger)'}; font-weight: bold;">${item.userAns || 'Chưa chọn'}</span></p>
            <p><strong>Đáp án chính xác:</strong> <span style="color: var(--status-success); font-weight: bold;">${item.correct_answer}</span></p>
          </div>
        ` : `
          <div style="font-size: 13px; margin-bottom: 12px; padding: 10px; background: #f8fafc; border-radius: 4px;">
            <p><strong>Câu trả lời của bạn:</strong></p>
            <blockquote style="margin: 6px 0; color: #475569; font-style: italic;">${escapeHtml(item.userAns || 'Trống')}</blockquote>
            <p style="margin-top: 8px;"><strong>Hướng dẫn đáp án mẫu:</strong></p>
            <pre style="background: #1e293b; color: #f8fafc; padding: 10px; border-radius: 4px; margin-top: 4px;"><code>${escapeHtml(item.sample_answer)}</code></pre>
          </div>
        `}

        <div style="background: #eff6ff; border: 1px solid #bfdbfe; padding: 12px; border-radius: var(--radius-sm); font-size: 13px; color: #1e3a8a; line-height: 1.6;">
          <strong>💡 Giải thích chi tiết & Trực giác kỹ thuật:</strong><br>
          ${formatMathText(item.explanation)}
        </div>
      </div>
    `;

    acc.querySelector(".review-item-header").addEventListener("click", () => {
      acc.classList.toggle("open");
      renderMathAndCode();
    });

    container.appendChild(acc);
  });

  renderMathAndCode();
  if (window.lucide) window.lucide.createIcons();
}

// ------------------------------------------------------------------
// PRACTICE MODE (FILTER BY MODULE & DIFFICULTY)
// ------------------------------------------------------------------
function initPracticeView() {
  const modSelect = document.getElementById("practice-module-select");
  const diffSelect = document.getElementById("practice-diff-select");

  if (modSelect && !modSelect.dataset.initialized) {
    modSelect.dataset.initialized = "true";
    modSelect.addEventListener("change", e => {
      state.practiceModule = e.target.value;
      updatePracticeQuestions();
    });
  }

  if (diffSelect && !diffSelect.dataset.initialized) {
    diffSelect.dataset.initialized = "true";
    diffSelect.addEventListener("change", e => {
      state.practiceDifficulty = e.target.value;
      updatePracticeQuestions();
    });
  }

  updatePracticeQuestions();
}

function updatePracticeQuestions() {
  const questions = state.allQuestions[state.practiceModule] || [];
  if (state.practiceDifficulty === "all") {
    state.practiceQuestions = questions;
  } else {
    state.practiceQuestions = questions.filter(q => q.difficulty === state.practiceDifficulty);
  }
  renderPracticeList();
}

function toggleAllPracticeExplanations() {
  state.practiceShowAllExplanations = !state.practiceShowAllExplanations;
  const label = document.getElementById("toggle-all-exp-label");
  if (label) {
    label.textContent = state.practiceShowAllExplanations ? "Thu gọn lời giải" : "Mở hết lời giải";
  }
  const btn = document.getElementById("btn-toggle-all-explanations");
  if (btn) {
    btn.classList.toggle("btn-primary", state.practiceShowAllExplanations);
    btn.classList.toggle("btn-secondary", !state.practiceShowAllExplanations);
  }
  renderPracticeList();
}

function toggleSinglePracticeExplanation(qid) {
  if (state.practiceExpanded.has(qid)) {
    state.practiceExpanded.delete(qid);
  } else {
    state.practiceExpanded.add(qid);
  }
  renderPracticeList();
}

function renderPracticeList() {
  const container = document.getElementById("practice-questions-list");
  if (!container) return;
  container.innerHTML = "";

  const countBadge = document.getElementById("practice-count-badge");
  if (countBadge) countBadge.textContent = `${state.practiceQuestions.length} câu hỏi`;

  state.practiceQuestions.forEach((q, idx) => {
    const item = document.createElement("div");
    item.className = "question-viewport";
    item.style.marginBottom = "24px";

    const feedback = state.practiceFeedback[q.id];
    const isExpanded = state.practiceShowAllExplanations || state.practiceExpanded.has(q.id) || !!feedback;

    item.innerHTML = `
      <div class="question-meta-bar">
        <div style="display: flex; align-items: center; gap: 8px;">
          <span class="module-badge">${MODULE_NAMES[q.module]}</span>
          <span class="difficulty-badge ${getDiffClass(q.difficulty)}">${q.difficulty || 'Trung bình'}</span>
        </div>
        <div style="display: flex; align-items: center; gap: 10px;">
          <button class="btn btn-secondary btn-sm" onclick="toggleSinglePracticeExplanation('${q.id}')" style="font-size: 12px; padding: 5px 12px;">
            <i data-lucide="${isExpanded ? 'eye-off' : 'help-circle'}" style="width: 14px; height: 14px;"></i>
            ${isExpanded ? 'Ẩn lời giải' : 'Xem lời giải & phân tích'}
          </button>
        </div>
      </div>
      <div class="question-title-text">
        <strong>Câu ${idx + 1} [${q.id}]:</strong> ${formatMathText(q.question)}
      </div>
      <div id="practice-opts-${q.id}"></div>
      <div id="practice-feedback-${q.id}" style="margin-top: 16px;"></div>
    `;

    container.appendChild(item);

    const optsDiv = item.querySelector(`#practice-opts-${q.id}`);
    const fbDiv = item.querySelector(`#practice-feedback-${q.id}`);

    if (q.type === "multiple_choice") {
      const list = document.createElement("div");
      list.className = "options-list";

      Object.entries(q.options).forEach(([k, v]) => {
        const opt = document.createElement("div");
        opt.className = "option-item";

        // Restore past answer highlight
        if (feedback) {
          if (k === feedback.selectedKey) {
            opt.style.borderColor = feedback.isCorrect ? "var(--status-success)" : "var(--status-danger)";
            opt.style.backgroundColor = feedback.isCorrect ? "var(--status-success-bg)" : "var(--status-danger-bg)";
          } else if (k === q.correct_answer) {
            opt.style.borderColor = "var(--status-success)";
            opt.style.backgroundColor = "var(--status-success-bg)";
          }
        }

        opt.innerHTML = `
          <div class="option-key">${k}</div>
          <div class="option-text">${formatMathText(v)}</div>
        `;
        opt.addEventListener("click", () => {
          checkPracticeAnswer(q, k, fbDiv, list);
        });
        list.appendChild(opt);
      });
      optsDiv.appendChild(list);

      // Render explanation card if expanded
      if (isExpanded) {
        fbDiv.innerHTML = `
          <div style="padding: 16px; border-radius: 6px; background-color: #f8fafc; border: 1px solid var(--border-subtle); font-size: 13.5px; line-height: 1.6;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; border-bottom: 1px solid var(--border-subtle); padding-bottom: 8px;">
              <span style="font-weight: 700; color: var(--accent-primary);">
                <i data-lucide="check-circle" style="width: 15px; height: 15px; display: inline-block; vertical-align: middle;"></i> Đáp án đúng: <strong>${q.correct_answer}</strong>
              </span>
              ${feedback ? (feedback.isCorrect ? '<span style="color: var(--status-success); font-weight: 700;">Đã trả lời đúng 🎉</span>' : '<span style="color: var(--status-danger); font-weight: 700;">Đã chọn: ' + feedback.selectedKey + ' (Chưa đúng) ❌</span>') : '<span style="color: var(--text-muted); font-size: 12px; font-weight: 600;">Chế độ ôn tập</span>'}
            </div>
            <div style="color: var(--text-main); margin-top: 8px;">
              <strong style="color: var(--accent-primary);">💡 Giải thích & Phân tích chi tiết:</strong>
              <div style="margin-top: 6px;">${formatMathText(q.explanation)}</div>
            </div>
          </div>
        `;
      }
    } else {
      // Scenario Question
      if (isExpanded) {
        fbDiv.innerHTML = `
          <div style="background: #f8fafc; border: 1px solid var(--border-subtle); padding: 18px; border-radius: 6px; font-size: 13.5px; line-height: 1.6;">
            <div style="font-weight: 700; color: var(--accent-primary); margin-bottom: 8px;">
              <i data-lucide="check-square" style="width: 15px; height: 15px; display: inline-block; vertical-align: middle;"></i> Hướng Dẫn Đáp Án Mẫu / Solution:
            </div>
            <pre style="background: #0f172a; color: #f8fafc; padding: 14px; border-radius: 6px; margin: 10px 0; overflow-x: auto; font-family: var(--font-mono); font-size: 13px; line-height: 1.5;"><code>${escapeHtml(q.sample_answer)}</code></pre>
            <div style="margin-top: 14px; color: var(--text-main); border-top: 1px solid var(--border-subtle); padding-top: 10px;">
              <strong style="color: var(--accent-primary);">💡 Phân Tích Kỹ Thuật & Tiêu Chí Giám Khảo VinUni:</strong>
              <div style="margin-top: 6px;">${formatMathText(q.explanation)}</div>
            </div>
          </div>
        `;
      } else {
        optsDiv.innerHTML = `
          <button class="btn btn-secondary" onclick="toggleSinglePracticeExplanation('${q.id}')">
            <i data-lucide="eye" style="width:16px;height:16px;"></i> Xem hướng dẫn giải & phân tích chuyên sâu
          </button>
        `;
      }
    }
  });

  renderMathAndCode();
  if (window.lucide) window.lucide.createIcons();
}

function checkPracticeAnswer(q, selectedKey, feedbackContainer, optionsList) {
  const isCorrect = selectedKey.toUpperCase() === q.correct_answer.toUpperCase();
  state.practiceFeedback[q.id] = { selectedKey, isCorrect };
  state.practiceExpanded.add(q.id);

  Array.from(optionsList.children).forEach(el => {
    const key = el.querySelector(".option-key").textContent.trim();
    el.classList.remove("selected");
    if (key === selectedKey) {
      el.style.borderColor = isCorrect ? "var(--status-success)" : "var(--status-danger)";
      el.style.backgroundColor = isCorrect ? "var(--status-success-bg)" : "var(--status-danger-bg)";
    } else if (key === q.correct_answer) {
      el.style.borderColor = "var(--status-success)";
      el.style.backgroundColor = "var(--status-success-bg)";
    }
  });

  feedbackContainer.innerHTML = `
    <div style="padding: 16px; border-radius: 6px; background-color: ${isCorrect ? 'var(--status-success-bg)' : 'var(--status-danger-bg)'}; border: 1px solid ${isCorrect ? 'var(--status-success-border)' : 'var(--status-danger-border)'}; font-size: 13.5px; line-height: 1.6;">
      <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; border-bottom: 1px solid ${isCorrect ? '#a7f3d0' : '#fecaca'}; padding-bottom: 8px;">
        <p style="font-weight: 700; color: ${isCorrect ? 'var(--status-success)' : 'var(--status-danger)'};">
          ${isCorrect ? '🎉 Chính xác!' : `❌ Chưa đúng. Đáp án chính xác là ${q.correct_answer}.`}
        </p>
        <span style="font-size: 12px; color: ${isCorrect ? 'var(--status-success)' : 'var(--status-danger)'}; font-weight: 600;">
          Lựa chọn của bạn: <strong>${selectedKey}</strong>
        </span>
      </div>
      <div style="color: var(--text-main); margin-top: 8px;">
        <strong style="color: var(--accent-primary);">💡 Giải thích & Phân tích chi tiết:</strong>
        <div style="margin-top: 6px;">${formatMathText(q.explanation)}</div>
      </div>
    </div>
  `;
  renderMathAndCode();
  if (window.lucide) window.lucide.createIcons();
}

// ------------------------------------------------------------------
// STUDY CENTER & DOCS VIEWER
// ------------------------------------------------------------------
async function loadDocumentContent(docName) {
  state.currentDoc = docName;
  const contentEl = document.getElementById("doc-content-article");
  if (!contentEl) return;

  contentEl.innerHTML = `<p style="color: var(--text-muted);">Đang tải tài liệu...</p>`;

  document.querySelectorAll(".doc-nav-item").forEach(item => {
    item.classList.toggle("active", item.dataset.doc === docName);
  });

  try {
    let mdText = "";
    if (window.EMBEDDED_DOCS && window.EMBEDDED_DOCS[docName]) {
      mdText = window.EMBEDDED_DOCS[docName];
    } else {
      try {
        const res = await fetch(`docs/${docName}`);
        if (res.ok) mdText = await res.text();
        else throw new Error("Fallback to API");
      } catch {
        const resApi = await fetch(`/api/docs/${docName}`);
        const data = await resApi.json();
        mdText = data.content || "";
      }
    }

    contentEl.innerHTML = parseMarkdownToHtml(mdText);
    renderMathAndCode();
  } catch (e) {
    contentEl.innerHTML = `<p style="color: var(--status-danger);">Lỗi tải tài liệu: ${e.message}</p>`;
  }
}

// Markdown Parser with Marked.js support, marked-katex-extension, and fallback
let markedInitialized = false;
function initMarkedExtension() {
  if (!markedInitialized && window.marked && window.markedKatex) {
    try {
      window.marked.use(window.markedKatex({ throwOnError: false, nonStandard: true }));
      markedInitialized = true;
    } catch (e) {
      console.warn("Could not register markedKatex extension:", e);
    }
  }
}

function parseMarkdownToHtml(md) {
  initMarkedExtension();
  if (window.marked && typeof window.marked.parse === "function") {
    try {
      const html = window.marked.parse(md, { gfm: true, breaks: true });
      return `<div class="doc-markdown-body">${html}</div>`;
    } catch (err) {
      console.warn("marked parsing error, falling back:", err);
    }
  }
  let html = md
    .replace(/^### (.*$)/gim, '<h3>$1</h3>')
    .replace(/^## (.*$)/gim, '<h2>$1</h2>')
    .replace(/^# (.*$)/gim, '<h1>$1</h1>')
    .replace(/^\> (.*$)/gim, '<blockquote style="border-left: 3px solid #94a3b8; padding-left: 12px; margin: 12px 0; color: #475569;">$1</blockquote>')
    .replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/gim, '<em>$1</em>')
    .replace(/```python([\s\S]*?)```/gim, '<pre><code class="language-python">$1</code></pre>')
    .replace(/```([\s\S]*?)```/gim, '<pre><code>$1</code></pre>')
    .replace(/\n\n/gim, '</p><p>')
    .replace(/^\- (.*$)/gim, '<li>$1</li>');
  return `<div class="doc-markdown-body">${html}</div>`;
}

// Keyboard shortcuts for exam taking (1,2,3,4 or A,B,C,D; N, P, F)
function setupKeyboardShortcuts() {
  document.addEventListener("keydown", e => {
    if (state.currentTab !== "exam" || state.examSubmitted) return;
    const tag = e.target.tagName.toLowerCase();
    if (tag === "input" || tag === "textarea") return;

    const key = e.key.toUpperCase();
    if (["A", "B", "C", "D"].includes(key)) {
      const q = state.examQuestions[state.currentIndex];
      if (q && q.type === "multiple_choice") selectOption(q.id, key);
    } else if (["1", "2", "3", "4"].includes(key)) {
      const map = { "1": "A", "2": "B", "3": "C", "4": "D" };
      const q = state.examQuestions[state.currentIndex];
      if (q && q.type === "multiple_choice") selectOption(q.id, map[key]);
    } else if (key === "N" || e.key === "ArrowRight") {
      nextQuestion();
    } else if (key === "P" || e.key === "ArrowLeft") {
      prevQuestion();
    } else if (key === "F") {
      toggleFlag();
    }
  });
}

// Utility: Math formatting with KaTeX & Code with Prism
function renderMathAndCode() {
  if (window.renderMathInElement) {
    try {
      window.renderMathInElement(document.body, {
        delimiters: [
          { left: "$$", right: "$$", display: true },
          { left: "$", right: "$", display: false },
          { left: "\\[", right: "\\]", display: true },
          { left: "\\(", right: "\\)", display: false },
        ],
        ignoredTags: ["script", "noscript", "style", "textarea", "pre", "code"],
        ignoredClasses: ["no-math", "ignore-katex", "currency-token", "btn", "timer-box", "brand-logo-badge"],
        preProcess: function(math) {
          // Clean up any stray <br> or &lt;br&gt; that might have slipped into math
          return math.replace(/<br\s*\/?>/gi, " ");
        },
        throwOnError: false,
        strict: false,
      });
    } catch (e) {
      console.warn("KaTeX render error:", e);
    }
  }

  if (window.Prism) {
    window.Prism.highlightAll();
  }
}

function formatMathText(str) {
  if (!str || typeof str !== "string") return "";
  try {
    // Split by display math $$...$$ and inline math $...$ so we NEVER insert <br> inside math blocks
    const parts = str.split(/(\$\$[\s\S]*?\$\$|\$[^\$\n]+?\$)/g);
    return parts.map((part, idx) => {
      // If it's a math delimiter (odd index in split), preserve without injecting <br>
      if (idx % 2 === 1) {
        return part;
      }
      // Only outside math blocks, convert newlines to <br>
      return part.replace(/\n/g, "<br>");
    }).join("");
  } catch (err) {
    return str;
  }
}

function getDiffClass(diff) {
  if (diff === "Cơ bản") return "diff-easy";
  if (diff === "Trung bình") return "diff-med";
  return "diff-hard";
}

function escapeHtml(text) {
  if (!text) return "";
  return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

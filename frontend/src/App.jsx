import { useState } from "react";
import { api } from "./api.js";

function Loading({ text }) {
  return (
    <div className="loading">
      <div className="spinner"></div>
      <p>{text}</p>
    </div>
  );
}

function Auth({ onAuth }) {
  const [mode, setMode] = useState("login");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function submit(e) {
    e.preventDefault();
    setBusy(true); setError("");
    const res = mode === "login"
      ? await api.login({ email, password })
      : await api.signup({ name, email, password });
    setBusy(false);
    if (!res.success) return setError(res.message);
    localStorage.setItem("careerai_token", res.token);
    onAuth(res.user);
  }

  return (
    <div className="auth-box">
      <h1>CareerAI</h1>
      <p className="sub">AI-powered career & placement analyzer</p>
      <form onSubmit={submit}>
        {mode === "signup" && (
          <input placeholder="Full name" value={name} onChange={(e) => setName(e.target.value)} required />
        )}
        <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} required />
        {error && <p className="error">{error}</p>}
        <button disabled={busy}>{busy ? "Please wait..." : mode === "login" ? "Log in" : "Create account"}</button>
      </form>
      <button className="ghost" onClick={() => { setMode(mode === "login" ? "signup" : "login"); setError(""); }}>
        {mode === "login" ? "New here? Create an account" : "Already have an account? Log in"}
      </button>
    </div>
  );
}

function ResumeAnalyzer({ setDemo }) {
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  async function handleFile(e) {
    const file = e.target.files[0];
    if (!file) return;
    if (!["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"].includes(file.type)) {
      return setError("Only PDF or DOCX files are allowed.");
    }
    if (file.size > 5 * 1024 * 1024) return setError("File exceeds the 5 MB limit.");
    setError(""); setBusy(true); setResult(null);
    const fd = new FormData();
    fd.append("file", file);
    const res = await api.analyzeResume(fd);
    setBusy(false);
    if (!res.success) return setError(res.message);
    if (res.demo) setDemo(true);
    setResult(res.analysis);
  }

  return (
    <div className="card">
      <h2>Resume Analyzer</h2>
      <label className="dropzone">
        <input type="file" accept=".pdf,.docx" style={{ display: "none" }} onChange={handleFile} />
        Click to upload your resume (PDF / DOCX, max 5 MB)
      </label>
      {error && <p className="error">{error}</p>}
      {busy && <Loading text="AI is analyzing your resume..." />}
      {result && (
        <div>
          <p className="muted">{result.summary}</p>
          <h3>Overall Score</h3>
          <div className="score">{result.overallScore}/100</div>
          <h3>Strengths</h3>
          <ul className="clean">{result.strengths.map((s, i) => <li key={i}>{s}</li>)}</ul>
          <h3>Areas to improve</h3>
          <ul className="clean">{result.weaknesses.map((s, i) => <li className="bad" key={i}>{s}</li>)}</ul>
          <h3>Recommended roles</h3>
          <div className="chips">{result.recommendedRoles.map((r, i) => <span className="chip" key={i}>{r}</span>)}</div>
          <h3>Skill gaps</h3>
          <div className="chips">{result.skillGaps.map((r, i) => <span className="chip" key={i}>{r}</span>)}</div>
        </div>
      )}
    </div>
  );
}

function JobMatch({ setDemo }) {
  const [skills, setSkills] = useState("");
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  async function go() {
    setBusy(true); setError(""); setResult(null);
    const res = await api.matchJobs({ skills });
    setBusy(false);
    if (!res.success) return setError(res.message);
    if (res.demo) setDemo(true);
    setResult(res.result.matches);
  }
  return (
    <div className="card">
      <h2>Job Matching</h2>
      <textarea rows={3} placeholder="Paste your skills, e.g. Python, React, SQL..." value={skills} onChange={(e) => setSkills(e.target.value)} />
      <button className="small" onClick={go} disabled={busy || !skills.trim()}>Find matches</button>
      {error && <p className="error">{error}</p>}
      {busy && <Loading text="AI is matching jobs for you..." />}
      {result && result.map((m, i) => (
        <div className="match-row" key={i}>
          <div>
            <strong>{m.title}</strong>
            <div className="chips">{m.missingSkills.map((s, j) => <span className="chip" key={j}>{s}</span>)}</div>
            <p className="muted">{m.advice}</p>
          </div>
          <span className="match-score">{m.score}%</span>
        </div>
      ))}
    </div>
  );
}

function Roadmap({ setDemo }) {
  const [role, setRole] = useState("");
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  async function go() {
    setBusy(true); setError(""); setResult(null);
    const res = await api.generateRoadmap({ targetRole: role });
    setBusy(false);
    if (!res.success) return setError(res.message);
    if (res.demo) setDemo(true);
    setResult(res.result);
  }
  return (
    <div className="card">
      <h2>Career Roadmap Generator</h2>
      <input placeholder="Target role, e.g. Full-Stack Developer" value={role} onChange={(e) => setRole(e.target.value)} />
      <button className="small" onClick={go} disabled={busy || !role.trim()}>Generate roadmap</button>
      {error && <p className="error">{error}</p>}
      {busy && <Loading text="AI is building your roadmap..." />}
      {result && (
        <div>
          {result.steps.map((s, i) => (
            <div className="phase" key={i}>
              <div className="p-phase">{s.phase}</div>
              <div className="p-title">{s.title}</div>
              <ul className="clean">{s.items.map((it, j) => <li key={j}>{it}</li>)}</ul>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function Projects({ setDemo }) {
  const [gap, setGap] = useState("");
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  async function go() {
    setBusy(true); setError(""); setResult(null);
    const res = await api.recommendProjects(gap);
    setBusy(false);
    if (!res.success) return setError(res.message);
    if (res.demo) setDemo(true);
    setResult(res.result.recommendations);
  }
  return (
    <div className="card">
      <h2>Project Recommendations</h2>
      <input placeholder="Skill gap, e.g. Docker" value={gap} onChange={(e) => setGap(e.target.value)} />
      <button className="small" onClick={go} disabled={busy}>Get projects</button>
      {error && <p className="error">{error}</p>}
      {busy && <Loading text="AI is finding projects for you..." />}
      {result && result.map((p, i) => (
        <div key={i} style={{ marginTop: 14 }}>
          <strong>{p.title}</strong> <span className="chip">{p.difficulty}</span>
          <p className="muted">{p.description}</p>
          <div className="chips">{p.skills.map((s, j) => <span className="chip" key={j}>{s}</span>)}</div>
        </div>
      ))}
    </div>
  );
}

function Interview({ setDemo }) {
  const [role, setRole] = useState("");
  const [started, setStarted] = useState(false);
  const [question, setQuestion] = useState("");
  const [index, setIndex] = useState(0);
  const [total] = useState(5);
  const [answer, setAnswer] = useState("");
  const [feedback, setFeedback] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function start() {
    setBusy(true); setError("");
    const res = await api.startInterview(role);
    setBusy(false);
    if (!res.success) return setError(res.message);
    if (res.demo) setDemo(true);
    setQuestion(res.question); setIndex(res.questionIndex);
    setStarted(true); setFeedback(null); setAnswer("");
  }

  async function submit() {
    setBusy(true); setError("");
    const res = await api.evaluateAnswer({ role, answer, questionIndex: index });
    setBusy(false);
    if (!res.success) return setError(res.message);
    setFeedback(res.evaluation);
    if (res.finished) {
      setQuestion(null);
    } else {
      setQuestion(res.question); setIndex(res.questionIndex); setAnswer("");
    }
  }

  return (
    <div className="card">
      <h2>Interview Simulator</h2>
      {!started ? (
        <div>
          <input placeholder="Role to practice for, e.g. Backend Engineer" value={role} onChange={(e) => setRole(e.target.value)} />
          <button className="small" onClick={start} disabled={busy}>Start interview</button>
          {error && <p className="error">{error}</p>}
          {busy && <Loading text="AI is preparing your interview..." />}
        </div>
      ) : (
        <div>
          {question ? (
            <div>
              <p className="muted">Question {index + 1} of {total}</p>
              <p className="interview-q">{question}</p>
              <textarea rows={5} placeholder="Type your answer..." value={answer} onChange={(e) => setAnswer(e.target.value)} />
              <button className="small" onClick={submit} disabled={busy || !answer.trim()}>
                {busy ? "Evaluating..." : "Submit answer"}
              </button>
            </div>
          ) : (
            <p className="score">Interview complete</p>
          )}
          {error && <p className="error">{error}</p>}
          {busy && <Loading text="AI is evaluating your answer..." />}
          {feedback && (
            <div className="feedback">
              <div className="f-score">{feedback.score}/100</div>
              <p>{feedback.feedback}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

const TABS = [
  ["resume", "Resume Analyzer"],
  ["jobs", "Job Match"],
  ["roadmap", "Roadmap"],
  ["projects", "Projects"],
  ["interview", "Interview"],
];

export default function App() {
  const [user, setUser] = useState(() => {
    const raw = localStorage.getItem("careerai_user");
    return raw ? JSON.parse(raw) : null;
  });
  const [tab, setTab] = useState("resume");
  const [demo, setDemo] = useState(false);

  function onAuth(u) {
    localStorage.setItem("careerai_user", JSON.stringify(u));
    setUser(u);
  }
  function logout() {
    localStorage.removeItem("careerai_token");
    localStorage.removeItem("careerai_user");
    setUser(null); setDemo(false);
  }

  if (!user) return <div className="container"><Auth onAuth={onAuth} /></div>;

  return (
    <div className="container">
      <header className="topbar">
        <span className="brand">CareerAI</span>
        {demo && <span className="badge">Demo Mode</span>}
        <span className="spacer"></span>
        <span className="muted">Hi, {user.name}</span>
        <button className="small ghost" style={{ width: "auto" }} onClick={logout}>Log out</button>
      </header>
      <nav className="tabs">
        {TABS.map(([id, label]) => (
          <button key={id} className={tab === id ? "active" : ""} onClick={() => setTab(id)}>{label}</button>
        ))}
      </nav>
      {tab === "resume" && <ResumeAnalyzer setDemo={setDemo} />}
      {tab === "jobs" && <JobMatch setDemo={setDemo} />}
      {tab === "roadmap" && <Roadmap setDemo={setDemo} />}
      {tab === "projects" && <Projects setDemo={setDemo} />}
      {tab === "interview" && <Interview setDemo={setDemo} />}
    </div>
  );
}

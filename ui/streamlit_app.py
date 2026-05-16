#!/usr/bin/env python3
"""
LexBridge - Single-File Streamlit UI
Upload any legal document. Understand it in your language. Know your rights.
"""
import streamlit as st
import tempfile
import json
import time
from datetime import datetime
from typing import Literal
import sys
import os

# BASE_DIR = os.path.abspath(
#     os.path.join(os.path.dirname(__file__), "..")
# )

# sys.path.append(BASE_DIR)


# ============================================================================
# 📦 CONFIGURATION
# ============================================================================
class Config:
    PAGE_TITLE = "■ LexBridge"
    PAGE_ICON = "⚖️"
    APP_TAGLINE = "Upload any legal document. Understand it in your language. Know your rights."
    DEFAULT_API_URL = "http://localhost:8000/analyze"
    API_TIMEOUT_SECONDS = 180
    AVAILABLE_MODELS = ("llama-3.3-70b-versatile", "mixtral-8x7b-32768")
    DEFAULT_MODEL = "llama-3.3-70b-versatile"
    DEFAULT_TEMPERATURE = 0.1
    MAX_FILE_SIZE_MB = 10
    SUPPORTED_EXTENSIONS = (".pdf", ".png", ".jpg", ".jpeg",".txt")
    URGENCY_COLORS = {"CRITICAL": "#ff4757", "HIGH": "#ffa502", "MEDIUM": "#4ecdc4", "LOW": "#2ed573"}
    SUPPORTED_LANGUAGES = {
        "en": "English", "es": "Español", "fr": "Français", "ar": "العربية",
        "zh": "中文", "hi": "हिन्दी", "pt": "Português"
    }

    @classmethod
    def get_model(cls):
        return os.getenv("MODEL_NAME", cls.DEFAULT_MODEL)
    
    @classmethod
    def get_temp(cls):
        return float(os.getenv("TEMPERATURE", cls.DEFAULT_TEMPERATURE))


# ============================================================================
# 🎨 CUSTOM CSS
# ============================================================================
CUSTOM_CSS = """
<style>
    .stApp { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); }
    .main-title { font-size: 2.5rem; font-weight: 700; background: linear-gradient(90deg, #c9a227, #8b7500);
                  -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.5rem; }
    .subtitle { color: #a0aec0; font-size: 1.1rem; margin-bottom: 2rem; }
    .card { background: rgba(30, 30, 50, 0.9); border: 1px solid rgba(100, 100, 150, 0.3); border-radius: 12px;
            padding: 1.2rem; margin: 0.5rem 0; transition: all 0.3s ease; }
    .card:hover { border-color: #c9a227; box-shadow: 0 4px 20px rgba(201, 162, 39, 0.15); }
    .pipeline { display: flex; gap: 0.5rem; margin: 1.5rem 0; flex-wrap: wrap; }
    .step { flex: 1; min-width: 100px; padding: 0.8rem; border-radius: 10px; text-align: center; font-weight: 500;
            border: 2px solid transparent; transition: all 0.3s ease; font-size: 0.9rem; }
    .step.waiting { background: rgba(50, 50, 80, 0.5); color: #666; }
    .step.active { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-color: #a855f7;
                   animation: pulse 2s infinite; }
    .step.done { background: rgba(201, 162, 39, 0.2); color: #c9a227; border-color: #c9a227; }
    .step.error { background: rgba(255, 71, 87, 0.2); color: #ff4757; border-color: #ff4757; }
    @keyframes pulse { 0%, 100% { box-shadow: 0 0 0 0 rgba(168, 85, 247, 0.4); }
                        50% { box-shadow: 0 0 0 10px rgba(168, 85, 247, 0); } }
    .metric-card { background: rgba(40, 40, 70, 0.6); border-radius: 10px; padding: 1rem; text-align: center;
                   border-left: 4px solid #c9a227; }
    .metric-value { font-size: 1.8rem; font-weight: 700; color: #fff; }
    .metric-label { color: #a0aec0; font-size: 0.85rem; margin-top: 0.3rem; }
    .urgency { display: inline-block; padding: 0.3rem 0.8rem; border-radius: 20px; font-weight: 600; font-size: 0.85rem; }
    .urgency.critical { background: rgba(255, 71, 87, 0.2); color: #ff4757; border: 1px solid #ff4757; }
    .urgency.high { background: rgba(255, 165, 2, 0.2); color: #ffa502; border: 1px solid #ffa502; }
    .urgency.medium { background: rgba(78, 205, 196, 0.2); color: #4ecdc4; border: 1px solid #4ecdc4; }
    .urgency.low { background: rgba(46, 213, 115, 0.2); color: #2ed573; border: 1px solid #2ed573; }
    .risk-item { background: rgba(50, 50, 80, 0.4); border-left: 4px solid #667eea; padding: 1rem; margin: 0.5rem 0;
                 border-radius: 0 8px 8px 0; }
    .risk-critical { border-left-color: #ff4757; } .risk-high { border-left-color: #ffa502; }
    .risk-medium { border-left-color: #4ecdc4; } .risk-low { border-left-color: #2ed573; }
    .risk-quote { font-family: monospace; background: rgba(30, 30, 50, 0.6); padding: 0.5rem; border-radius: 4px;
                  margin: 0.5rem 0; font-size: 0.9rem; }
    .action-item { display: flex; align-items: flex-start; gap: 0.8rem; padding: 0.8rem; background: rgba(40, 40, 70, 0.4);
                   border-radius: 8px; margin: 0.5rem 0; }
    .action-priority { font-weight: 700; min-width: 100px; padding: 0.2rem 0.5rem; border-radius: 4px;
                       font-size: 0.8rem; text-align: center; }
    .priority-do-today { background: rgba(255, 71, 87, 0.3); color: #ff6b6b; }
    .priority-this-week { background: rgba(255, 165, 2, 0.3); color: #ffa502; }
    .priority-when-possible { background: rgba(78, 205, 196, 0.3); color: #4ecdc4; }
    .disclaimer { background: rgba(255, 193, 7, 0.15); border: 1px solid #ffc107; border-left: 4px solid #ffc107;
                  padding: 1rem; border-radius: 0 8px 8px 0; margin: 1rem 0; font-size: 0.9rem; }
    .stButton > button { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none;
                         border-radius: 8px; padding: 0.8rem 2rem; font-weight: 600; transition: all 0.3s ease; }
    .stButton > button:hover { transform: translateY(-2px); box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4); }
    .streamlit-expanderHeader { background: rgba(30, 30, 50, 0.8) !important; border-radius: 8px !important;
                                border: 1px solid rgba(100, 100, 150, 0.3) !important; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    .fade-in { animation: fadeIn 0.4s ease forwards; }
    @media (max-width: 768px) { .pipeline { flex-direction: column; } .step { min-width: 100%; } }
</style>
"""

# ============================================================================
# 🧩 REUSABLE COMPONENTS
# ============================================================================
def render_metric(label, value, color="#c9a227"):
    st.markdown(f'<div class="metric-card" style="border-left-color:{color}"><div class="metric-value" style="color:{color}">{value}</div><div class="metric-label">{label}</div></div>', unsafe_allow_html=True)

def render_urgency_badge(urgency):
    return f'<span class="urgency {urgency.lower()}">{urgency}</span>'

def render_risk_item(risk):
    sev = risk.get('severity', 'MEDIUM').lower()
    return f"""<div class="risk-item risk-{sev}">
        <strong>{render_urgency_badge(risk.get('severity', 'MEDIUM'))}</strong>
        <p style="margin:0.5rem 0">{risk.get('plain_issue', '')}</p>
        {f'<div class="risk-quote">"{risk.get("quote", "")}"</div>' if risk.get('quote') else ''}
    </div>"""

def render_action_item(idx, action):
    prio = action.get('priority', 'WHEN POSSIBLE').upper().replace(' ', '-')
    return f"""<div class="action-item">
        <div class="action-priority priority-{prio.lower()}">{prio}</div>
        <div><strong>{action.get('action', '')}</strong>
        <p style="margin:0.3rem 0;color:#a0aec0;font-size:0.9rem">{action.get('reason', '')}</p>
        {f'<small>📅 {action.get("deadline", "")}</small>' if action.get('deadline') else ''}</div>
    </div>"""

def render_pipeline_step(name, desc, status, icon):
    cls = {"done": "done", "active": "active", "error": "error"}.get(status, "waiting")
    return f'<div class="step {cls}"><div style="font-size:1.3rem;margin-bottom:0.3rem">{icon}</div><div style="font-weight:600">{name}</div><div style="font-size:0.75rem;opacity:0.8">{desc}</div></div>'

# ============================================================================
# 🔄 PIPELINE VISUALIZER
# ============================================================================
class PipelineVisualizer:
    STEPS = [
        {"name": "📄 Parse", "desc": "Extract text + detect type"},
        {"name": "⚠️ Extract", "desc": "Find risks & deadlines"},
        {"name": "🗣️ Explain", "desc": "Plain language + translate"},
        {"name": "⚖️ Rights", "desc": "RAG: retrieve legal rights"},
        {"name": "📝 Plan", "desc": "Action plan + draft letter"}
    ]
    def __init__(self):
        self._placeholders = [st.empty() for _ in self.STEPS]
    def render(self, current, status="active"):
        for i, step in enumerate(self.STEPS):
            if i < current: s, ic = "done", "✓"
            elif i == current: s, ic = ("active" if status=="active" else "error"), ("●" if status=="active" else "✗")
            else: s, ic = "waiting", "○"
            with self._placeholders[i]:
                st.markdown(render_pipeline_step(step["name"], step["desc"], s, ic), unsafe_allow_html=True)
    def reset(self): self.render(-1)
    def complete(self): self.render(len(self.STEPS), "done")
    def error_at(self, idx): self.render(idx, "error")

# ============================================================================
# 📐 UI SECTIONS
# ============================================================================
def render_sidebar():
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        mode = st.radio("Processing Mode", ["🔗 Local (HF Spaces)", "🌐 Remote API"], index=0)
        if "Remote" in mode:
            api = st.text_input("API Endpoint", value=os.getenv("API_URL", Config.DEFAULT_API_URL))
            st.session_state["api_url"] = api
        else:
            st.info("🔗 Running LangGraph locally")
            st.session_state.pop("api_url", None)
        st.divider()
        st.markdown("### 🤖 Model Settings")
        st.selectbox("LLM Model", Config.AVAILABLE_MODELS, index=Config.AVAILABLE_MODELS.index(Config.DEFAULT_MODEL), key="model_name")
        st.slider("Temperature", 0.0, 1.0, Config.DEFAULT_TEMPERATURE, step=0.1, key="temperature")
        st.divider()
        st.markdown("### 📦 Sample Documents")
        sample_docs = {"🏠 Eviction Notice (Fake)": "eviction", "📜 Contract (Fake)": "contract"}
        sel = st.selectbox("Choose demo", list(sample_docs.keys()))
        if st.button("🎯 Load Sample", use_container_width=True):
            st.session_state["sample_type"] = sample_docs[sel]
            st.rerun()
        st.divider()
        if st.button("🗑️ Clear Session", use_container_width=True):
            for k in list(st.session_state.keys()):
                if k not in ["api_url", "model_name", "temperature"]: del st.session_state[k]
            st.rerun()
        with st.expander("🆓 Free Legal Help"):
            st.markdown("- [LawHelp.org](https://www.lawhelp.org)\n- [CFPB Complaints](https://consumerfinance.gov/complaint)\n- [HUD Counseling](https://hud.gov/findacounselor)")

def render_header():
    c1, c2 = st.columns([1, 4])
    with c1: st.markdown("<div style='font-size:3rem'>⚖️</div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="main-title">{Config.PAGE_TITLE}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="subtitle">{Config.APP_TAGLINE}</div>', unsafe_allow_html=True)
    st.markdown("""<div class="disclaimer">⚠️ <strong>Information only, not legal advice.</strong> LexBridge helps you understand documents and find rights. For serious matters, always consult a qualified attorney or free legal aid clinic.</div>""", unsafe_allow_html=True)

def render_inputs():
    with st.expander("📥 Upload Legal Document", expanded=True):
        c1, c2 = st.columns([3, 1])
        with c1:
            file = st.file_uploader("Choose PDF or image", type=list(Config.SUPPORTED_EXTENSIONS), help=f"Max: {Config.MAX_FILE_SIZE_MB}MB")
            if file:
                sz = len(file.getvalue())/(1024*1024)
                if sz > Config.MAX_FILE_SIZE_MB: st.error(f"❌ Too large: {sz:.1f}MB"); return None, None
                else: st.success(f"✓ {file.name} ({sz:.1f}MB)")
        with c2:
            st.markdown("### 🌐 Output Language")
            lang = st.selectbox("Translate to:", list(Config.SUPPORTED_LANGUAGES.keys()), format_func=lambda x: Config.SUPPORTED_LANGUAGES[x], index=0, label_visibility="collapsed")
        return file, lang

def render_results(res):
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    st.success("✅ Analysis Complete")
    c1, c2, c3, c4 = st.columns(4)
    with c1: render_metric("Urgency", render_urgency_badge(res.get('urgency','MEDIUM')), Config.URGENCY_COLORS.get(res.get('urgency','MEDIUM'), "#888"))
    with c2: render_metric("Doc Type", res.get('doc_type','Unknown').title())
    with c3: render_metric("Language", Config.SUPPORTED_LANGUAGES.get(res.get('language','en'), 'Unknown'))
    with c4: render_metric("Completed", datetime.now().strftime('%H:%M'))
    st.markdown('</div>', unsafe_allow_html=True)
    st.divider()
    
    with st.expander("⚠️ Identified Risks", expanded=True):
        risks = res.get('risks', [])
        if risks:
            sev_ord = {'CRITICAL':0,'HIGH':1,'MEDIUM':2,'LOW':3}
            for r in sorted(risks, key=lambda x: sev_ord.get(x.get('severity','MEDIUM'),2)):
                st.markdown(render_risk_item(r), unsafe_allow_html=True)
        else: st.info("ℹ️ No specific risks detected")
        
    with st.expander("🗣️ Plain Language Explanations"):
        for exp in res.get('plain_explanations', []):
            st.markdown(f"**Original**: `{exp.get('original_clause','')[:100]}...`")
            st.markdown(f"**Simplified**: {exp.get('plain_language','')}")
            if exp.get('translation') and exp.get('translation') != exp.get('plain_language'): st.markdown(f"*In your language*: {exp.get('translation')}")
            st.divider()
            
    with st.expander("⚖️ Your Legal Rights (from government sources)"):
        rights = res.get('legal_rights', [])
        if rights:
            st.markdown("*Retrieved from CFPB, HUD, USCIS, etc.:*")
            for i, r in enumerate(rights, 1): st.markdown(f"{i}. <div style='background:rgba(50,50,80,0.3);padding:0.8rem;border-radius:8px;margin:0.3rem 0;border-left:3px solid #c9a227'>{r}</div>", unsafe_allow_html=True)
        else: st.caption("Rights retrieved based on document type")
        
    with st.expander("✅ Your Action Plan", expanded=True):
        for i, a in enumerate(res.get('action_plan', []), 1): st.markdown(render_action_item(i, a), unsafe_allow_html=True)
        st.markdown("""<div class="disclaimer" style="margin-top:1rem">🆓 <strong>Free Legal Help</strong>: Visit <a href="https://www.lawhelp.org" target="_blank">LawHelp.org</a> to find aid near you.</div>""", unsafe_allow_html=True)
        
    letter = res.get('response_letter')
    if letter:
        with st.expander("📝 Draft Response Letter"):
            st.text_area("Template (edit before sending)", value=letter, height=400)
            st.caption("⚠️ Review with a legal professional before sending")
            
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        st.download_button("📄 Download JSON", json.dumps(res, indent=2, default=str), f"lexbridge_{datetime.now():%Y%m%d_%H%M}.json", "application/json", use_container_width=True)
    with c2:
        md = f"# LexBridge Report\n**Type**: {res.get('doc_type')} | **Urgency**: {res.get('urgency')}\n## Risks\n" + "\n".join(f"- **{r.get('severity')}**: {r.get('plain_issue')}" for r in res.get('risks',[])) + "\n## Actions\n" + "\n".join(f"- {a.get('action')}" for a in res.get('action_plan',[]))
        st.download_button("📝 Download Markdown", md, f"lexbridge_summary_{datetime.now():%Y%m%d_%H%M}.md", "text/markdown", use_container_width=True)

def render_footer():
    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown("**🛠 Tech Stack**\nLangGraph • ChatGroq • PyMuPDF • Tesseract • FAISS • Streamlit")
    with c2: st.markdown("**📚 Resources**\n[GitHub](https://github.com) • [CFPB](https://consumerfinance.gov) • [HUD](https://hud.gov)")
    with c3: st.markdown("**🔐 Privacy**\nProcessed in memory • Deleted after analysis • No data stored")
    st.markdown("""<div style="text-align:center;padding:1rem;background:rgba(30,30,50,0.5);border-radius:8px;margin-top:1rem"><small style="color:#a0aec0">⚖️ <strong>LexBridge provides legal information, not legal advice.</strong> Outputs are AI-generated. Laws vary by jurisdiction. Always consult a qualified attorney.</small></div>""", unsafe_allow_html=True)

# ============================================================================
# 🚀 MAIN LOGIC
# ============================================================================
def run_analysis(file_path: str, language: str) -> dict:
    """Execute local LangGraph pipeline"""
    import sys
    import importlib.util
    import types

    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    graph_dir = os.path.join(root_dir, "agent")
    graph_path = os.path.join(graph_dir, "graph.py")
    initial_state = {
        'file_path': file_path, 'raw_text': '', 'doc_type': '', 'language': language or '',
        'risks': [], 'plain_explanations': [], 'legal_rights': [], 'action_plan': [],
        'response_letter': None, 'urgency': 'MEDIUM'
    }

    try:
        sys.path.insert(0, root_dir)
        try:
            from agent.graph import app as agent_graph
        except ImportError:
            if not os.path.exists(graph_path):
                raise
            agent_pkg = types.ModuleType("agent")
            agent_pkg.__path__ = [graph_dir]
            sys.modules["agent"] = agent_pkg
            spec = importlib.util.spec_from_file_location("agent.graph", graph_path)
            if not spec or not spec.loader:
                raise ImportError(f"Unable to load agent.graph from {graph_path}")
            module = importlib.util.module_from_spec(spec)
            sys.modules["agent.graph"] = module
            spec.loader.exec_module(module)
            agent_graph = getattr(module, "app", None)
            if agent_graph is None:
                raise ImportError("`app` not found in agent.graph")

        return agent_graph.invoke(initial_state)
    except ImportError:
        st.error("❌ Missing agent.graph. Ensure you're running from project root with correct structure.")
        st.stop()
    except Exception as e:
        raise e

def main():
    st.set_page_config(page_title=Config.PAGE_TITLE, page_icon=Config.PAGE_ICON, layout="wide", initial_sidebar_state="expanded")
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    
    render_sidebar()
    render_header()
    uploaded_file, language = render_inputs()
    
    st.markdown("### ⚙️ Analysis Pipeline")
    pipeline = PipelineVisualizer()
    pipeline.reset()
    
    c1, c2 = st.columns([3, 1])
    with c1: analyze = st.button("🚀 Analyze Document", type="primary", use_container_width=True, disabled=(uploaded_file is None))
    with c2: st.caption(f"Model: `{Config.get_model()}`")
    
    if analyze and uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name
        
        try:
            pipeline.render(0)
            with st.spinner("🔍 Analyzing your document..."):
                for step in range(1, len(PipelineVisualizer.STEPS)):
                    time.sleep(0.3)
                    pipeline.render(step)
                result = run_analysis(tmp_path, language)
            pipeline.complete()
            render_results(result)
        except Exception as e:
            pipeline.error_at(2)
            st.error(f"❌ Analysis failed: {str(e)}")
            with st.expander("🔧 Debug Details"): st.code(f"{type(e).__name__}: {str(e)}")
        finally:
            if os.path.exists(tmp_path): os.unlink(tmp_path)
            
    render_footer()

if __name__ == "__main__":
    main()\
    
    
    
    
    
    
    
    
    
    
    
    
    
    
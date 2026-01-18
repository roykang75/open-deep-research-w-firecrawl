import streamlit as st
from dotenv import load_dotenv
import sys
import io
import re
from contextlib import redirect_stdout

# Load environment variables
load_dotenv()

from coordinator import run_deep_research

# ANSI escape code pattern for stripping colors
ANSI_ESCAPE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

# Page configuration
st.set_page_config(
    page_title="Deep Research Agent",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Dark Theme CSS
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .stApp {
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Main Header with Gradient */
    .hero-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 2.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    }
    
    .hero-title {
        font-size: 2.8rem;
        font-weight: 700;
        color: white;
        text-align: center;
        margin: 0;
        text-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }
    
    .hero-subtitle {
        font-size: 1.1rem;
        color: rgba(255,255,255,0.9);
        text-align: center;
        margin-top: 0.5rem;
        font-weight: 300;
    }
    
    /* Card Styles */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    
    /* Input Section */
    .input-section {
        background: linear-gradient(145deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid rgba(102, 126, 234, 0.3);
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    }
    
    .section-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #667eea;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Text Area Styling */
    .stTextArea > div > div > textarea {
        background: #ffffff !important;
        border: 2px solid #667eea !important;
        border-radius: 12px !important;
        color: #000000 !important;
        font-size: 1rem !important;
        padding: 1rem !important;
        font-weight: 500 !important;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2) !important;
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.8rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 25px rgba(102, 126, 234, 0.5) !important;
    }
    
    .stButton > button:disabled {
        background: linear-gradient(135deg, #4a4a4a 0%, #3a3a3a 100%) !important;
        box-shadow: none !important;
    }
    
    /* Example Query Buttons */
    .example-btn {
        background: rgba(102, 126, 234, 0.1) !important;
        border: 1px solid rgba(102, 126, 234, 0.3) !important;
        border-radius: 10px !important;
        color: #a0a0ff !important;
        font-size: 0.9rem !important;
        padding: 0.6rem 1rem !important;
        transition: all 0.2s ease !important;
    }
    
    /* Log Container */
    .log-box {
        background: #0d1117;
        border-radius: 12px;
        border: 1px solid #30363d;
        padding: 1.2rem;
        font-family: 'JetBrains Mono', 'Fira Code', monospace;
        font-size: 0.9rem;
        height: 600px;
        overflow-y: auto;
        color: #c9d1d9;
        white-space: pre-wrap;
        line-height: 1.5;
    }
    
    /* Result Container */
    .result-container {
        background: linear-gradient(145deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 16px;
        padding: 2rem;
        border: 1px solid rgba(102, 126, 234, 0.3);
        margin-top: 1.5rem;
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #1a1a2e 0%, #0f0f1a 100%);
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #0f0f1a 100%);
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #e0e0e0;
    }
    
    /* Progress Indicator */
    .progress-indicator {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.8rem 1rem;
        background: rgba(102, 126, 234, 0.1);
        border-radius: 10px;
        border-left: 3px solid #667eea;
    }
    
    /* Tech Stack Pills */
    .tech-pill {
        display: inline-block;
        background: rgba(102, 126, 234, 0.2);
        color: #a0a0ff;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        margin: 0.2rem;
    }
    
    /* Divider */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.3), transparent);
        margin: 1.5rem 0;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #666;
        font-size: 0.85rem;
        padding: 2rem 0;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: rgba(102, 126, 234, 0.1) !important;
        border-radius: 10px !important;
    }
    
    /* Download button */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #00c853 0%, #00a041 100%) !important;
        box-shadow: 0 4px 15px rgba(0, 200, 83, 0.3) !important;
    }
    
    .stDownloadButton > button:hover {
        box-shadow: 0 6px 25px rgba(0, 200, 83, 0.4) !important;
    }
    
    /* Animation */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .loading-pulse {
        animation: pulse 2s infinite;
    }
</style>
""", unsafe_allow_html=True)

# Hero Section
st.markdown("""
<div class="hero-container">
    <h1 class="hero-title">🔬 Deep Research Agent</h1>
    <p class="hero-subtitle">AI 기반 심층 리서치 도구 • SerpAPI & Scraping MCP 기반</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### ⚡ 상태")
    status_placeholder = st.empty()
    status_placeholder.info("🟢 대기 중")
    
    st.markdown("---")
    
    st.markdown("### 📖 사용 방법")
    st.markdown("""
    1️⃣ 연구 주제를 입력하세요  
    2️⃣ **리서치 시작** 클릭  
    3️⃣ AI가 자동으로 분석합니다
    """)
    
    st.markdown("---")
    
    st.markdown("### 🛠️ 기술 스택")
    st.markdown("""
    <div style="margin-top: 0.5rem;">
        <span class="tech-pill">SerpAPI</span>
        <span class="tech-pill">MCP Server</span>
        <span class="tech-pill">OpenAI</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### ℹ️ 정보")
    st.caption("복잡한 주제일수록 시간이 더 걸릴 수 있습니다.")

# Initialize session state for query input if not exists
if 'main_query_input' not in st.session_state:
    st.session_state.main_query_input = ""

# Handle example query selection
if 'selected_query' in st.session_state:
    st.session_state.main_query_input = st.session_state.selected_query
    del st.session_state.selected_query

# Main Content
col1, col2 = st.columns([3, 2])

with col1:
    st.markdown('<p class="section-title">📝 연구 주제</p>', unsafe_allow_html=True)
    user_query = st.text_area(
        "연구하고 싶은 주제를 입력하세요",
        height=150,
        placeholder="예: 2024년 AI 반도체 시장 동향과 주요 기업들의 전략 분석",
        label_visibility="collapsed",
        key="main_query_input"
    )

with col2:
    st.markdown('<p class="section-title">💡 추천 주제</p>', unsafe_allow_html=True)
    example_queries = [
        "🤖 생성형 AI 최신 트렌드",
        "🔋 전기차 배터리 기술 현황",
        "🌱 ESG 경영 글로벌 동향",
        "⚛️ 양자 컴퓨팅의 미래"
    ]
    for query in example_queries:
        if st.button(query, key=query, use_container_width=True):
            # Remove emoji for actual query
            clean_query = query.split(" ", 1)[1] if " " in query else query
            st.session_state.selected_query = clean_query
            st.rerun()

# Research Button
st.markdown("<br>", unsafe_allow_html=True)
col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    research_button = st.button(
        "🚀 리서치 시작",
        type="primary",
        use_container_width=True,
        disabled=not user_query
    )

# Results Section
if research_button and user_query:
    status_placeholder.warning("🔄 리서치 진행 중...")
    
    # Create containers
    log_expander = st.expander("📜 실시간 로그", expanded=True)
    result_container = st.container()
    
    with log_expander:
        log_placeholder = st.empty()
    
    import html
    from streamlit.runtime.scriptrunner_utils.script_run_context import get_script_run_ctx
    
    # Capture stdout for logging with ANSI code stripping and auto-scroll
    class StreamlitLogger(io.StringIO):
        def __init__(self, placeholder):
            super().__init__()
            self.placeholder = placeholder
            self.logs = ""
            self.max_lines = 100
        
        def write(self, text):
            if text:
                # Strip ANSI escape codes
                clean_text = ANSI_ESCAPE.sub('', text)
                self.logs += clean_text
                
                # Keep only the last N lines
                lines = self.logs.splitlines()
                if len(lines) > self.max_lines:
                    self.logs = "\n".join(lines[-self.max_lines:])
                
                # Check if we are in a valid streamlit session before updating
                if get_script_run_ctx() is not None:
                    # Escape HTML to prevent injection
                    # Then also escape markdown special characters to prevent st.markdown from parsing them
                    escaped_logs = html.escape(self.logs)
                    escaped_logs = escaped_logs.replace('#', '&#35;')
                    escaped_logs = escaped_logs.replace('*', '&#42;')
                    escaped_logs = escaped_logs.replace('-', '&#45;')
                    escaped_logs = escaped_logs.replace('_', '&#95;')
                    escaped_logs = escaped_logs.replace('`', '&#96;')
                    
                    # Log box with auto-scroll script
                    # MUST NOT have leading spaces in the template because Streamlit 
                    # interprets indented lines as markdown code blocks.
                    template = f"""
<div id="log-container" class="log-box" style="height: 600px; overflow-y: auto; background: #0d1117; color: #c9d1d9; border-radius: 12px; padding: 1.2rem; border: 1px solid #30363d;">
<pre style="white-space: pre-wrap; font-family: 'JetBrains Mono', 'Fira Code', monospace; font-size: 13px; line-height: 1.5; margin: 0; border: none; background: transparent; color: inherit;">{escaped_logs}</pre>
<div id="log-end-anchor"></div>
</div>
<script>
    (function() {{
        var containers = parent.document.querySelectorAll(".log-box");
        containers.forEach(function(c) {{
            c.scrollTop = c.scrollHeight;
        }});
        var anchor = document.getElementById("log-end-anchor");
        if (anchor) {{
            anchor.scrollIntoView({{behavior: "auto", block: "end"}});
        }}
    }})();
</script>
"""
                    try:
                        self.placeholder.markdown(template, unsafe_allow_html=True)
                    except:
                        pass # Ignore errors during shutdown
            return super().write(text)
    
    try:
        logger = StreamlitLogger(log_placeholder)
        
        with st.spinner("🔍 AI가 심층 리서치를 수행하고 있습니다..."):
            old_stdout = sys.stdout
            sys.stdout = logger
            
            try:
                # Ensure we have a fresh line at start
                sys.stdout.write("Initializing Research Agent...\n")
                result = run_deep_research(user_query)
            finally:
                sys.stdout = old_stdout
        
        status_placeholder.success("✅ 리서치 완료!")
        
        with result_container:
            st.markdown("---")
            st.markdown("### 📊 리서치 결과")
            st.markdown(result)
            
            st.markdown("---")
            col_dl1, col_dl2, col_dl3 = st.columns([1, 2, 1])
            with col_dl2:
                st.download_button(
                    label="📥 마크다운으로 다운로드",
                    data=result,
                    file_name="research_result.md",
                    mime="text/markdown",
                    use_container_width=True
                )
    
    except Exception as e:
        status_placeholder.error("❌ 오류 발생!")
        st.error(f"리서치 중 오류가 발생했습니다: {str(e)}")
        st.exception(e)

# Footer
st.markdown("---")
st.markdown("""
<div class="footer">
    <p>Powered by <strong>SerpAPI</strong> • <strong>Scraping MCP</strong> • <strong>OpenAI-compatible LLMs</strong></p>
</div>
""", unsafe_allow_html=True)

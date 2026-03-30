import json
import os
import re
from pathlib import Path
from typing import Any, Optional

import streamlit as st


def _inject_health_theme() -> None:
    st.markdown(
        """
        <style>
            .stApp {
                background:
                    radial-gradient(1200px 500px at 0% -10%, rgba(61, 168, 116, 0.16), transparent 60%),
                    radial-gradient(900px 420px at 100% -20%, rgba(83, 214, 156, 0.10), transparent 58%),
                    linear-gradient(180deg, #0b1110 0%, #0f1715 55%, #121c19 100%);
                animation: fadeInApp 0.6s ease-out;
            }
            header[data-testid="stHeader"] {
                display: none;
            }
            [data-testid="stAppViewContainer"] > .main {
                padding-top: 0;
            }
            @keyframes fadeInApp {
                from { opacity: 0; transform: translateY(5px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .main .block-container {
                max-width: 900px;
                padding-top: 0.9rem;
            }
            .stApp * {
                caret-color: transparent;
            }
            .hero-title {
                font-size: 3rem;
                font-weight: 850;
                letter-spacing: -0.025em;
                color: #eefbf4;
                margin-bottom: 0.22rem;
                text-shadow: 0 6px 26px rgba(58, 186, 125, 0.18);
            }
            .hero-subtitle {
                color: #b7d9c7;
                font-size: 1.02rem;
                margin-bottom: 1rem;
            }
            .logo-box {
                display: inline-flex;
                align-items: center;
                gap: 0.5rem;
                background: rgba(20, 30, 27, 0.8);
                border: 1px solid rgba(123, 195, 154, 0.28);
                border-radius: 12px;
                padding: 0.45rem 0.7rem;
                color: #d5f4e3;
                box-shadow: 0 12px 32px rgba(0, 0, 0, 0.34);
                backdrop-filter: blur(6px);
            }
            .logo-spin {
                display: inline-block;
                animation: spin 1.1s linear infinite;
            }
            @keyframes spin {
                from { transform: rotate(0deg); }
                to { transform: rotate(360deg); }
            }
            .result-card {
                background: linear-gradient(160deg, rgba(21, 31, 28, 0.9) 0%, rgba(16, 25, 23, 0.88) 100%);
                border: 1px solid rgba(114, 182, 145, 0.24);
                border-radius: 16px;
                padding: 1.05rem;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.34);
                transition: all 0.24s ease;
            }
            .result-card:hover {
                transform: translateY(-2px);
                border-color: rgba(144, 226, 181, 0.36);
            }
            div[data-testid="stForm"] {
                background: linear-gradient(160deg, rgba(21, 31, 28, 0.9) 0%, rgba(16, 25, 23, 0.88) 100%);
                border: 1px solid rgba(114, 182, 145, 0.24);
                border-radius: 16px;
                padding: 1.05rem;
                margin-top: 0.55rem;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.34);
                transition: all 0.24s ease;
                position: relative;
                z-index: 1;
            }
            div[data-testid="stForm"]:hover {
                transform: translateY(-2px);
                border-color: rgba(144, 226, 181, 0.36);
            }
            .stTextArea textarea {
                min-height: 260px !important;
                border: 1px solid #2d423a !important;
                border-radius: 12px !important;
                background: #090d0c !important;
                color: #ffffff !important;
                font-size: 1rem !important;
                line-height: 1.5 !important;
                caret-color: #7df5b6 !important;
                transition: all 0.2s ease !important;
            }
            .stTextArea textarea::placeholder {
                color: #93a79c !important;
            }
            .stTextArea label, .stCheckbox label, .stMarkdown, .stCaption, p, li {
                color: #d3ebde !important;
            }
            .stTextArea textarea:focus {
                border-color: #3ecf8e !important;
                box-shadow: 0 0 0 1px #3ecf8e, 0 0 0 4px rgba(62, 207, 142, 0.15) !important;
            }
            .stFormSubmitButton > button {
                background: linear-gradient(92deg, #1f7e52 0%, #2da867 55%, #37bd74 100%);
                color: white;
                border: none;
                border-radius: 12px;
                font-weight: 700;
                width: 100%;
                transition: all 0.22s ease;
                box-shadow: 0 10px 24px rgba(55, 189, 116, 0.3);
            }
            .stFormSubmitButton > button:hover {
                transform: translateY(-1px);
                filter: brightness(1.03);
            }
            .result-box {
                border-radius: 12px;
                padding: 0.95rem 1rem;
                margin-top: 0.6rem;
                animation: fadeResult 0.35s ease-out;
            }
            @keyframes fadeResult {
                from { opacity: 0; transform: translateY(4px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .result-green {
                background: rgba(40, 128, 86, 0.18);
                border: 1px solid rgba(91, 204, 144, 0.45);
                color: #cffffe;
            }
            .result-yellow {
                background: rgba(180, 134, 23, 0.20);
                border: 1px solid rgba(255, 207, 92, 0.5);
                color: #ffe9b5;
            }
            .result-red {
                background: rgba(154, 42, 42, 0.22);
                border: 1px solid rgba(255, 129, 129, 0.45);
                color: #ffd7d7;
            }
            .badges-footer {
                margin-top: 1.2rem;
                display: flex;
                flex-wrap: wrap;
                gap: 0.35rem;
                opacity: 0.9;
            }
            .badge-small {
                background: rgba(42, 71, 60, 0.65);
                color: #bfe5d2;
                border: 1px solid rgba(134, 204, 167, 0.28);
                border-radius: 999px;
                padding: 0.2rem 0.62rem;
                font-size: 0.72rem;
                font-weight: 600;
            }
            .footer-note {
                margin-top: 0.5rem;
                color: #85b79d;
                font-size: 0.78rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _inject_thinking_ring(active: bool) -> None:
    if not active:
        return
    st.markdown(
        """
        <style>
            @property --snake-angle {
                syntax: "<angle>";
                inherits: false;
                initial-value: 0deg;
            }
            @keyframes snakeRun {
                from { --snake-angle: 0deg; }
                to { --snake-angle: 360deg; }
            }
            /* Supprime l'ancien gros effet sur le formulaire complet */
            div[data-testid="stForm"]::before {
                content: none !important;
            }
            /* Contour lumineux uniquement autour de la zone de texte */
            .stTextArea [data-baseweb="textarea"] {
                position: relative !important;
                border-radius: 12px !important;
                overflow: visible !important;
            }
            .stTextArea [data-baseweb="textarea"]::before {
                content: "";
                position: absolute;
                inset: -1px;
                border-radius: 13px;
                background: conic-gradient(
                    from var(--snake-angle),
                    transparent 0deg 292deg,
                    rgba(116, 240, 182, 0.20) 292deg 300deg,
                    rgba(116, 240, 182, 0.95) 300deg 312deg,
                    rgba(109, 213, 255, 0.95) 312deg 324deg,
                    rgba(143, 168, 255, 0.95) 324deg 336deg,
                    rgba(214, 142, 255, 0.95) 336deg 348deg,
                    rgba(255, 177, 114, 0.92) 348deg 360deg
                );
                padding: 2px;
                -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
                -webkit-mask-composite: xor;
                mask-composite: exclude;
                opacity: 0.98;
                z-index: 1;
                filter: drop-shadow(0 0 6px rgba(125, 245, 182, 0.45))
                        drop-shadow(0 0 7px rgba(141, 184, 255, 0.35));
                animation: snakeRun 1.6s linear infinite;
                pointer-events: none;
            }
            .stTextArea [data-baseweb="textarea"]::after {
                content: none !important;
            }
            .stTextArea textarea {
                position: relative !important;
                z-index: 2 !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _get_api_key() -> Optional[str]:
    try:
        key = st.secrets.get("GEMINI_API_KEY")  # type: ignore[attr-defined]
        if isinstance(key, str) and key.strip():
            return key.strip()
    except Exception:
        pass

    key = os.environ.get("GEMINI_API_KEY", "")
    return key.strip() if key else None


def _build_prompt(text_to_verify: str, high_caution: bool) -> str:
    caution_level = "ELEVEE" if high_caution else "STANDARD"
    return f"""Tu es Agent Sante, specialise en verification d'informations sante et detection de desinformation.

Mission:
- Evaluer la fiabilite d'une affirmation sante.
- Rester prudent et transparent sur l'incertitude.
- Ne jamais poser de diagnostic ni proposer de traitement personnalise.

Regles de securite:
- Si urgence potentielle, recommander de contacter les services d'urgence.
- Refuser tout conseil dangereux.
- Rappeler qu'un professionnel de sante est la reference.

Niveau de prudence: {caution_level}

Reponds UNIQUEMENT en JSON valide avec ces cles exactes:
{{
  "verdict": "Vrai | Plutot vrai | Incertain | Plutot faux | Faux",
  "niveau_confiance": "Faible | Moyen | Eleve",
  "raisons_principales": ["..."],
  "points_a_verifier": ["..."],
  "sources_recommandees": ["OMS", "HAS", "CDC", "Ministere de la Sante"],
  "avertissement_sante": "..."
}}

Information a verifier:
\"\"\"{text_to_verify}\"\"\"
"""


def _extract_json(text: str) -> dict[str, Any]:
    cleaned = (text or "").strip()
    if not cleaned:
        raise ValueError("Reponse vide du modele.")
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
        if not match:
            raise ValueError("JSON invalide.")
        return json.loads(match.group(0))


def _as_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(v) for v in value]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def verify_health_information(text_to_verify: str, high_caution: bool = True) -> dict[str, Any]:
    api_key = _get_api_key()
    if not api_key:
        return {"error": "Cle API manquante. Definis GEMINI_API_KEY dans st.secrets ou variable d'environnement."}

    try:
        import google.generativeai as genai
        from google.api_core.exceptions import ResourceExhausted
    except ImportError:
        return {"error": "Dependance manquante: installe google-generativeai."}

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name="gemini-2.5-flash")
    prompt = _build_prompt(text_to_verify, high_caution=high_caution)

    try:
        response = model.generate_content(prompt)
    except ResourceExhausted:
        return {
            "throttled": True,
            "warning": (
                "VeriDoc est victime de son succes ! Beaucoup de verifications sont en cours. "
                "Merci de patienter environ une minute avant de reessayer."
            ),
        }
    raw_text = getattr(response, "text", "") or str(response)
    try:
        data = _extract_json(raw_text)
    except Exception:
        return {"error": "Reponse non structuree du modele.", "raw": raw_text}

    return {
        "verdict": str(data.get("verdict", "Incertain")),
        "niveau_confiance": str(data.get("niveau_confiance", "Faible")),
        "raisons_principales": _as_list(data.get("raisons_principales", [])),
        "points_a_verifier": _as_list(data.get("points_a_verifier", [])),
        "sources_recommandees": _as_list(data.get("sources_recommandees", [])),
        "avertissement_sante": str(data.get("avertissement_sante", "Consultez un professionnel de sante.")),
    }


def _result_theme(verdict: str) -> str:
    v = verdict.lower()
    if "vrai" in v and "plutot" not in v:
        return "result-green"
    if "faux" in v:
        return "result-red"
    return "result-yellow"


def _render_result(result: dict[str, Any]) -> None:
    if result.get("throttled"):
        st.warning(
            result.get(
                "warning",
                "VeriDoc est victime de son succes ! Beaucoup de verifications sont en cours. "
                "Merci de patienter environ une minute avant de reessayer.",
            )
        )
        return
    if "error" in result:
        st.error(result["error"])
        if "raw" in result:
            st.write(result["raw"])
        return

    verdict = result.get("verdict", "Incertain")
    box_class = _result_theme(str(verdict))
    raisons = result.get("raisons_principales", [])
    points = result.get("points_a_verifier", [])
    sources = result.get("sources_recommandees", [])
    avertissement = result.get("avertissement_sante", "")
    confiance = result.get("niveau_confiance", "Faible")

    st.markdown(
        f"""
        <div class="result-card">
            <div class="result-box {box_class}">
                <strong>Verdict:</strong> {verdict}<br/>
                <strong>Niveau de confiance:</strong> {confiance}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("**Raisons principales**")
    for item in raisons:
        st.write(f"- {item}")
    st.markdown("**Points a verifier**")
    for item in points:
        st.write(f"- {item}")
    st.markdown("**Sources recommandees**")
    for item in sources:
        st.write(f"- {item}")
    st.markdown("**Avertissement sante**")
    st.write(avertissement)


def _render_footer_badges() -> None:
    st.markdown(
        """
        <div class="badges-footer">
            <span class="badge-small">Agent Sante IA</span>
            <span class="badge-small">Mode prudence</span>
            <span class="badge-small">Sortie structuree</span>
            <span class="badge-small">Cle API securisee</span>
        </div>
        <div class="footer-note">
            Badges informatifs non officiels.
        </div>
        """,
        unsafe_allow_html=True,
    )


def _get_logo_paths() -> tuple[Optional[Path], Optional[Path]]:
    static_dir = Path(__file__).resolve().parent / "static"
    square_logo = static_dir / "logo veridoc 1.png"
    horizontal_logo = static_dir / "logo veridoc 2.png"

    return (
        square_logo if square_logo.exists() else None,
        horizontal_logo if horizontal_logo.exists() else None,
    )


def main() -> None:
    st.set_page_config(page_title="Agent Sante - Verif Info", page_icon="🩺")
    _inject_health_theme()
    if "is_thinking" not in st.session_state:
        st.session_state.is_thinking = False
    if "pending_query" not in st.session_state:
        st.session_state.pending_query = ""
    if "pending_caution" not in st.session_state:
        st.session_state.pending_caution = True
    if "last_result" not in st.session_state:
        st.session_state.last_result = None

    _inject_thinking_ring(bool(st.session_state.is_thinking))
    square_logo, horizontal_logo = _get_logo_paths()

    if horizontal_logo is not None:
        st.image(str(horizontal_logo), width=165)

    title_col, seal_col = st.columns([6, 1.2])
    with title_col:
        st.markdown('<div class="hero-title">Agent Sante IA</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="hero-subtitle">Verifie rapidement une information sante avec un rendu simple, clair et prudent.</div>',
            unsafe_allow_html=True,
        )
    with seal_col:
        if square_logo is not None:
            st.image(str(square_logo), width=76)

    status_placeholder = st.empty()
    if st.session_state.is_thinking:
        status_placeholder.markdown(
            '<div class="logo-box"><span class="logo-spin">🧠</span> <strong>Analyse en cours...</strong></div>',
            unsafe_allow_html=True,
        )
    else:
        status_placeholder.markdown(
            '<div class="logo-box">🩺 <strong>Pret a analyser</strong></div>',
            unsafe_allow_html=True,
        )

    with st.form("verify_form", clear_on_submit=False, border=False):
        text_to_verify = st.text_area(
            "Information a verifier",
            placeholder="Ex: Ce remede naturel guerit toutes les maladies en 48h.",
            height=280,
        )
        high_caution = st.checkbox(
            "Mode prudence elevee (recommande)",
            value=True,
            help="Renforce les avertissements en cas d'ambiguite.",
        )
        submitted = st.form_submit_button("Verifier l'information")

    if submitted:
        cleaned = (text_to_verify or "").strip()
        if not cleaned:
            st.warning("Veuillez saisir une information a verifier.")
            _render_footer_badges()
            return
        st.session_state.pending_query = cleaned
        st.session_state.pending_caution = high_caution
        st.session_state.is_thinking = True
        st.rerun()

    if st.session_state.is_thinking and st.session_state.pending_query:
        with st.spinner("L'IA verifie l'information..."):
            result = verify_health_information(
                st.session_state.pending_query,
                high_caution=bool(st.session_state.pending_caution),
            )
        st.session_state.last_result = result
        st.session_state.pending_query = ""
        st.session_state.is_thinking = False
        st.rerun()

    if st.session_state.last_result is not None:
        _render_result(st.session_state.last_result)

    _render_footer_badges()


if __name__ == "__main__":
    main()


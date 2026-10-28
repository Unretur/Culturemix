import os
import sys
from pathlib import Path

import streamlit as st

# Make sibling modules importable when run as `streamlit run src/app.py`
sys.path.insert(0, str(Path(__file__).parent))

from planner import LineItem, check_budget  # noqa: E402
from qloo_client import QlooError, live_search, mock_search  # noqa: E402

st.set_page_config(page_title="CultureMix", layout="wide")
st.title("CultureMix")
st.caption("An agent that designs culturally intelligent events.")


def load_secret_into_env() -> None:
    """On Streamlit Cloud, secrets live in st.secrets. Copy into env once."""
    try:
        if "QLOO_API_KEY" in st.secrets and not os.environ.get("QLOO_API_KEY"):
            os.environ["QLOO_API_KEY"] = st.secrets["QLOO_API_KEY"]
    except Exception:
        # No secrets file locally. Fine, the .env path or MOCK mode applies.
        pass


load_secret_into_env()
live_key_present = bool(os.environ.get("QLOO_API_KEY", "").strip())

with st.form("brief"):
    city = st.text_input("City", "Mumbai")
    budget = st.number_input("Budget (INR)", min_value=0, value=1_000_000, step=50_000)
    interest = st.text_input("Primary interest", "independent music")
    submitted = st.form_submit_button("Build event plan")

if submitted:
    st.subheader("Cultural entities")
    try:
        if live_key_present:
            data = live_search(interest, "urn:entity:artist")
            st.success("Source: LIVE Qloo API")
        else:
            data = mock_search(interest, "artist")
            st.warning("Source: MOCK, not Qloo. No API key is configured.")
        st.json(data)
    except QlooError as exc:
        st.error(str(exc))

    st.subheader("Budget check")
    # Placeholder cost. Real estimates come from the planner in the next milestone.
    items = [LineItem("Venue (placeholder estimate)", 0.0, "estimate")]
    check = check_budget(items, budget)
    st.write(
        {
            "total (INR)": check.total,
            "budget (INR)": check.budget,
            "within budget": check.within_budget,
            "remaining (INR)": check.remaining,
        }
    )

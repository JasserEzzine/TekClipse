"""Cloud entrypoint: initialize an actual nominal preview, then serve the full UI."""

import os
from pathlib import Path
import runpy

import streamlit as st

os.environ["TEKCLIPSE_CLOUD"] = "1"
st.set_page_config(
    page_title="TekClipse | Mission Control", page_icon="◉", layout="wide"
)


@st.cache_resource(show_spinner=False)
def initialize_cloud_demo():
    from tekclipse.dashboard.data_service import (
        dataset_token,
        detect,
        load_nominal_preview,
        save_nominal_preview,
    )

    # Build the largest offered range once, before concurrent visitors arrive.
    # Switching between 1 and 7 days then reads the same completed dataset.
    token = dataset_token(168)
    if load_nominal_preview(24, token) is None:
        result = detect(24, token, "E1")
        save_nominal_preview(24, token, result)
    return True


with st.spinner("Preparing the simulated mission and its actual detector results…"):
    initialize_cloud_demo()

runpy.run_path(
    str(Path(__file__).parent / "tekclipse/dashboard/app.py"), run_name="__main__"
)

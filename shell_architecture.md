# Streamlit Multi-Section Dashboard Shell Architecture Guide

## 1. Streamlit Execution Model & State Mechanics

Streamlit operates on a **top-to-bottom script execution model**:
- Every time a user interacts with a widget (such as selecting a sidebar radio button, adjusting a slider, or entering text), Streamlit reruns the entire Python script from line 1 to the end.
- State is preserved across reruns through widget state keys and `@st.cache_data` decorators.
- In `app.py`, the `st.sidebar.radio` widget evaluates `page` variable on each rerun, executing only the corresponding `if/elif` branch and rendering only the active section into the DOM.

---

## 2. Layout Component Design Rules

### `st.columns` (Side-by-Side Parallel Content)
- **When to Use:** Presenting metrics, cards, or charts that require immediate side-by-side comparison.
- **Application in `app.py`:**
  - `st.columns(5)`: Top executive KPI header row (`Revenue`, `Users`, `AOV`, `Churn`, `NPS`).
  - `st.columns(2)`: Dual trend charts (`Monthly Revenue` alongside `Revenue by Product`).
  - `st.columns([2, 1])`: Asymmetric search input and slider filter layout.

### `st.expander` (Collapsible Supplementary Content)
- **When to Use:** Optional background information, mathematical formulas, data dictionaries, or methodology notes that stakeholders may reference on demand but should not clutter the primary view.
- **Application in `app.py`:**
  - `st.expander("About These Metrics")`: Explains KPI definitions without consuming vertical space.
  - `st.expander("Historical Benchmark Notes")`: Provides seasonal context.
  - `st.expander("Data Dictionary")`: Documents raw column schemas.

---

## 3. Visual & Information Hierarchy Standards

To ensure maximum scannability and executive clarity:

| Hierarchy Level | Streamlit Method | Usage Rule in `app.py` |
| :--- | :--- | :--- |
| **Level 1 (Page Title)** | `st.title()` | Used **once per page section** at the top of the main container. |
| **Level 2 (Major Section)** | `st.header()` | Demarcates major structural blocks (e.g. `Executive Summary`, `Revenue Trends`). |
| **Level 3 (Subsection)** | `st.subheader()` | Labels specific charts, tables, or sub-components. |
| **Visual Separator** | `st.divider()` | Places clean horizontal rules between major logical sections. |

---

## 4. Above-the-Fold Optimization

Executive decision-makers judge dashboard utility within 3 seconds of page load. In `app.py`:
- The 5 top-row KPI cards (`st.columns(5)`) are positioned **immediately below the page title**.
- Zero large images, instructions, or blank spaces precede the metrics.
- All key business health signals are visible on first load without scrolling.

---

## 5. Scaling to Multi-Page Applications (`pages/` Directory Convention)

As the application grows, single-file conditional structures (`if page == ...`) can be modularized using Streamlit's native `pages/` directory architecture:

```text
FactoryPluse/
├── app.py                     # Main entrypoint / landing page
├── requirements.txt           # Environment dependencies
├── pages/
│   ├── 1_📊_Overview.py       # Overview section
│   ├── 2_📈_Trends.py         # Trend analysis section
│   └── 3_🔍_Data_Explorer.py  # Data explorer & export section
```

### Advantages of the `pages/` Convention:
1. **Automatic Navigation:** Streamlit automatically detects scripts in `pages/` and renders sidebar navigation buttons.
2. **Code Separation:** Each section lives in its own dedicated file, simplifying maintenance and git code reviews.
3. **Independent Caching:** Module-level imports and session state can be scoped per page.

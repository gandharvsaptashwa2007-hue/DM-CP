# Guided tours

Select **Take a tour** at the bottom right to explore the current screen.
Home covers the brand, page picker, appearance, visit navigation, and seven cards.
Module walkthroughs cover visible inputs, actions, theory exercises and results.
Calculate first and replay to include tables, playback and history. Hidden
controls inside closed expanders are not included until visible.

The overlay highlights a feature and blurs the surrounding page. Next, Back,
Skip and Finish control the tour. Escape closes it; Tab stays in the dialog.
The tour scrolls directly to each feature without animated motion. It does not
change inputs, execute calculations, or add results to history.

Steps live in `ui/tour.py`; positioning and accessibility behavior live in
`ui/tour.js`. This trusted local Streamlit component uses parent-document DOM
access, tested against the pinned Streamlit 1.50.0. Recheck selectors, replay,
keyboard controls and responsive placement when upgrading Streamlit.

# 7th Grade ELA Curriculum

Curriculum materials for 7th grade English Language Arts in McIntosh County School System, built on Georgia's K-12 ELA Standards (2023) and the Georgia Milestones Grade 7 ELA Achievement Level Descriptors.

## Contents

- `7th_Grade_ELA_Curriculum_Map.md`: the year-long, writing-centered curriculum map. Source of truth. Edit this file.
- `7th_Grade_ELA_Curriculum_Map.html`: the map as a tile page. One tile per unit slides open a panel with that unit's standards, success criteria, assessments, texts, and weekly arc. Reference tiles hold the Milestones target, routines, and coverage tables.
- `7th_Grade_ELA_Curriculum_Map_Print.html`: the full map in reading order, for printing.
- `7th_Grade_ELA_Curriculum_Map.pdf`: the print edition exported to PDF.
- `tools/build_map_html.py`: rebuilds both HTML pages from the markdown.

## Rebuilding after editing the map

1. Install the converter once: `pip install markdown`
2. From the repository root run: `python3 tools/build_map_html.py`
3. Commit the `.md` and both `.html` files. Re-export the PDF from the print edition if it matters for that change.

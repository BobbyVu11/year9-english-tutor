Year 9 English Extension Tutor
================================
Victorian Curriculum · Targeting Year 10 Level

HOW TO RUN
----------
1. Open the folder  Year9_English_Tutor
2. Double-click     run.bat
3. Your browser opens automatically at http://localhost:5050
4. To quit: close the black command window (or press Ctrl+C in it)

WHAT'S INSIDE
-------------
  app.py       — Python server (no internet or pip installs needed)
  index.html   — The tutor app
  run.bat      — Windows double-click launcher
  README.txt   — This file

SECTIONS
--------
  Writing      — Rotating prompts (persuasive, analytical, creative, expository)
                 + instant feedback, model paragraphs, TEEL checklist
  Reading      — 4 unseen passages with graded comprehension questions
  Vocabulary   — Flashcards (academic, literary, analytical) + gap quiz
  Metalanguage — Identify-the-technique quiz + full reference table
  Progress     — Tracks activity and saves your most recent writing

REQUIREMENTS
------------
  Python 3.7 or higher (comes pre-installed on most modern Windows PCs)
  Any web browser (Chrome, Edge, Firefox)
  No internet connection needed once set up

TROUBLESHOOTING
---------------
  "python is not recognised..."
    → Python may not be on the system PATH.
    → Open the app folder, type  python app.py  in the address bar
      replacing it with  cmd  first to open a terminal, then run:
        python app.py
    → Or try:  py app.py

  Browser doesn't open automatically
    → Open your browser manually and go to:  http://localhost:5050

  Port already in use
    → Edit app.py, change PORT = 5050 to any other number (e.g. 5051)

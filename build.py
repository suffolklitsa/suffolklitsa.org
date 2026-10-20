import os, sys, shutil, importlib, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "src"))
sys.path.insert(0, os.path.dirname(HERE))
IDENTITY_SRC = os.path.join(HERE, "vendor", "identity", "src")  # copied from the LITSA identity project
sys.path.insert(0, IDENTITY_SRC)
OUT = os.path.join(HERE, "build")

PAGES = [("page_index",    "index.html"),
         ("page_resources", "resources/index.html"),
         ("page_curriculum", "curriculum/index.html"),
         ("page_events",   "events/index.html"),
         ("page_courses",  "curriculum/courses/index.html"),
         ("page_field",    "field/index.html"),
         ("page_suffolk",  "suffolk/index.html"),
         ("page_build",    "build/index.html"),
         ("page_watch",    "watch/index.html"),
         ("page_compete",  "compete/index.html"),
         ("page_history",  "history/index.html"),
         ("page_join",     "join/index.html"),
         ("page_partners", "partners/index.html"),
         ("page_contact",  "contact/index.html"),
         ("page_calendar", "calendar/index.html"),
         ("page_me",       "me/index.html"),
         ("page_404",      "404.html")]

def main():
    if os.path.exists(OUT): shutil.rmtree(OUT)
    os.makedirs(OUT)
    shutil.copytree(os.path.join(HERE, "static"), OUT, dirs_exist_ok=True)
    import assets
    today = datetime.date.today().isoformat()
    assets.build_all(OUT, today)
    for mod, dest in PAGES:
        m = importlib.import_module(mod)
        p = os.path.join(OUT, dest)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w").write(m.render())
        print("  %-28s %6d bytes" % (dest, os.path.getsize(p)))

    # One page per subject and per concentration, driven by the content files.
    import data as D
    import page_subject, page_concentration
    total = 0
    for s in D.subjects():
        dest = os.path.join(OUT, "resources", s["slug"], "index.html")
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        open(dest, "w").write(page_subject.render(s["slug"]))
        total += os.path.getsize(dest)
    print("  %-28s %6d bytes  (%d pages)"
          % ("resources/<subject>/", total, len(D.subjects())))
    total = 0
    for c in D.concentrations():
        dest = os.path.join(OUT, "curriculum", c["slug"], "index.html")
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        open(dest, "w").write(page_concentration.render(c["slug"]))
        total += os.path.getsize(dest)
    print("  %-28s %6d bytes  (%d pages)"
          % ("curriculum/<conc>/", total, len(D.concentrations())))

if __name__ == "__main__":
    main()

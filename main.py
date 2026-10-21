with open('/mnt/agents/output/pyeditor/libraries.json', 'w', encoding='utf-8') as f:
    json.dump(libs, f, ensure_ascii=False, indent=0)

main_py = '''# -*- coding: utf-8 -*-
"""
محرر بايثون الاحترافي للهاتف
مميزات مستوحاة من أشهر تطبيقات الهاتف: Pydroid 3, DroidEdit, ACode, Termux
"""
import os, sys, json, threading, subprocess, keyword, builtins, urllib.request

from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.codeinput import CodeInput
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.recycleview import RecycleView
from kivy.uix.screenmanager import Screen, ScreenManager
from pygments.lexers import PythonLexer

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
LIBS_PATH = os.path.join(BASE_DIR, "libraries.json")
WORK_DIR  = os.path.join(BASE_DIR, "projects")
os.makedirs(WORK_DIR, exist_ok=True)

PYI_URL = "https://hugovk.github.io/top-pypi-packages/top-pypi-packages-30-days.min.json"


# ---------------------------------------------------------------- الطرفية
class TerminalPanel(BoxLayout):
    """طرفية حقيقية: تدعم أي أمر shell + pip مباشرة"""
    def __init__(self, **kw):
        super().__init__(orientation="vertical", **kw)
        self.out = TextInput(readonly=True, multiline=True,
                             background_color=(0.04, 0.04, 0.07, 1),
                             foreground_color=(0.75, 1.0, 0.75, 1),
                             font_size="13sp")
        self.inp = TextInput(multiline=False, size_hint_y=None, height=dp(46),
                             hint_text="اكتب أمراً... مثال: pip install numpy",
                             background_color=(0.1, 0.1, 0.12, 1),
                             foreground_color=(1, 1, 1, 1))
        self.inp.bind(on_text_validate=self._submit)
        self.add_widget(self.out)
        self.add_widget(self.inp)

    def log(self, s):
        self.out.text += s
        self.out.scroll_y = 0

    def _submit(self, instance):
        cmd = instance.text.strip()
        instance.text = ""
        if cmd:
            Clock.schedule_once(lambda dt: self.log("\\n$ " + cmd + "\\n"))
            threading.Thread(target=self._exec, args=(cmd,), daemon=True).start()

    def run_command(self, cmd):
        self.inp.text = cmd
        self._submit(self.inp)

    def _exec(self, cmd):
        try:
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT, cwd=WORK_DIR,
                                 env=dict(os.environ))
            for line in iter(p.stdout.readline, b""):
                s = line.decode("utf-8", "replace")
                Clock.schedule_once(lambda dt, s=s: self.log(s))
            p.wait()
        except Exception as e:
            Clock.schedule_once(lambda dt, e=e: self.log(str(e) + "\\n"))


# ---------------------------------------------------------------- المحرر
class Editor(CodeInput):
    def __init__(self, app, **kw):
        super().__init__(lexer=PythonLexer(),
                         font_size="15sp",
                         auto_indentation=True,
                         **kw)
        self.app_ref = app
        self.bind(text=self._on_text)

    def _on_text(self, *a):
        Clock.schedule_once(lambda dt: self.app_ref.update_suggestions(), 0)

    def current_prefix(self):
        before = self.text[:self.cursor_index()]
        w = ""
        for ch in reversed(before):
            if ch.isalnum() or ch == "_":
                w = ch + w
            else:
                break
        return w


# ---------------------------------------------------------------- شاشة المكتبات
class LibsScreen(Screen):
    def __init__(self, app, **kw):
        super().__init__(**kw)
        self.app = app
        root = BoxLayout(orientation="vertical")

        top = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(4))
        self.search = TextInput(hint_text="ابحث عن مكتبة... (أكثر من 1000 مكتبة)",
                                multiline=False)
        self.search.bind(text=lambda i, v: self.populate(v))
        btn_sync = Button(text="مزامنة", size_hint_x=None, width=dp(85))
        btn_sync.bind(on_release=lambda i: self.sync_online())
        btn_back = Button(text="رجوع", size_hint_x=None, width=dp(85))
        btn_back.bind(on_release=lambda i: setattr(self.app.sm, "current", "editor"))
        top.add_widget(self.search)
        top.add_widget(btn_sync)
        top.add_widget(btn_back)

        self.rv = RecycleView()
        self.rv.viewclass = "Button"
        self.rv.data = []

        root.add_widget(top)
        root.add_widget(self.rv)
        self.add_widget(root)

    def load(self):
        try:
            with open(LIBS_PATH, encoding="utf-8") as f:
                self.all_libs = json.load(f)
        except Exception:
            self.all_libs = []
            self.sync_online()
        self.populate("")

    def populate(self, q=""):
        q = q.lower().strip()
        items = [l for l in self.all_libs if q in l.lower()][:500]
        self.rv.data = [{"text": l,
                         "on_release": (lambda n: lambda i: self.install(n))(l)}
                        for l in items]
        if not items:
            self.rv.data = [{"text": "لا نتائج — جرّب المزامنة",
                             "on_release": lambda i: self.sync_online()}]

    def install(self, name):
        self.app.sm.current = "editor"
        self.app.term_dock.height = dp(240)
        Clock.schedule_once(lambda dt: self.app.term.run_command("pip install " + name), 0.3)

    def sync_online(self, *a):
        self.app.term.log("\\n[مزامنة قائمة المكتبات من الإنترنت...]\\n")
        threading.Thread(target=self._sync, daemon=True).start()

    def _sync(self):
        try:
            with urllib.request.urlopen(PYI_URL, timeout=60) as r:
                data = json.load(r)
            names = sorted({row["project"] for row in data["rows"]})
            with open(LIBS_PATH, "w", encoding="utf-8") as f:
                json.dump(names, f, ensure_ascii=False)
            Clock.schedule_once(lambda dt: self.load())
            Clock.schedule_once(lambda dt: self.app.term.log(
                "[تمت المزامنة: %d مكتبة]\\n" % len(names)))
        except Exception as e:
            Clock.schedule_once(lambda dt: self.app.term.log("فشلت المزامنة: %s\\n" % e))


# ---------------------------------------------------------------- التطبيق
class PyEditorApp(App):
    def build(self):
        self.title = "محرر بايثون AI"
        self.sm = ScreenManager()
        self.sm.add_widget(Screen(name="editor"))
        self.libs = LibsScreen(self, name="libs")
        self.sm.add_widget(self.libs)

        root = BoxLayout(orientation="vertical")

        # شريط علوي
        top = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(2))
        for text, cb in [("جديد", self.new_file), ("فتح", self.open_dialog),
                         ("حفظ", self.save_dialog), ("تشغيل ▶", self.run_code),
                         ("📦 مكتبات", self.show_libs),
                         ("⌨ الطرفية", self.toggle_terminal)]:
            b = Button(text=text)
            b.bind(on_release=cb)
            top.add_widget(b)
        root.add_widget(top)

        # المحرر
        self.editor = Editor(self, size_hint_y=1)
        self.editor.text = DEFAULT_CODE
        root.add_widget(self.editor)

        # شريط التكملة الذكية
        self.sugg_dock = BoxLayout(size_hint_y=None, height=0, spacing=dp(4))
        self.sugg_scroll = ScrollView(do_scroll_y=False)
        self.sugg_box = BoxLayout(size_hint_x=None, spacing=dp(4),
                                  padding=[dp(4), 0])
        self.sugg_box.bind(minimum_width=self.sugg_box.setter("width"))
        self.sugg_scroll.add_widget(self.sugg_box)
        self.sugg_dock.add_widget(self.sugg_scroll)
        root.add_widget(self.sugg_dock)

        # الشريط السفلي (الأقواس والرموز)
        bar = ScrollView(do_scroll_y=False, size_hint_y=None, height=dp(46))
        box = BoxLayout(size_hint_x=None, spacing=dp(3), padding=[dp(4), 2])
        box.bind(minimum_width=box.setter("width"))
        for label, text, shift in [
            ("( )", "()", -1), ("[ ]", "[]", -1), ("{ }", "{}", -1),
            ('" "', '\"\"', -1), ("' '", "''", -1), (":", ":", 0),
            (";", ";", 0), (",", ",", 0), ("=", "=", 0), ("==", "==", 0),
            ("+", "+", 0), ("-", "-", 0), ("*", "*", 0), ("/", "/", 0),
            ("_", "_", 0), ("#", "#", 0), ("<", "<", 0), (">", ">", 0),
            ("!", "!", 0), ("&", "&", 0), ("|", "|", 0), ("%", "%", 0),
            ("def", "def ():", -3), ("if", "if :", -1), ("for", "for :", -1),
            ("Tab", "    ", 0), ("⇤", "undo", 0), ("⇥", "redo", 0),
            ("◀", "left", 0), ("▶", "right", 0), ("⌫", "back", 0),
        ]:
            b = Button(text=label, size_hint_x=None, width=dp(52), font_size="13sp")
            b.bind(on_release=lambda i, t=text, s=shift: self.insert_at_cursor(t, s))
            box.add_widget(b)
        bar.add_widget(box)
        root.add_widget(bar)

        # الطرفية
        self.term = TerminalPanel()
        self.term_dock = BoxLayout(size_hint_y=None, height=0, orientation="vertical")
        self.term_dock.add_widget(self.term)
        root.add_widget(self.term_dock)

        self.sm.get_screen("editor").add_widget(root)
        Clock.schedule_once(lambda dt: self.libs.load())
        Clock.schedule_once(lambda dt: self.term.log(
            "مرحباً! هذه طرفية حقيقية تدعم pip.\\n"
            "مثال: pip install numpy\\n"))
        return self.sm

    # ---------- أدوات ----------
    def insert_at_cursor(self, text, shift=0):
        e = self.editor
        if text == "undo":
            e.do_undo(); return
        if text == "redo":
            e.do_redo(); return
        if text == "left":
            idx = max(0, e.cursor_index() - 1)
            e.cursor = e.get_cursor_from_index(idx); return
        if text == "right":
            idx = min(len(e.text), e.cursor_index() + 1)
            e.cursor = e.get_cursor_from_index(idx); return
        if text == "back":
            if e.selection_text:
                e.delete_selection()
            else:
                idx = e.cursor_index()
                if idx > 0:
                    e.text = e.text[:idx-1] + e.text[idx:]
                    e.cursor = e.get_cursor_from_index(idx-1)
            return
        e.insert_text(text)
        if shift:
            e.cursor = e.get_cursor_from_index(e.cursor_index() + shift)

    def update_suggestions(self):
        pref = self.editor.current_prefix()
        self.sugg_box.clear_widgets()
        if len(pref) < 2:
            self.sugg_dock.height = 0
            return
        words = set(keyword.kwlist) | set(dir(builtins)) | set(self.editor.text.split())
        matches = sorted(w for w in words if w.startswith(pref) and w != pref)[:8]
        if not matches:
            self.sugg_dock.height = 0
            return
        self.sugg_dock.height = dp(40)
        for m in matches:
            b = Button(text=m, size_hint_x=None,
                       width=dp(len(m) * 11 + 26), font_size="13sp")
            b.bind(on_release=lambda i, w=m: self.apply_suggestion(w))
            self.sugg_box.add_widget(b)

    def apply_suggestion(self, word):
        e = self.editor
        idx = e.cursor_index()
        pref = e.current_prefix()
        start = idx - len(pref)
        e.text = e.text[:start] + word + e.text[idx:]
        e.cursor = e.get_cursor_from_index(start + len(word))
        self.sugg_dock.height = 0

    # ---------- ملفات ----------
    def ask_filename(self, title, cb):
        lay = BoxLayout(orientation="vertical", spacing=dp(6))
        ti = TextInput(multiline=False, hint_text="اسم الملف، مثال: main.py",
                       size_hint_y=None, height=dp(46))
        row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(6))
        ok, cancel = Button(text="تأكيد"), Button(text="إلغاء")
        pop = Popup(title=title, content=lay, size_hint=(0.92, 0.32))
        ok.bind(on_release=lambda i: (cb(ti.text.strip()), pop.dismiss()))
        cancel.bind(on_release=pop.dismiss)
        lay.add_widget(ti); row.add_widget(ok); row.add_widget(cancel); lay.add_widget(row)
        pop.open()

    def current_path(self):
        return getattr(self, "_path", os.path.join(WORK_DIR, "main.py"))

    def new_file(self, *a):
        self.editor.text = ""
        self._path = os.path.join(WORK_DIR, "untitled.py")

    def open_dialog(self, *a):
        self.ask_filename("فتح ملف (من مجلد projects)", self._do_open)

    def _do_open(self, name):
        if not name:
            return
        path = name if os.path.isabs(name) else os.path.join(WORK_DIR, name)
        try:
            with open(path, encoding="utf-8") as f:
                self.editor.text = f.read()
            self._path = path
        except Exception as e:
            self.term.log("خطأ في الفتح: %s\\n" % e)

    def save_dialog(self, *a):
        self.ask_filename("حفظ باسم", self._do_save)

    def _do_save(self, name):
        if not name:
            return
        path = name if os.path.isabs(name) else os.path.join(WORK_DIR, name)
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.editor.text)
            self._path = path
            self.term.log("[تم الحفظ: %s]\\n" % path)
        except Exception as e:
            self.term.log("خطأ في الحفظ: %s\\n" % e)

    # ---------- تشغيل / تنقل ----------
    def run_code(self, *a):
        path = self.current_path()
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.editor.text)
        except Exception as e:
            self.term.log("خطأ: %s\\n" % e)
            return
        self.term_dock.height = dp(240)
        self.term.run_command('"%s" "%s"' % (sys.executable, path))

    def show_libs(self, *a):
        self.sm.current = "libs"

    def toggle_terminal(self, *a):
        self.term_dock.height = 0 if self.term_dock.height else dp(240)


DEFAULT_CODE = \'\'\'# مرحباً بك في محرر بايثون AI!
# اكتب كودك هنا ثم اضغط "تشغيل ▶"

import math

def circle_area(r):
    return math.pi * r ** 2

for i in range(1, 4):
    print(f"مساحة دائرة نصف قطرها {i} = {circle_area(i):.2f}")
\'\'\'


if __name__ == "__main__":
    PyEditorApp().run()
'''

with open('/mnt/agents/output/pyeditor/main.py', 'w', encoding='utf-8') as f:
    f.write(main_py)

print("main.py:", len(main_py), "chars")

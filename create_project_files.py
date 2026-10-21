spec = '''[app]

# (str) Title of your application
title = محرر بايثون AI

# (str) Package name
package.name = pyeditor

# (str) Package domain (needed for android/ios packaging)
package.domain = org.example.pyeditor

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,json

# (list) List of inclusions using pattern matching
#source.include_patterns = assets/*,images/*.png

# (str) Application versioning
version = 0.1

# (list) Application requirements
requirements = python3,kivy,pygments

# (str) Supported orientation
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# (int) Android API to use
android.api = 33

# (int) Minimum API required
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Use --private data storage for the app
android.private_storage = True

# (str) The Android arch to build for
android.archs = arm64-v8a, armeabi-v7a

# (int) overrides automatic versionCode computation
# android.numeric_version = 1

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
'''

readme = '''# محرر بايثون AI — دليل البناء والتثبيت

تطبيق محرر أكواد Python للهاتف، مستوحى من أشهر تطبيقات تحرير الأكواد على الهاتف
(Pydroid 3، DroidEdit، ACode، Termux).

## المميزات

| الميزة | الوصف |
|---|---|
| محرر أكواد | تلوين تلقائي لصياغة Python (Pygments) |
| طرفية حقيقية | تدعم أوامر shell و pip مباشرة |
| +1000 مكتبة | قائمة مدمجة + مزامنة واحدة لأكثر من 8000 مكتبة من PyPI |
| مكتبات AI | TensorFlow، PyTorch، Transformers، LangChain، Ollama، OpenAI... |
| شريط سفلي | أقواس، تنصيص، رموز، Tab، تراجع/إعادة، أسهم |
| تكملة نصوص | كلمات مفتاحية + دوال مدمجة + كلمات من ملفك |

## بنية المشروع

```
pyeditor/
├── main.py            # التطبيق الكامل
├── libraries.json     # قائمة المكتبات المدمجة (1385 مكتبة)
└── buildozer.spec     # إعدادات بناء الـ APK
```

---

## أولاً: تشغيل التطبيق للتجربة داخل Termux

```bash
# ثبّت Termux من F-Droid (وليس Google Play)
pkg update && pkg upgrade
pkg install python git

# للواجهة الرسومية ثبّت Termux:X11 من F-Droid أيضاً
pkg install x11-repo
pkg install termux-x11-nightly

# داخل Ubuntu عبر proot (الطريقة الأضمن لتشغيل Kivy):
pkg install proot-distro
proot-distro install ubuntu
proot-distro login ubuntu

# داخل أوبونتو:
apt update && apt install -y python3-pip python3-venv
python3 -m venv venv && source venv/bin/activate
pip install kivy pygments
cd /path/to/pyeditor
python main.py
```

> ملاحظة: Kivy يحتاج سيرفر رسوميات؛ الأسهل تشغيله عبر proot-distro ubuntu
> مع termux-x11، أو تجربة التطبيق مباشرة بعد بناء الـ APK.

---

## ثانياً: تحويل التطبيق إلى APK باستخدام Termux

> ⚠️ **تنبيه مهم**: buildozer لا يعمل داخل Termux مباشرة، بل يحتاج توزيعة لينكس
> كاملة عبر `proot-distro`. تأكد من توفر:
> - مساحة فارغة **15 جيجابايت** على الأقل
> - ذاكرة RAM **4 جيجابايت** على الأقل (8 أفضل)
> - اتصال إنترنت قوي (تحميل SDK/NDK بحجم عدة جيجا)
> - صبر 😄 (أول بناء يستغرق 30–90 دقيقة)

### الخطوة 1: تجهيز Termux و Ubuntu

```bash
pkg update && pkg upgrade -y
pkg install proot-distro -y
proot-distro install ubuntu
proot-distro login ubuntu

# داخل Ubuntu ثبّت الأدوات المطلوبة:
apt update && apt upgrade -y
apt install -y python3-pip python3-venv git zip unzip openjdk-17-jdk \\
    autoconf libtool pkg-config zlib1g-dev libncurses5-dev libffi-dev \\
    libssl-dev libltdl-dev make cmake default-jdk

# أعطِ مجلد التخزين صلاحية الوصول (من Termux وليس Ubuntu):
# خرج بـ exit ثم نفّذ:
# termux-setup-storage
```

### الخطوة 2: نسخ المشروع إلى Ubuntu

من Termux (ليس داخل Ubuntu):

```bash
mkdir -p ~/ubuntu-fs/root/pyeditor 2>/dev/null
cp -r /sdcard/Download/pyeditor/* ~/ubuntu-fs/root/pyeditor/ 2>/dev/null
# أو إذا نسخت الملفات يدوياً إلى مجلد التخزين:
proot-distro login ubuntu
```

ثم داخل Ubuntu:

```bash
python3 -m venv venv && source venv/bin/activate
pip install --upgrade pip
pip install buildozer cython==0.29.36
cd /root/pyeditor
```

### الخطوة 3: البناء

```bash
buildozer android debug
```

- أول مرة سيحمّل Android SDK + NDK تلقائياً (عدة جيجابا).
- عند النجاح ستجد الملف في: `bin/pyeditor-0.1-arm64-v8a-debug.apk`

لبناء نسخة الإصدار (أصغر وموقعة):

```bash
buildozer android release
```

### الخطوة 4: نقل الـ APK للهاتف وتثبيته

من داخل Ubuntu انسخ الناتج إلى التخزين:

```bash
exit  # خروج إلى Termux
cp ~/ubuntu-fs/root/pyeditor/bin/*.apk /sdcard/Download/
```

ثم من مدير ملفات الهاتف افتح ملف الـ APK من مجلد Download:

1. سيسألك عن السماح بتثبيت تطبيقات من مصادر غير معروفة — وافق.
2. اضغط "تثبيت" ثم "فتح".

---

## بدائل أسرع إذا كان هاتفك ضعيفاً

1. **GitHub Actions (مجاني 100%)**: ارفع المشروع على GitHub واستخدم سيرفر GitHub
   المجاني للبناء — ستحصل على الـ APK خلال دقائق بدون استهلاك موارد هاتفك.
   ابحث عن "buildozer github actions" وستجد قوالب جاهزة.
2. **Google Colab**: نفّذ buildozer داخل Colab (سيرفر Linux كامل مجاناً).
3. **Pydroid 3**: ثبّت Pydroid 3 ثم البرنامج المساعد "Pydroid repository plugin"
   ومنه يمكنك تصدير أي مشروع Python كـ APK من داخل الهاتف مباشرة.

---

## حل المشكلات الشائعة

| المشكلة | الحل |
|---|---|
| فشل التحميل بسبب حجم كبير | استخدم VPN أو شبكة Wi-Fi مستقرة |
| نفاد الذاكرة أثناء البناء | أغلق كل التطبيقات، أو أضف ملف `swap` |
| `command failed: gradlew` | نفّذ `buildozer android clean` ثم أعد البناء |
| Kivy لا يشتغل داخل Termux مباشرة | هذا طبيعي — استخدم proot-distro ubuntu |
| خطأ في pip داخل التطبيق | تأكد من صلاحية INTERNET في buildozer.spec |

---

## ملاحظات

- قائمة المكتبات المدمجة فيها **1385 مكتبة** حقيقية، وزر "مزامنة" يحمّل
  أشهر 8000 مكتبة على PyPI تلقائياً.
- تثبيت مكتبات ضخمة مثل TensorFlow داخل التطبيق قد يفشل على بعض الهواتف
  بسبب حجمها — جرّب نسخ `tensorflow-cpu` أو `tflite-runtime`.
'''

with open('/mnt/agents/output/pyeditor/buildozer.spec', 'w', encoding='utf-8') as f:
    f.write(spec)
with open('/mnt/agents/output/pyeditor/README_AR.md', 'w', encoding='utf-8') as f:
    f.write(readme)

import os
for fn in os.listdir('/mnt/agents/output/pyeditor'):
    p = os.path.join('/mnt/agents/output/pyeditor', fn)
    print(fn, os.path.getsize(p), "bytes")

# فحص سريع لصحة syntax
import ast
with open('/mnt/agents/output/pyeditor/main.py', encoding='utf-8') as f:
    src = f.read()
try:
    tree = ast.parse(src)
    print("✓ main.py syntax OK")
except SyntaxError as e:
    print("✗ Syntax error:", e)

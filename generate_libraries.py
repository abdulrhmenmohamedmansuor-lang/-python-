import json, os

os.makedirs('/mnt/agents/output/pyeditor', exist_ok=True)

cats = {
"AI/تعلم آلي": """tensorflow torch torchvision torchaudio keras keras-tuner scikit-learn scipy numpy pandas transformers
datasets accelerate peft trl diffusers tokenizers sentence-transformers sentencepiece tiktoken openai anthropic
google-generativeai groq ollama langchain langchain-core langchain-community langchain-openai langchain-anthropic
llama-index llama-index-core llama-index-llms-openai chromadb qdrant-client faiss-cpu faiss-gpu weaviate-client
pinecone-client pymilvus pgvector open-clip-torch clip-interrogator ultralytics yolov5 detectron2 mmcv mmengine
timm torchmetrics pytorch-lightning lightning jax flax optax equinox dm-haiku keras-cv keras-nlp tensorflow-hub
tensorflow-datasets tf-keras tensorflow-probability tensorflow-text torch-geometric torchdrug dgl networkx
node2vec karateclub stable-baselines3 gymnasium gym ray optuna hyperopt xgboost lightgbm catboost shap lime
eli5 mlxtend imbalanced-learn pycaret evalml mlflow wandb tensorboard tensorboardx autogluon autokeras tpot
lazypredict category-encoders featuretools missingno yellowbrick statsmodels prophet pmdarima tsfresh darts
sktime neuralprophet pytorch-forecasting statsforecast mlforecast darts xgboost ray tune-sklearn skopt bayesian-optimization
albumentations imgaug augly cleanlab adversarial-robustness-toolbox foolbox segmentation-models-pytorch open3d
mediapipe face-recognition dlib mtcnn retina-face deepface fer supervision roboflow onnx onnxruntime tf2onnx
skl2onnx openvino coremltools fastai einops torchinfo torchviz hiddenlayer netron opencv-python opencv-contrib-python
nltk spacy gensim textblob langdetect langid polyglot translate deep-translator googletrans sacremoses subword-nmt
sacrebleu rouge-score jiwer evaluate bert-score seqeval sentence-splitter unstructured pdf2image emoji word2number
inflect num2words textacy clean-text preprocessor scikit-learn-extra sklearn-crfsuite hmmlearn pgmpy bnlearn
causalml dowhy econml statsforecast prophet-neuralprophet orbit-ml lifelines scikit-survival imbalanced-ensemble
combo deslib deep-ensemble? deepensembles stacked-ensemble vecstack mlens mlem bentoml evidently whylogs
feast dbt-core apache-airflow prefect dagster luigi snakemake kedro metaflow zenml flyte argo-workflows
clearml comet-ml neptune-client aim sagemaker sagemaker-training azureml-core google-cloud-aiplatform kubeflow
adlfs gcsfs s3fs fsspec smart-open paramiko sshtunnel asyncio-nats nats-py aiokafka kafka-python confluent-kafka
pulsar-client celery rq dramatiq huey apscheduler schedule rocketry aiocron""",
"بيانات/ملفات": """polars duckdb dask vaex modin pyspark petl tablib openpyxl xlsxwriter xlrd xlwt python-docx
python-pptx pypdf pdfplumber PyMuPDF pdfminer-six reportlab weasyprint camelot-py tabula-py pyarrow fastparquet
h5py tables zarr netcdf4 rasterio geopandas shapely fiona folium geopy reverse-geocoder timezonefinder
rasterstats earthpy eemont sentinelsat sentinelsat copernicusmarine xarray rioxarray dask-geopandas movingpandas
beautifulsoup4 lxml html5lib selectolax parsel w3lib xmltodict dicttoxml jsonlines orjson ujson rapidjson
python-dateutil arrow pendulum humanize inflection python-slugify unidecode chardet charset-normalizer ftfy
openpyxl-stubs? python-magic filetype puremagic patool py7zr rarfile zipfile36? pyzipper stream-zip unzip? smart-getenv
sqlalchemy alembic peewee tortoise-orm pony pymongo motor redis psycopg2-binary asyncpg mysql-connector-python
pymysql sqlite-utils elasticsearch opensearch-py meilisearch typesense minio boto3 google-cloud-storage
azure-storage-blob supabase firebase-admin pymssql cx-oracle oracledb clickhouse-driver clickhouse-connect
snowflake-connector-python databricks-sql-warehouse? databricks-sql-connector pyathena google-cloud-bigquery
pandas-gbq redshift-connector cassandra-driver scylla-driver neo4j py2neo igraph graphviz pydot pygraphviz
anytree treelib ete3 biopython pysam scikit-bio""",
"ويب/شبكات": """flask django fastapi uvicorn gunicorn starlette tornado bottle pyramid falcon sanic quart litestar
requests httpx aiohttp urllib3 httpcore h11 h2 websockets websocket-client python-socketio python-engineio
selenium playwright pyppeteer scrapy curl-cffi cloudscraper undetected-chromedriver drissionpage splinter
mechanicalsoup robobrowser mechanical dryscrape? asyncio aiofiles aiodns aioresponses tenacity backoff retry
ratelimit cachecontrol requests-cache requests-toolbelt requests-oauthlib authlib oauthlib pyjwt python-jose
itsdangerous passlib bcrypt argon2-cffi cryptography pyopenssl pynacl pyotp qrcode segno python-barcode
python-telegram-bot aiogram telethon pyrogram discord.py nextcord py-cord tweepy praw instaloader yt-dlp
pytube spotipy lyricsgenius wikipedia imdbpy tmdbsimple facebook-sdk linkedin-api? python-binance ccxt
yfinance investpy? investiny alpha-vantage pandas-datareader quandl fredapi cryptocompare pycoingecko""",
"وسائط/صوت/صورة": """moviepy pydub librosa soundfile sounddevice pyaudio pyttsx3 gtts edge-tts openai-whisper
faster-whisper whisperx vosk speechrecognition pysrt ffmpeg-python imageio imageio-ffmpeg av scikit-image
rembg easyocr paddleocr rapidocr-onnxruntime pytesseract pdf2image wand pillow pillow-heif pillow-avif-plugin
imagehash piexif exifread python-resize-image? img2pdf pdf2image cairosvg svglib manim manimgl pygame pyglet
arcade panda3d ursina kivy kivymd flet customtkinter ttkbootstrap nicegui streamlit gradio dash panel bokeh
altair voila jupyter notebook jupyterlab ipython ipywidgets nbconvert nbformat papermill jupytext voila
pywebview eel pyinstaller nuitka cx-freeze briefcase pysimplegui dearpygui pyqt5 pyqt6 pyside2 pyside6
wxpython toga beeware?""",
"أدوات/أخرى": """rich click typer fire tqdm alive-progress loguru structlog dynaconf environs python-dotenv pydantic
marshmallow attrs cattrs dataclasses-json PyYAML toml tomlkit freezegun faker factory-boy mimesis joblib
cloudpickle dill tinydb boltons more-itertools toolz cytoolz funcy lru-dict expiringdict memoization diskcache
pytest hypothesis tox nox coverage pytest-cov pytest-mock pytest-asyncio responses requests-mock vcrpy locust
sphinx mkdocs mkdocs-material docutils mistune markdown markdownify bleach pypandoc setuptools wheel pip
virtualenv poetry pipenv pip-tools conda-pack? shiv pex zipapp pyoxidizer? cython numba cffi pybind11 cppimport
watchdog psutil py-cpuinfo gputil pynvml nvidia-ml-py pyudev pyserial pyusb bleak pybluez nfcpy? pyscard
keyboard mouse pynput pyautogui mss pyscreenshot pygetwindow pywin32? pywinauto? pyperclip clipboard pyqr?""",
}

libs = set()
for v in cats.values():
    for tok in v.split():
        tok = tok.strip()
        if tok and '?' not in tok and tok not in ('deep-ensemble?',):
            libs.add(tok.lower().replace('pyyaml','pyyaml'))

libs = sorted(libs)
len(libs)

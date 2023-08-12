import os
import logging
import pdfplumber
import sys
from flask import Flask, request, url_for, send_from_directory, render_template
from werkzeug.utils import secure_filename
from model import OpenAIModel
from translator import PDFTranslator
from flasgger import Swagger
from utils import LOG

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "files"
swagger = Swagger(app)

model = OpenAIModel(model="gpt-3.5-turbo",
                    api_key=os.environ.get("API2D_API_KEY"))


@app.get("/")
def index():
    return render_template('index.html')


@app.post("/translate/pdf")
def translatePdf():
    """Translate Pdf.
    ---
    tags:
      - Translate Api
    parameters:
      - name: file
        in: formData
        type: file        
        required: true
        description: The target pdf file to be translated
      - name: start
        in: query
        type: int        
        required: false
        default: 1
        description: the start of the pdf pages
      - name: end
        in: query
        type: int        
        required: false
        default: 1
        description: the end of the pdf pages
      - name: lang
        in: query
        type: string        
        required: false
        default: 中文
        description: The target languague translated to
    definitions:
        Result:
          type: object
          properties:
            msg: 
              type: string
              description: the message of the result
            success:
              type: bool
              description: the status of the request
            token:
              type: int
              description: the consumed token numbers
    responses:
      200:
        description: the result of the request
        schema:
          $ref: '#/definitions/Result'
    """
    start = request.args.get("start", type=int, default=1)
    end = request.args.get("end", type=int, default=1)

    if end < start:
        return {
            "success": False,
            "msg": f"end({end}) must larger than start({start})."
        }

    file = request.files['file']
    if file == None:
        LOG.error("file is a must.")
        return {
            "success": False,
            "msg": "file is a must."
        }

    lang = request.args.get("lang", type=str, default="中文")
    LOG.info(
        f"receive request to parse {file.filename} to {lang} from page {start} to page {end}.")

    ext = file.filename.rsplit(".", 1)[1].lower()
    if ext != "pdf":
        LOG.error("Must be a pdf file.")
        return {
            "success": False,
            "msg": "Must be a pdf."
        }

    filename = secure_filename(file.filename)
    filename_without_ext = filename.rsplit(".", 1)[0]

    # 对 pdf 文件进行解析
    fullpath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(fullpath)

    translated_filename = f"{filename_without_ext}_translated.pdf"
    file_url = url_for("files", filename=translated_filename)

    translator = PDFTranslator(model)
    token_number = translator.translate_pdf(fullpath, target_language=lang,  start=start, end=end)

    return {
        "success": True,
        "msg": file_url,
        "token": token_number
    }


@app.get("/files/<filename>")
def files(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


if __name__ == "__main__":
    app.run(debug=True)

from flask import request, jsonify, Blueprint
from . import s3, s3_bucket
from .helper import token_required, add_cors_headers


app = Blueprint('file_routes_blueprint', __name__)


@app.route("/upload", methods=["POST"])
@add_cors_headers
@token_required
def upload_file(user):
    if "file" not in request.files:
        return jsonify({"message": "No file key in request.files"}), 400
    file = request.files["file"]
    f_type = request.args.get('ftype')
    if f_type is None:
        return jsonify({"message": "No ftype key in url param"}), 400
    name = f"{user.id}-{f_type}" 
    try:
        output = upload_to_s3(name, file)
    except Exception as e:
        print(e)
        return jsonify({"message": "upload failed."}), 500
    return jsonify({"message": "uploaded."}), 200


def upload_to_s3(name, file):
    s3.upload_fileobj(
        file,
        s3_bucket,
        name
    )

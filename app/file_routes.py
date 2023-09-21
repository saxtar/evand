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


@app.route("/download", methods=["GET"])
@token_required
def download_file(user):
    f_type = request.args.get('ftype')
    if f_type is None:
        return jsonify({"message": "No ftype key in url param"}), 400
    name = f"{user.id}-{f_type}" 
    try:
        output = get_download_link_from_s3(name)
    except Exception as e:
        print(e)
        return jsonify({"message": "get download link failed."}), 500
    return jsonify({"link": output}), 200


def upload_to_s3(name, file):
    s3.upload_fileobj(
        file,
        s3_bucket,
        name
    )


def get_download_link_from_s3(key):
    return s3.generate_presigned_url(
        'get_object',
        Params={
            'Bucket': s3_bucket,
            'Key': key
        },
        ExpiresIn=3600
    )



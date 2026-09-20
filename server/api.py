import json
import os

from flask import redirect, send_from_directory
from uuid import UUID
from decimal import Decimal
from datetime import datetime
from flask import Flask
from flask import jsonify
from flask import request
from flasgger import Swagger

from config import ALLOWED_ORIGINS, API_BASE_URL
from database import Database

app = Flask(__name__)

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "ESP32CAM Monitoring API",
        "description": "Dokumentasi API untuk sistem monitoring ESP32CAM dengan database PostgreSQL",
        "version": "1.0.0"
    },
    "host": "api-monitor.fhanafii.my.id",
    "schemes": [
        "https",
        "http"
    ]
}

swagger = Swagger(app, template=swagger_template)

db = Database()

@app.after_request
def add_cors_headers(response):
    origin = request.headers.get("Origin")

    if origin in ALLOWED_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Vary"] = "Origin"
        response.headers["Access-Control-Allow-Methods"] = (
            "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        )
        response.headers["Access-Control-Allow-Headers"] = (
            "Content-Type, Authorization"
        )

    return response

def serialize(data):

    return json.loads(
        json.dumps(
            data,
            default=lambda o:
                str(o) if isinstance(o, (UUID, datetime))
                else float(o) if isinstance(o, Decimal)
                else o
        )
    )

@app.route("/")
def home():
    return redirect("/apidocs/")

@app.route("/api/detections", methods=["GET"])
def get_detections():
    """
    Get paginated and filtered detections list
    ---
    parameters:
      - name: page
        in: query
        type: integer
        required: false
        description: Page number (default 1)
      - name: limit
        in: query
        type: integer
        required: false
        description: Items per page (default 20, max 50)
      - name: status
        in: query
        type: string
        required: false
        description: Filter by detection status
      - name: start
        in: query
        type: string
        required: false
        description: Start date filter (YYYY-MM-DD)
      - name: end
        in: query
        type: string
        required: false
        description: End date filter (YYYY-MM-DD)
      - name: keyword
        in: query
        type: string
        required: false
        description: Search keyword or query
    responses:
      200:
        description: List of paginated detections
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            page:
              type: integer
              example: 1
            limit:
              type: integer
              example: 20
            total:
              type: integer
              example: 100
            total_pages:
              type: integer
              example: 5
            count:
              type: integer
              example: 20
            data:
              type: array
              items:
                type: object
      400:
        description: Invalid parameters / keyword too long
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            message:
              type: string
              example: Keyword terlalu panjang
      500:
        description: Server error
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            message:
              type: string
    """

    try:
        page = int(request.args.get("page", 1, type=int))
        limit = int(request.args.get("limit", 20, type=int))
        if page < 1:
            page = 1

        if limit < 1:
            limit = 20

        if limit > 50:
            limit = 50
        
        status = request.args.get("status")
        start = request.args.get("start")
        end = request.args.get("end")
        keyword = ( request.args.get("keyword") or request.args.get("q") or "" ).strip()

        if len (keyword) > 50:
            return jsonify({
                "success": False,
                "message": "Keyword terlalu panjang"
            }), 400
        
        result = db.get_paginated(
            page=page,
            limit=limit,
            status=status,
            start=start,
            end=end,
            keyword=keyword
        )

        return jsonify({
            "success": True,
            "page": result["page"],
            "limit": result["limit"],
            "total": result["total"],
            "total_pages": result["total_pages"],
            "count": len(result["rows"]),
            "data": serialize(result["rows"])

        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }),500

@app.route("/api/dashboard")
def dashboard():
    """
    Get dashboard statistics data
    ---
    responses:
      200:
        description: Dashboard statistics data retrieved successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
              description: Statistik ringkasan data dari database
      500:
        description: Server error
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            message:
              type: string
    """

    try:
        data = db.get_dashboard()
        return jsonify({
            "success":True,
            "data":serialize(data)
        })

    except Exception as e:

        return jsonify({
            "success":False,
            "message":str(e)
        }),500

@app.route("/api/detections/<uuid:detection_id>", methods=["GET"])
def get_detection(detection_id):
    """
    Get detection detail by UUID including media list
    ---
    parameters:
      - name: detection_id
        in: path
        type: string
        format: uuid
        required: true
        description: Detection UUID
    responses:
      200:
        description: Detection detail retrieved successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
              properties:
                id:
                  type: string
                  format: uuid
                images:
                  type: array
                  items:
                    type: object
                video:
                  type: object
      404:
        description: Data not found
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            message:
              type: string
              example: Data tidak ditemukan
      500:
        description: Server error
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            message:
              type: string
    """

    try:
        detection = db.get_by_id(str(detection_id))

        if not detection:

            return jsonify({
                "success": False,
                "message": "Data tidak ditemukan"
            }), 404

        images, video = build_media(
            detection["batch_folder"],
            detection["batch_number"]
        )

        result = serialize(detection)

        result["images"] = images
        result["video"] = video

        return jsonify({
            "success": True,
            "data": result
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

@app.route("/api/detections/<uuid:detection_id>/files")
def detection_files(detection_id):
    """
    Get list of image and video files associated with a detection
    ---
    parameters:
      - name: detection_id
        in: path
        type: string
        format: uuid
        required: true
        description: Detection UUID
    responses:
      200:
        description: Files list retrieved successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            batch_folder:
              type: string
            batch_number:
              type: integer
            images:
              type: array
              items:
                type: object
                properties:
                  name:
                    type: string
                  url:
                    type: string
            video:
              type: object
              properties:
                name:
                  type: string
                url:
                  type: string
      404:
        description: Data or folder not found
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            message:
              type: string
      500:
        description: Server error
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            message:
              type: string
    """

    try:
        data = db.get_files_info(str(detection_id))

        if not data:

            return jsonify({
                "success": False,
                "message": "Data tidak ditemukan"
            }), 404

        batch_folder = data["batch_folder"]
        batch_number = data["batch_number"]

        absolute_folder = os.path.abspath(batch_folder)

        if not os.path.exists(absolute_folder):

            return jsonify({
                "success": False,
                "message": "Folder batch tidak ditemukan"
            }), 404

        images = []

        video = None

        for file in sorted(os.listdir(absolute_folder)):

            if file.lower().endswith(".jpg"):
                images.append({
                    "name": file,
                    "url": f"{API_BASE_URL}/api/files/{batch_folder}/{file}"
                })

            elif file.lower().endswith(".mp4"):
                video = {
                    "name": file,
                    "url": f"{API_BASE_URL}/api/files/{batch_folder}/{file}"
                }

        return jsonify({
            "success": True,
            "batch_folder": batch_folder,
            "batch_number": batch_number,
            "images": images,
            "video": video

        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@app.route("/api/files/<path:filepath>")
def serve_file(filepath):

    try:
        absolute_path = os.path.abspath(filepath)
        folder = os.path.dirname(absolute_path)
        filename = os.path.basename(absolute_path)

        return send_from_directory(folder, filename)

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 404


def build_media(batch_folder, batch_number):

    absolute_folder = os.path.abspath(batch_folder)

    images = []
    video = None

    if not os.path.exists(absolute_folder):
        return images, video

    for file in sorted(os.listdir(absolute_folder)):

        if file.lower().endswith(".jpg"):
            images.append({
                "name": file,
                "detected": "_detected" in file,
                "url": f"{API_BASE_URL}/api/files/{batch_folder}/{file}"
            })

        elif file.lower().endswith(".mp4"):
            video = {
                "name": file,
                "url": f"{API_BASE_URL}/api/files/{batch_folder}/{file}"
            }

    return images, video

if __name__=="__main__":

    app.run(
        host="0.0.0.0",
        port=5001,
        debug=True
    )

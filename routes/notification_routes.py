from flask import Blueprint, request, jsonify
from models.db import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from datetime import datetime

notifications_bp = Blueprint('notifications', __name__)

notifications_collection = db['notifications']

@notifications_bp.route('/index', methods=['GET'])
@jwt_required()
def get_notifications():
    try:

        user_id = request.args.get('user_id')

        query = {}

        if user_id:
            if not ObjectId.is_valid(user_id):
                return jsonify({"message": "Invalid user_id parameter."}), 400
            query["user_id"] = ObjectId(user_id)

        notifications = notifications_collection.find(query)

        response = []
        for notification in notifications:
            response.append({
                "_id": str(notification["_id"]),
                "user_id": str(notification["user_id"]),
                "dataset_type": notification.get("dataset_type", ""),
                "message": notification.get("message", ""),
                "read": notification.get("read", False),
                "created_at": notification.get("created_at", "").isoformat() if notification.get("created_at") else None
            })

        return jsonify({"message" : "Notifications fetched successfully!", "notifications": response}), 200

    except Exception as e:
        return jsonify({"message": f"Error retrieving notifications: {str(e)}"}), 500

@notifications_bp.route('/mark-read/<user_id>/<notification_id>', methods=['PATCH'])
def mark_notification_as_read(user_id, notification_id):

    try:
        if not all([ObjectId.is_valid(user_id), ObjectId.is_valid(notification_id)]):
            return jsonify({"message": "Invalid user ID or notification ID."}), 400

        result = notifications_collection.update_one(
            {"_id": ObjectId(notification_id), "user_id": ObjectId(user_id)},
            {"$set": {"read": True}}
        )

        if result.matched_count == 0:
            return jsonify({"message": "Notification not found or does not belong to this user."}), 404

        return jsonify({"message": "Notification marked as read."}), 200

    except Exception as e:
        return jsonify({"message": f"Error marking notification as read: {str(e)}"}), 500

@notifications_bp.route('/find/<string:notification_id>', methods=['GET'])
@jwt_required()
def get_notification_detail(notification_id):

    try:

        notification = notifications_collection.find_one({"_id" : ObjectId(notification_id)})

        if not notification:
            return jsonify({"error": "Notification not found"}), 404

        notification["_id"] = str(notification["_id"])
        notification["user_id"] = str(notification["user_id"])
        notification["teacher_id"] = str(notification["teacher_id"])
        teacher_data = db.users.find_one({"_id": ObjectId(notification["teacher_id"])})
        if teacher_data:
            notification["teacher"] = {
                "_id": str(teacher_data["_id"]),
                "first_name": teacher_data.get("first_name"),
                "last_name": teacher_data.get("last_name"),
            }

        return jsonify({"message": "Notification found successfully!", "notification": notification}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
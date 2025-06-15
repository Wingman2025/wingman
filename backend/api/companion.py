"""Companion App API blueprint (migrated).

Provides REST endpoints for motivational companion features:
- Goal templates
- User goals
- Badges
- Update goal progress

This file replaces the legacy dynamic proxy that imported `companion_api.py`.
"""

from flask import Blueprint, jsonify, request, session, abort
from backend.models.legacy import (
    db,
    GoalTemplate,
    UserGoal,
    Badge,
    UserBadge,
)

companion_bp = Blueprint("companion", __name__, url_prefix="/api")

# ---------------------------- Helper utilities -----------------------------

def _require_login():
    user_id = session.get("user_id")
    if not user_id:
        abort(401, description="Authentication required")
    return user_id

# --------------------------- Public API routes -----------------------------

@companion_bp.get("/goal_templates")
def get_goal_templates():
    templates = GoalTemplate.query.order_by(GoalTemplate.category).all()
    return jsonify([
        {
            "id": t.id,
            "title": t.title,
            "description": t.description,
            "category": t.category,
            "difficulty_level": t.difficulty_level,
            "estimated_duration_days": t.estimated_duration_days,
            "icon": t.icon,
            "target_type": t.target_type,
            "default_target_value": t.default_target_value,
        }
        for t in templates
    ])


@companion_bp.get("/badges")
def get_badges():
    badges = Badge.query.order_by(Badge.category, Badge.rarity).all()
    return jsonify([
        {
            "id": b.id,
            "name": b.name,
            "description": b.description,
            "icon": b.icon,
            "category": b.category,
            "rarity": b.rarity,
            "points_value": b.points_value,
            "is_active": b.is_active,
        }
        for b in badges
    ])


@companion_bp.get("/user_goals")
def get_user_goals():
    user_id = _require_login()
    goals = (
        UserGoal.query.filter_by(user_id=user_id)
        .order_by(UserGoal.status, UserGoal.start_date.desc())
        .all()
    )
    return jsonify([
        {
            "id": g.id,
            "title": g.custom_title or (g.goal_template.title if g.goal_template else ""),
            "description": g.custom_description or (g.goal_template.description if g.goal_template else ""),
            "target_value": g.target_value,
            "current_progress": g.current_progress,
            "status": g.status,
            "start_date": g.start_date.isoformat() if g.start_date else None,
            "target_date": g.target_date.isoformat() if g.target_date else None,
            "completed_date": g.completed_date.isoformat() if g.completed_date else None,
        }
        for g in goals
    ])


@companion_bp.patch("/update_goal_progress")
def update_goal_progress():
    user_id = _require_login()
    data = request.get_json(force=True)
    goal_id = data.get("goal_id")
    progress = data.get("progress")
    if goal_id is None or progress is None:
        abort(400, description="goal_id and progress are required")

    goal = UserGoal.query.filter_by(id=goal_id, user_id=user_id).first()
    if not goal:
        abort(404, description="Goal not found")

    goal.current_progress = progress
    if goal.current_progress >= goal.target_value:
        goal.status = "completed"
        # TODO: trigger badge unlock logic here
    db.session.commit()

    return jsonify({
        "id": goal.id,
        "current_progress": goal.current_progress,
        "status": goal.status,
    })

# --------------------------- Badges endpoints ------------------------------

@companion_bp.post("/unlock_badge")
def unlock_badge():
    user_id = _require_login()
    data = request.get_json(force=True)
    badge_id = data.get("badge_id")
    if badge_id is None:
        abort(400, description="badge_id is required")

    badge = Badge.query.get(badge_id)
    if not badge:
        abort(404, description="Badge not found")

    existing = UserBadge.query.filter_by(user_id=user_id, badge_id=badge_id).first()
    if existing:
        return jsonify({"message": "Badge already unlocked"}), 200

    user_badge = UserBadge(user_id=user_id, badge_id=badge_id)
    db.session.add(user_badge)
    db.session.commit()

    return jsonify({
        "message": "Badge unlocked",
        "badge_id": badge_id,
        "unlocked_at": user_badge.unlocked_at.isoformat(),
    }), 201

__all__ = ["companion_bp"]

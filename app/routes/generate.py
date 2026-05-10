from flask import Blueprint, request, jsonify, g
from app.pipeline_runner import ViralImagePipeline
from app.security import require_api_key

bp = Blueprint("generate", __name__)

@bp.route("/generate", methods=["POST"])
@require_api_key
def generate():
    data = request.json or {}

    pipeline = ViralImagePipeline()
    results, stats = pipeline.run(
        query=data.get("query", "oddly satisfying"),
        num_images=int(data.get("num_images", 2))
    )

    return jsonify({
        "success": True,
        "request_id": g.request_id,
        "run_id": pipeline.run_id,
        "results_count": len(results),
        "results": results,
        "stats": stats
    })

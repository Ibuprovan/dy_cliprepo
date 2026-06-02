from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.database.models import Video, SessionLocal


class SQLiteManager:
    def __init__(self):
        self.Session = SessionLocal

    def get_db(self) -> Session:
        return self.Session()

    def add_video(self, data: dict) -> Video:
        db = self.get_db()
        try:
            video = Video(**data)
            db.add(video)
            db.commit()
            db.refresh(video)
            return video
        finally:
            db.close()

    def get_video_by_url(self, url: str) -> Optional[Video]:
        db = self.get_db()
        try:
            return db.query(Video).filter(Video.url == url).first()
        finally:
            db.close()

    def get_video_by_id(self, video_id: int) -> Optional[Video]:
        db = self.get_db()
        try:
            return db.query(Video).filter(Video.id == video_id).first()
        finally:
            db.close()

    def get_videos(
        self,
        page: int = 1,
        size: int = 20,
        category: Optional[str] = None,
        tag: Optional[str] = None,
        min_quality: Optional[int] = None,
        sort_by: str = "synced_at",
        sort_order: str = "desc",
    ) -> dict:
        db = self.get_db()
        try:
            query = db.query(Video)

            if category:
                query = query.filter(Video.category == category)
            if tag:
                query = query.filter(Video.tags.contains(tag))
            if min_quality:
                query = query.filter(Video.quality_score >= min_quality)

            sort_column = getattr(Video, sort_by, Video.synced_at)
            if sort_order == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(sort_column)

            total = query.count()
            videos = query.offset((page - 1) * size).limit(size).all()
            pages = (total + size - 1) // size

            return {
                "items": [self._video_to_dict(v) for v in videos],
                "total": total,
                "page": page,
                "size": size,
                "pages": pages,
            }
        finally:
            db.close()

    def update_video(self, video_id: int, data: dict) -> Optional[Video]:
        db = self.get_db()
        try:
            video = db.query(Video).filter(Video.id == video_id).first()
            if video:
                for key, value in data.items():
                    setattr(video, key, value)
                db.commit()
                db.refresh(video)
            return video
        finally:
            db.close()

    def delete_video(self, video_id: int) -> bool:
        db = self.get_db()
        try:
            video = db.query(Video).filter(Video.id == video_id).first()
            if video:
                db.delete(video)
                db.commit()
                return True
            return False
        finally:
            db.close()

    def search_videos(self, query: str) -> list:
        db = self.get_db()
        try:
            videos = (
                db.query(Video)
                .filter(
                    (Video.title.contains(query))
                    | (Video.summary.contains(query))
                    | (Video.desc.contains(query))
                )
                .all()
            )
            return [self._video_to_dict(v) for v in videos]
        finally:
            db.close()

    def get_stats(self) -> dict:
        db = self.get_db()
        try:
            total = db.query(func.count(Video.id)).scalar()
            categories = (
                db.query(Video.category, func.count(Video.id))
                .group_by(Video.category)
                .all()
            )
            avg_quality = db.query(func.avg(Video.quality_score)).scalar() or 0

            category_distribution = [
                {
                    "category": cat or "未分类",
                    "count": count,
                    "percentage": round(count / total * 100, 1) if total > 0 else 0,
                }
                for cat, count in categories
            ]

            recent = (
                db.query(Video).order_by(desc(Video.synced_at)).limit(10).all()
            )

            return {
                "overview": {
                    "total_videos": total,
                    "total_categories": len(categories),
                    "avg_quality_score": round(float(avg_quality), 1),
                },
                "category_distribution": category_distribution,
                "recent_syncs": [
                    {
                        "id": v.id,
                        "title": v.title,
                        "category": v.category,
                        "synced_at": v.synced_at.isoformat() if v.synced_at else None,
                    }
                    for v in recent
                ],
            }
        finally:
            db.close()

    def get_all_videos(self) -> list:
        db = self.get_db()
        try:
            videos = db.query(Video).all()
            return [self._video_to_dict(v) for v in videos]
        finally:
            db.close()

    def clear_all(self) -> int:
        db = self.get_db()
        try:
            count = db.query(Video).count()
            db.query(Video).delete()
            db.commit()
            return count
        finally:
            db.close()

    @staticmethod
    def _video_to_dict(video: Video) -> dict:
        return {
            "id": video.id,
            "url": video.url,
            "title": video.title,
            "author": video.author,
            "author_id": video.author_id,
            "desc": video.desc,
            "cover_path": video.cover_path,
            "summary": video.summary,
            "category": video.category,
            "tags": video.tags,
            "key_points": video.key_points,
            "quality_score": video.quality_score,
            "created_at": video.created_at.isoformat() if video.created_at else None,
            "favorited_at": video.favorited_at.isoformat() if video.favorited_at else None,
            "synced_at": video.synced_at.isoformat() if video.synced_at else None,
            "embedding_id": video.embedding_id,
        }


db_manager = SQLiteManager()

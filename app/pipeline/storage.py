import json
import csv
import logging
import os
from datetime import datetime
from pathlib import Path
from io import StringIO
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

Base = declarative_base()

class PipelineRun(Base):
    __tablename__ = 'pipeline_runs'
    __table_args__ = (
        Index('ix_run_id', 'run_id'),
        Index('ix_started_at', 'started_at'),
        {'sqlite_autoincrement': True}
    )
    
    id = Column(Integer, primary_key=True)
    run_id = Column(String(50), unique=True, nullable=False)
    query = Column(String(500), nullable=False)
    num_images_requested = Column(Integer)
    num_images_generated = Column(Integer)
    pass_rate = Column(Float)
    avg_clip_score = Column(Float)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    status = Column(String(20))

class GeneratedImage(Base):
    __tablename__ = 'generated_images'
    __table_args__ = (
        Index('ix_generated_run_id', 'run_id'),
        Index('ix_video_id', 'video_id'),
        Index('ix_created_at', 'created_at'),
        {'sqlite_autoincrement': True}
    )
    
    id = Column(Integer, primary_key=True)
    run_id = Column(String(50), nullable=False)
    video_id = Column(String(100))
    caption = Column(Text)
    prompt = Column(Text)
    viral_score = Column(Float)
    clip_score = Column(Float)
    passed_quality_gate = Column(Boolean)
    attempt_number = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

class StorageManager:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.getenv('DATABASE_PATH', './outputs/pipeline.db')
        
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        Base.metadata.create_all(self.engine)
        
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
        logger.info(f"Database initialized: {db_path}")
        
        self.jobs_path = Path("./outputs/jobs")
        self.jobs_path.mkdir(parents=True, exist_ok=True)
    
    def save_run(self, run_id, query, num_requested, num_generated, 
                 pass_rate, avg_clip, status='success'):
        try:
            run = PipelineRun(
                run_id=run_id,
                query=query,
                num_images_requested=num_requested,
                num_images_generated=num_generated,
                pass_rate=pass_rate,
                avg_clip_score=avg_clip,
                completed_at=datetime.utcnow(),
                status=status
            )
            self.session.add(run)
            self.session.commit()
            logger.debug(f" Saved run {run_id}")
        except Exception as e:
            logger.error(f" Failed to save run: {e}")
            self.session.rollback()
    
    def save_image(self, run_id, video_id, caption, prompt, 
                   viral_score, clip_score, passed, attempt):
        try:
            image = GeneratedImage(
                run_id=run_id,
                video_id=video_id,
                caption=caption[:500],
                prompt=prompt[:2000],
                viral_score=viral_score,
                clip_score=clip_score,
                passed_quality_gate=passed,
                attempt_number=attempt
            )
            self.session.add(image)
            self.session.commit()
        except Exception as e:
            logger.error(f" Failed to save image: {e}")
            self.session.rollback()
    
    def get_stats(self, limit=100):
        try:
            runs = self.session.query(PipelineRun)\
                .order_by(PipelineRun.started_at.desc())\
                .limit(limit)\
                .all()
            
            if not runs:
                return {
                    'total_runs': 0,
                    'avg_pass_rate': 0,
                    'avg_clip_score': 0,
                    'total_images_generated': 0
                }
            
            return {
                'total_runs': len(runs),
                'avg_pass_rate': sum(r.pass_rate or 0 for r in runs) / len(runs),
                'avg_clip_score': sum(r.avg_clip_score or 0 for r in runs) / len(runs),
                'total_images_generated': sum(r.num_images_generated or 0 for r in runs)
            }
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {'error': str(e)}
    
    def export_runs(self, format='json', limit=100):
        try:
            runs = self.session.query(PipelineRun)\
                .order_by(PipelineRun.started_at.desc())\
                .limit(limit)\
                .all()
            
            if format == 'json':
                data = []
                for r in runs:
                    data.append({
                        'run_id': r.run_id,
                        'query': r.query,
                        'num_requested': r.num_images_requested,
                        'num_generated': r.num_images_generated,
                        'pass_rate': r.pass_rate,
                        'avg_clip_score': r.avg_clip_score,
                        'started_at': r.started_at.isoformat() if r.started_at else None,
                        'completed_at': r.completed_at.isoformat() if r.completed_at else None,
                        'status': r.status
                    })
                return data
            
            elif format == 'csv':
                output = StringIO()
                writer = csv.writer(output)
                writer.writerow(['run_id', 'query', 'num_requested', 'num_generated', 
                               'pass_rate', 'avg_clip_score', 'started_at', 'status'])
                
                for r in runs:
                    writer.writerow([
                        r.run_id, r.query, r.num_images_requested, 
                        r.num_images_generated, r.pass_rate, r.avg_clip_score,
                        r.started_at.isoformat() if r.started_at else '', r.status
                    ])
                
                return output.getvalue()
            
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        except Exception as e:
            logger.error(f"Failed to export runs: {e}")
            return {'error': str(e)} if format == 'json' else f"Error: {e}"
    
    def export_images(self, run_id=None, format='json', limit=1000):
        try:
            query = self.session.query(GeneratedImage)
            
            if run_id:
                query = query.filter_by(run_id=run_id)
            
            images = query.order_by(GeneratedImage.created_at.desc()).limit(limit).all()
            
            if format == 'json':
                data = []
                for i in images:
                    data.append({
                        'id': i.id,
                        'run_id': i.run_id,
                        'video_id': i.video_id,
                        'caption': i.caption,
                        'prompt': i.prompt[:200] if i.prompt else None,
                        'viral_score': i.viral_score,
                        'clip_score': i.clip_score,
                        'passed': i.passed_quality_gate,
                        'attempt': i.attempt_number,
                        'created_at': i.created_at.isoformat() if i.created_at else None
                    })
                return data
            
            elif format == 'csv':
                output = StringIO()
                writer = csv.writer(output)
                writer.writerow([
                    'id', 'run_id', 'video_id', 'caption', 'prompt_preview',
                    'viral_score', 'clip_score', 'passed', 'attempt', 'created_at'
                ])
                
                for i in images:
                    writer.writerow([
                        i.id,
                        i.run_id,
                        i.video_id,
                        i.caption[:100] if i.caption else '',
                        i.prompt[:100] if i.prompt else '',
                        i.viral_score,
                        i.clip_score,
                        i.passed_quality_gate,
                        i.attempt_number,
                        i.created_at.isoformat() if i.created_at else ''
                    ])
                
                return output.getvalue()
            
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        except Exception as e:
            logger.error(f"Failed to export images: {e}")
            return {'error': str(e)} if format == 'json' else f"Error: {e}"
    
    def close(self):
        try:
            self.session.close()
            logger.debug("Database session closed")
        except Exception as e:
            logger.error(f"Error closing database: {e}")

    def create_job_dir(self, run_id: str) -> Path:
        path = self.jobs_path / run_id
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    def save_job_json(self, run_id: str, name: str, data):
        job_dir = self.create_job_dir(run_id)
        file_path = job_dir / f"{name}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
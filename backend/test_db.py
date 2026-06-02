import sys
sys.path.insert(0, '.')

from app.database.models import Base, engine, SessionLocal
from app.database.sqlite_manager import db_manager

# 创建表
Base.metadata.create_all(bind=engine)
print('Database tables created')

# 测试添加视频
video_data = {
    'url': 'https://www.douyin.com/video/test123',
    'title': '测试视频标题',
    'author': '测试作者',
    'desc': '这是一个测试视频的描述',
    'summary': 'AI生成的总结',
    'category': '编程技术',
    'tags': ['Python', '测试'],
    'key_points': ['要点1', '要点2'],
    'quality_score': 8,
}

video = db_manager.add_video(video_data)
print(f'Video added: id={video.id}, title={video.title}')

# 测试查询
all_videos = db_manager.get_videos()
print(f'Total videos: {all_videos["total"]}')

# 测试统计
stats = db_manager.get_stats()
print(f'Stats: {stats["overview"]}')

print('Database tests passed!')

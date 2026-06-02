import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getVideoById, searchVideos } from '../api/client';
import type { Video } from '../types';

export default function VideoDetail() {
  const { id } = useParams<{ id: string }>();
  const [video, setVideo] = useState<Video | null>(null);
  const [similar, setSimilar] = useState<Video[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      loadVideo(parseInt(id));
    }
  }, [id]);

  async function loadVideo(videoId: number) {
    setLoading(true);
    try {
      const data = await getVideoById(videoId);
      setVideo(data);

      if (data.summary) {
        const result = await searchVideos(data.summary, 5, 'semantic');
        setSimilar(result.results.filter((v) => v.id !== videoId));
      }
    } catch (e) {
      console.error('Failed to load video:', e);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">加载中...</div>
      </div>
    );
  }

  if (!video) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">视频不存在</p>
        <Link to="/library" className="text-blue-500 hover:underline mt-2 inline-block">
          返回知识库
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <Link to="/library" className="text-sm text-gray-500 hover:text-gray-700">
        ← 返回知识库
      </Link>

      <div className="bg-white rounded-lg border p-6">
        <h1 className="text-xl font-bold text-gray-900 mb-4">{video.title}</h1>

        <div className="flex items-center gap-4 text-sm text-gray-500 mb-6">
          <span>作者：{video.author || '未知'}</span>
          {video.category && (
            <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded">
              {video.category}
            </span>
          )}
          {video.quality_score && (
            <span className="text-yellow-600">⭐ {video.quality_score}/10</span>
          )}
        </div>

        {video.cover_path && (
          <div className="mb-6">
            <img
              src={video.cover_path}
              alt={video.title}
              className="max-w-full rounded-lg"
              onError={(e) => {
                (e.target as HTMLImageElement).style.display = 'none';
              }}
            />
          </div>
        )}

        <div className="mb-6">
          <h2 className="text-lg font-semibold mb-2">AI 总结</h2>
          <p className="text-gray-700 leading-relaxed">{video.summary}</p>
        </div>

        {video.key_points && video.key_points.length > 0 && (
          <div className="mb-6">
            <h2 className="text-lg font-semibold mb-2">关键要点</h2>
            <ul className="list-disc list-inside space-y-1">
              {video.key_points.map((point, i) => (
                <li key={i} className="text-gray-700">
                  {point}
                </li>
              ))}
            </ul>
          </div>
        )}

        {video.tags && video.tags.length > 0 && (
          <div className="mb-6">
            <h2 className="text-lg font-semibold mb-2">标签</h2>
            <div className="flex flex-wrap gap-2">
              {video.tags.map((tag) => (
                <span
                  key={tag}
                  className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        )}

        {video.desc && (
          <div className="mb-6">
            <h2 className="text-lg font-semibold mb-2">原始描述</h2>
            <p className="text-gray-600 text-sm whitespace-pre-wrap">{video.desc}</p>
          </div>
        )}

        <div className="pt-4 border-t">
          <a
            href={video.url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center px-4 py-2 bg-pink-500 text-white rounded-lg hover:bg-pink-600"
          >
            在抖音中查看
          </a>
        </div>
      </div>

      {similar.length > 0 && (
        <div className="bg-white rounded-lg border p-6">
          <h2 className="text-lg font-semibold mb-4">同类推荐</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {similar.map((item) => (
              <Link
                key={item.id}
                to={`/video/${item.id}`}
                className="flex gap-3 p-3 rounded-lg hover:bg-gray-50"
              >
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {item.title}
                  </p>
                  <p className="text-xs text-gray-500 mt-1 line-clamp-2">
                    {item.summary}
                  </p>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-xs px-2 py-0.5 bg-gray-100 rounded">
                      {item.category}
                    </span>
                    {item.similarity && (
                      <span className="text-xs text-green-600">
                        相似度 {(item.similarity * 100).toFixed(0)}%
                      </span>
                    )}
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

import { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { getVideos, searchVideos } from '../api/client';
import type { Video } from '../types';

export default function Library() {
  const [searchParams] = useSearchParams();
  const initialCategory = searchParams.get('category') || '';

  const [videos, setVideos] = useState<Video[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [category, setCategory] = useState(initialCategory);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchMode, setSearchMode] = useState<'keyword' | 'semantic'>('semantic');

  useEffect(() => {
    loadVideos();
  }, [page, category]);

  async function loadVideos() {
    setLoading(true);
    try {
      const data = await getVideos({
        page,
        size: 20,
        category: category || undefined,
      });
      setVideos(data.items);
      setTotal(data.total);
      setPages(data.pages);
    } catch (e) {
      console.error('Failed to load videos:', e);
    } finally {
      setLoading(false);
    }
  }

  async function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    if (!searchQuery.trim()) {
      loadVideos();
      return;
    }
    setLoading(true);
    try {
      const data = await searchVideos(searchQuery, 20, searchMode);
      setVideos(data.results);
      setTotal(data.total);
      setPages(1);
    } catch (e) {
      console.error('Search failed:', e);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">知识库</h1>
        <span className="text-sm text-gray-500">共 {total} 条</span>
      </div>

      <form onSubmit={handleSearch} className="flex gap-2">
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="搜索视频..."
          className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <select
          value={searchMode}
          onChange={(e) => setSearchMode(e.target.value as 'keyword' | 'semantic')}
          className="px-3 py-2 border rounded-lg"
        >
          <option value="semantic">语义搜索</option>
          <option value="keyword">关键词</option>
        </select>
        <button
          type="submit"
          className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
        >
          搜索
        </button>
      </form>

      {category && (
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-500">筛选：</span>
          <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm">
            {category}
          </span>
          <button
            onClick={() => setCategory('')}
            className="text-sm text-gray-400 hover:text-gray-600"
          >
            清除
          </button>
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center h-32">
          <div className="text-gray-500">加载中...</div>
        </div>
      ) : videos.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-400">暂无视频数据</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {videos.map((video) => (
            <VideoCard key={video.id} video={video} />
          ))}
        </div>
      )}

      {pages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <button
            onClick={() => setPage(Math.max(1, page - 1))}
            disabled={page === 1}
            className="px-3 py-1 border rounded disabled:opacity-50"
          >
            上一页
          </button>
          <span className="text-sm text-gray-500">
            {page} / {pages}
          </span>
          <button
            onClick={() => setPage(Math.min(pages, page + 1))}
            disabled={page === pages}
            className="px-3 py-1 border rounded disabled:opacity-50"
          >
            下一页
          </button>
        </div>
      )}
    </div>
  );
}

function VideoCard({ video }: { video: Video }) {
  return (
    <Link
      to={`/video/${video.id}`}
      className="bg-white rounded-lg border overflow-hidden hover:shadow-md transition-shadow"
    >
      {video.cover_path && (
        <div className="aspect-video bg-gray-100">
          <img
            src={video.cover_path}
            alt={video.title}
            className="w-full h-full object-cover"
            loading="lazy"
            onError={(e) => {
              (e.target as HTMLImageElement).style.display = 'none';
            }}
          />
        </div>
      )}
      <div className="p-4">
        <h3 className="text-sm font-medium text-gray-900 line-clamp-2 mb-2">
          {video.title}
        </h3>
        {video.summary && (
          <p className="text-xs text-gray-500 line-clamp-3 mb-2">
            {video.summary}
          </p>
        )}
        <div className="flex items-center justify-between">
          <span className="text-xs px-2 py-1 bg-gray-100 rounded">
            {video.category || '未分类'}
          </span>
          {video.quality_score && (
            <span className="text-xs text-yellow-600">
              ⭐ {video.quality_score}
            </span>
          )}
        </div>
      </div>
    </Link>
  );
}

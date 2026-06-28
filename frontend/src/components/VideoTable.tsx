import { useState } from 'react';
import type { Video } from '../types';

interface VideoTableProps {
  videos: Video[];
  categories: string[];
  selectedCategory: string;
  onCategoryChange: (cat: string) => void;
}

function downloadMarkdown(video: Video) {
  const md = `# ${video.title}\n\n> ${video.summary || '暂无总结'}\n\n---\n\n原视频链接：${video.url}`;
  const blob = new Blob([md], { type: 'text/markdown;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${video.title.replace(/[/\\?%*:|"<>]/g, '_')}.md`;
  a.click();
  URL.revokeObjectURL(url);
}

export function VideoTable({ videos, categories, selectedCategory, onCategoryChange }: VideoTableProps) {
  const [imgErrors, setImgErrors] = useState<Set<number>>(new Set());

  return (
    <div>
      {/* 分类筛选栏 */}
      {categories.length > 1 && (
        <div className="flex flex-wrap gap-2 mb-4">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => onCategoryChange(cat === selectedCategory ? '' : cat)}
              className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${
                (cat === selectedCategory) || (cat === '全部' && !selectedCategory)
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      )}

      {videos.length === 0 ? (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 px-6 py-12 text-center text-gray-400">
          暂无视频数据，请先点击"开始同步"
        </div>
      ) : (
        <div className="grid gap-4">
          {videos.map((video) => (
            <div key={video.id} className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden flex flex-col sm:flex-row">
              {/* 封面图片 */}
              <div className="w-full sm:w-48 h-48 sm:h-auto bg-gray-100 flex-shrink-0">
                {video.cover_url && !imgErrors.has(video.id) ? (
                  <img
                    src={video.cover_url}
                    alt={video.title}
                    className="w-full h-full object-cover"
                    onError={() => setImgErrors((prev) => new Set(prev).add(video.id))}
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-gray-300 text-4xl">🎬</div>
                )}
              </div>

              {/* 信息区域 */}
              <div className="flex-1 p-5 flex flex-col justify-between min-w-0">
                <div>
                  <div className="flex items-start justify-between gap-3 mb-2">
                    <h3 className="text-base font-semibold text-gray-900 leading-snug">
                      <a href={video.url} target="_blank" rel="noopener noreferrer" className="hover:text-blue-600 transition-colors">
                        {video.title || '无标题'}
                      </a>
                    </h3>
                    <span className="text-xs text-gray-400 whitespace-nowrap shrink-0">{video.author || ''}</span>
                  </div>

                  {video.summary && (
                    <p className="text-sm text-gray-600 leading-relaxed mb-3">{video.summary}</p>
                  )}
                </div>

                {/* 操作按钮 */}
                <div className="flex items-center gap-2 mt-2">
                  <button
                    onClick={() => downloadMarkdown(video)}
                    disabled={!video.summary}
                    className="text-xs px-3 py-1.5 rounded-md bg-gray-100 text-gray-600 hover:bg-gray-200 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                  >
                    下载 Markdown
                  </button>
                  <a
                    href={video.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs px-3 py-1.5 rounded-md bg-blue-50 text-blue-600 hover:bg-blue-100 transition-colors"
                  >
                    打开原视频
                  </a>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

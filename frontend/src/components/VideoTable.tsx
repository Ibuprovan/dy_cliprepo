/**
 * 视频列表组件 — 极简设计系统
 * 单色卡片，border contrast，无彩色强调
 */

import { useState, useEffect } from 'react';
import { deleteVideo, deleteVideos } from '../api/client';
import type { Video } from '../types';

interface VideoTableProps {
  videos: Video[];
  categories: string[];
  selectedCategory: string;
  onCategoryChange: (cat: string) => void;
  onVideosChange: () => void;
}

function downloadMarkdown(video: Video) {
  const md = `# ${video.title}\n\n> ${video.summary || '暂无总结'}\n\n---\n\n原视频链接：${video.url}`;
  const blob = new Blob([md], { type: 'text/markdown;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${video.title.replace(/[/\\?%*:|"<>]/g, '_')}.md`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

export function VideoTable({ videos, categories, selectedCategory, onCategoryChange, onVideosChange }: VideoTableProps) {
  const [imgErrors, setImgErrors] = useState<Set<number>>(new Set());
  const [expandedTitles, setExpandedTitles] = useState<Set<number>>(new Set());
  const [deleting, setDeleting] = useState<number | null>(null);
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());
  const [batchDeleting, setBatchDeleting] = useState(false);

  useEffect(() => {
    setSelectedIds(new Set());
    setImgErrors(new Set());
    setExpandedTitles(new Set());
  }, [videos]);

  const toggleExpand = (id: number) => {
    setExpandedTitles((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id); else next.add(id);
      return next;
    });
  };

  const allSelected = videos.length > 0 && videos.every(v => selectedIds.has(v.id));

  const toggleSelect = (id: number) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id); else next.add(id);
      return next;
    });
  };

  const toggleSelectAll = () => {
    if (allSelected) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(videos.map((v) => v.id)));
    }
  };

  const handleDelete = async (video: Video) => {
    if (!confirm(`确定删除「${video.title || '无标题'}」？`)) return;
    setDeleting(video.id);
    try {
      await deleteVideo(video.id);
      setSelectedIds((prev) => { const n = new Set(prev); n.delete(video.id); return n; });
      onVideosChange();
    } catch (e) {
      console.error('删除失败:', e);
    } finally {
      setDeleting(null);
    }
  };

  const handleBatchDelete = async () => {
    if (selectedIds.size === 0) return;
    if (!confirm(`确定删除选中的 ${selectedIds.size} 个视频？此操作不可撤销。`)) return;
    setBatchDeleting(true);
    try {
      await deleteVideos(Array.from(selectedIds));
      setSelectedIds(new Set());
      onVideosChange();
    } catch (e) {
      console.error('批量删除失败:', e);
    } finally {
      setBatchDeleting(false);
    }
  };

  return (
    <div>
      {/* 分类筛选 — 极简 tab 风格 */}
      {categories.length > 1 && (
        <div className="flex flex-wrap gap-1 mb-5">
          {categories.map((cat) => {
            const isActive = (cat === selectedCategory) || (cat === '全部' && !selectedCategory);
            return (
              <button
                key={cat}
                onClick={() => onCategoryChange(cat === selectedCategory ? '' : cat)}
                className={`px-3 py-1.5 rounded-md text-xs font-medium tracking-tight transition-colors ${
                  isActive
                    ? 'bg-brand-900 text-brand-50'
                    : 'text-ink-400 hover:text-ink-700 hover:bg-brand-100'
                }`}
              >
                {cat}
              </button>
            );
          })}
        </div>
      )}

      {videos.length === 0 ? (
        <div className="bg-surface-50 rounded-lg border border-brand-200 px-6 py-16 text-center shadow-sm">
          <p className="text-ink-300 text-sm tracking-tight">暂无视频数据，请先点击「开始同步」</p>
        </div>
      ) : (
        <div>
          {/* 批量操作工具栏 */}
          <div className="flex items-center gap-3 mb-4 px-0.5">
            <label className="flex items-center gap-2 text-xs text-ink-400 cursor-pointer select-none tracking-tight">
              <input
                type="checkbox"
                checked={allSelected}
                onChange={toggleSelectAll}
                className="w-3.5 h-3.5 rounded"
              />
              全选
            </label>
            {selectedIds.size > 0 && (
              <span className="text-xs text-ink-400 tracking-tight">已选 {selectedIds.size} 项</span>
            )}
            <button
              onClick={handleBatchDelete}
              disabled={selectedIds.size === 0 || batchDeleting}
              className={`ml-auto text-xs px-3 py-1.5 rounded-md font-medium tracking-tight transition-colors ${
                selectedIds.size > 0
                  ? 'bg-danger text-white hover:bg-danger-text'
                  : 'bg-brand-100 text-ink-300 cursor-not-allowed'
              }`}
            >
              {batchDeleting ? '删除中...' : `批量删除${selectedIds.size > 0 ? ` (${selectedIds.size})` : ''}`}
            </button>
          </div>

          {/* 视频卡片列表 */}
          <div className="grid gap-3">
            {videos.map((video) => {
              const isExpanded = expandedTitles.has(video.id);
              const isSelected = selectedIds.has(video.id);
              return (
                <div
                  key={video.id}
                  className={`relative bg-surface-50 rounded-lg border overflow-hidden flex flex-col sm:flex-row shadow-sm transition-colors ${
                    isSelected
                      ? 'border-brand-900 ring-1 ring-brand-300'
                      : 'border-brand-200 hover:border-brand-300'
                  }`}
                >
                  {/* 复选框 */}
                  <div className="absolute sm:relative z-10 p-2.5">
                    <input
                      type="checkbox"
                      checked={isSelected}
                      onChange={() => toggleSelect(video.id)}
                      className="w-3.5 h-3.5 rounded cursor-pointer"
                    />
                  </div>

                  {/* 封面 */}
                  <div className="w-full sm:w-44 h-44 sm:h-auto bg-brand-100 flex-shrink-0">
                    {video.cover_url && !imgErrors.has(video.id) ? (
                      <img
                        src={video.cover_url}
                        alt={video.title}
                        className="w-full h-full object-cover"
                        referrerPolicy="no-referrer"
                        onError={() => setImgErrors((prev) => new Set(prev).add(video.id))}
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-brand-300 text-2xl">
                        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="m15.75 10.5 4.72-4.72a.75.75 0 0 1 1.28.53v11.38a.75.75 0 0 1-1.28.53l-4.72-4.72M4.5 18.75h9a2.25 2.25 0 0 0 2.25-2.25v-9a2.25 2.25 0 0 0-2.25-2.25h-9A2.25 2.25 0 0 0 2.25 7.5v9a2.25 2.25 0 0 0 2.25 2.25Z" />
                        </svg>
                      </div>
                    )}
                  </div>

                  {/* 信息 */}
                  <div className="flex-1 p-4 flex flex-col justify-between min-w-0">
                    <div>
                      <div className="flex items-start justify-between gap-3 mb-2">
                        <div className="min-w-0">
                          <h3 className={`text-sm font-semibold text-ink-900 leading-snug tracking-tight ${isExpanded ? '' : 'line-clamp-2'}`}>
                            <a href={video.url} target="_blank" rel="noopener noreferrer" className="hover:text-brand-600 transition-colors">
                              {video.title || '无标题'}
                            </a>
                          </h3>
                          {video.title && video.title.length > 30 && (
                            <button
                              onClick={() => toggleExpand(video.id)}
                              className="text-xs text-ink-400 hover:text-ink-600 mt-0.5 tracking-tight"
                            >
                              {isExpanded ? '收起' : '展开全部'}
                            </button>
                          )}
                        </div>
                        {video.author && (
                          <span className="text-xs text-ink-400 whitespace-nowrap shrink-0 tracking-tight">{video.author}</span>
                        )}
                      </div>

                      {video.summary && (
                        <p className="text-xs text-ink-500 leading-relaxed tracking-tight">{video.summary}</p>
                      )}
                    </div>

                    {/* 操作按钮 */}
                    <div className="flex items-center gap-2 mt-3">
                      <button
                        onClick={() => downloadMarkdown(video)}
                        disabled={!video.summary}
                        className="text-xs px-2.5 py-1.5 rounded-md bg-brand-100 text-ink-600 hover:bg-brand-200 disabled:opacity-30 disabled:cursor-not-allowed transition-colors tracking-tight"
                      >
                        下载 Markdown
                      </button>
                      <a
                        href={video.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs px-2.5 py-1.5 rounded-md bg-brand-50 text-ink-600 hover:bg-brand-100 border border-brand-200 transition-colors tracking-tight"
                      >
                        打开原视频
                      </a>
                      <button
                        onClick={() => handleDelete(video)}
                        disabled={deleting === video.id}
                        className="text-xs px-2.5 py-1.5 rounded-md text-danger-text hover:bg-danger-subtle disabled:opacity-30 transition-colors ml-auto tracking-tight"
                      >
                        {deleting === video.id ? '删除中...' : '删除'}
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

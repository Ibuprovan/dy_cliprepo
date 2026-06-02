import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getStats, startSync, stopSync, checkAuth, createSyncEventSource } from '../api/client';
import type { Stats, SyncTask, AuthStatus } from '../types';

export default function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [auth, setAuth] = useState<AuthStatus | null>(null);
  const [syncTask, setSyncTask] = useState<SyncTask | null>(null);
  const [syncMessage, setSyncMessage] = useState('');

  useEffect(() => {
    loadStats();
    loadAuth();
  }, []);

  async function loadStats() {
    try {
      const data = await getStats();
      setStats(data);
    } catch (e) {
      console.error('Failed to load stats:', e);
    } finally {
      setLoading(false);
    }
  }

  async function loadAuth() {
    try {
      const data = await checkAuth();
      setAuth(data);
    } catch (e) {
      console.error('Failed to check auth:', e);
    }
  }

  async function handleStartSync() {
    if (!auth?.logged_in) {
      setSyncMessage('请先登录抖音');
      return;
    }

    try {
      const result = await startSync();
      setSyncMessage('同步任务已启动');

      const eventSource = createSyncEventSource(result.task_id);

      eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        setSyncTask(data);

        if (data.status === 'completed') {
          setSyncMessage('同步完成');
          eventSource.close();
          loadStats();
        } else if (data.status === 'failed') {
          setSyncMessage(`同步失败: ${data.error}`);
          eventSource.close();
        } else if (data.status === 'stopped') {
          setSyncMessage('同步已中止');
          eventSource.close();
        }
      };

      eventSource.onerror = () => {
        eventSource.close();
      };
    } catch (e) {
      setSyncMessage('启动同步失败');
    }
  }

  async function handleStopSync() {
    if (!syncTask) return;

    try {
      await stopSync(syncTask.task_id);
      setSyncMessage('正在停止同步...');
    } catch (e) {
      setSyncMessage('停止同步失败');
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">加载中...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">控制台</h1>
        <div className="flex items-center gap-3">
          {syncTask?.status === 'running' ? (
            <button
              onClick={handleStopSync}
              className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600"
            >
              停止同步
            </button>
          ) : (
            <button
              onClick={handleStartSync}
              className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
            >
              同步收藏
            </button>
          )}
        </div>
      </div>

      {syncMessage && (
        <div className="p-3 bg-blue-50 text-blue-700 rounded-lg text-sm">
          {syncMessage}
        </div>
      )}

      {syncTask && syncTask.status === 'running' && (
        <div className="bg-white rounded-lg border p-6">
          <h2 className="text-lg font-semibold mb-4">同步进度</h2>
          <div className="space-y-3">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">当前处理：{syncTask.current_title || '准备中...'}</span>
              <span className="text-gray-500">{syncTask.processed}/{syncTask.total}</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-500 h-2 rounded-full transition-all"
                style={{ width: `${syncTask.progress}%` }}
              />
            </div>
            <div className="text-right text-sm text-gray-500">
              {syncTask.progress}%
            </div>
          </div>
        </div>
      )}

      {stats ? (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard
              title="总收藏数"
              value={stats.overview.total_videos}
              icon="📚"
            />
            <StatCard
              title="分类数"
              value={stats.overview.total_categories}
              icon="📁"
            />
            <StatCard
              title="向量索引"
              value={stats.overview.total_embeddings || 0}
              icon="🔍"
            />
            <StatCard
              title="平均质量分"
              value={stats.overview.avg_quality_score}
              icon="⭐"
            />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg border p-6">
              <h2 className="text-lg font-semibold mb-4">分类分布</h2>
              <div className="space-y-3">
                {stats.category_distribution.length === 0 ? (
                  <p className="text-gray-400 text-center py-4">暂无分类数据</p>
                ) : (
                  stats.category_distribution.map((cat) => (
                    <Link
                      key={cat.category}
                      to={`/library?category=${encodeURIComponent(cat.category)}`}
                      className="flex items-center justify-between hover:bg-gray-50 p-2 rounded"
                    >
                      <span className="text-gray-700">{cat.category}</span>
                      <div className="flex items-center gap-2">
                        <div className="w-32 bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-blue-500 h-2 rounded-full"
                            style={{ width: `${cat.percentage}%` }}
                          />
                        </div>
                        <span className="text-sm text-gray-500 w-12 text-right">
                          {cat.count}
                        </span>
                      </div>
                    </Link>
                  ))
                )}
              </div>
            </div>

            <div className="bg-white rounded-lg border p-6">
              <h2 className="text-lg font-semibold mb-4">最近同步</h2>
              <div className="space-y-3">
                {stats.recent_syncs.length === 0 ? (
                  <p className="text-gray-400 text-center py-4">暂无同步记录</p>
                ) : (
                  stats.recent_syncs.map((item) => (
                    <Link
                      key={item.id}
                      to={`/video/${item.id}`}
                      className="flex items-center justify-between hover:bg-gray-50 p-2 rounded"
                    >
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {item.title}
                        </p>
                        <p className="text-xs text-gray-500">{item.category}</p>
                      </div>
                      <span className="text-xs text-gray-400 ml-2">
                        {item.synced_at
                          ? new Date(item.synced_at).toLocaleDateString()
                          : ''}
                      </span>
                    </Link>
                  ))
                )}
              </div>
            </div>
          </div>
        </>
      ) : (
        <div className="text-center py-12">
          <p className="text-gray-500">暂无数据，请先同步收藏</p>
        </div>
      )}
    </div>
  );
}

function StatCard({ title, value, icon }: { title: string; value: number | string; icon: string }) {
  return (
    <div className="bg-white rounded-lg border p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-500">{title}</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
        </div>
        <span className="text-3xl">{icon}</span>
      </div>
    </div>
  );
}

/**
 * 抖音收藏AI知识库 - 主应用
 * 使用 Tailwind CSS 和组件化架构
 */

import { useState, useEffect, useCallback } from 'react';
import { checkHealth, getVideos, getCategories, logout } from './api/client';
import { useSync } from './hooks/useSync';
import { Layout } from './components/Layout';
import { SyncPanel } from './components/SyncPanel';
import { VideoTable } from './components/VideoTable';
import type { Video } from './types';

export default function App() {
  const [backendOk, setBackendOk] = useState<boolean | null>(null);
  const [authExists, setAuthExists] = useState(false);
  const [videos, setVideos] = useState<Video[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [loading, setLoading] = useState(true);

  // 加载视频列表（根据当前分类筛选）
  const loadVideos = useCallback(async (category?: string) => {
    try {
      const data = await getVideos(100, 0, category || undefined);
      setVideos(data.items as Video[]);
    } catch (e) {
      console.error('加载视频失败:', e);
    }
  }, []);

  // 分类切换回调
  const handleCategoryChange = useCallback((cat: string) => {
    setSelectedCategory(cat);
    loadVideos(cat || undefined);
  }, [loadVideos]);

  // 同步完成回调
  const handleSyncComplete = useCallback(() => {
    loadVideos(selectedCategory || undefined);
    // 同步后刷新分类列表
    getCategories().then(data => {
      if (data.categories.length > 0) setCategories(data.categories);
    }).catch(() => {});
  }, [loadVideos, selectedCategory]);

  // 同步状态管理
  const sync = useSync(handleSyncComplete);

  // 初始化
  useEffect(() => {
    const init = async () => {
      try {
        const health = await checkHealth();
        setBackendOk(true);
        setAuthExists(health.auth_exists);
        const [videoData, catData] = await Promise.all([
          getVideos(),
          getCategories(),
        ]);
        setVideos(videoData.items as Video[]);
        setCategories(catData.categories);
      } catch {
        setBackendOk(false);
      } finally {
        setLoading(false);
      }
    };
    init();
  }, []);

  // 退出登录
  const handleLogout = useCallback(async () => {
    try {
      const result = await logout();
      if (result.success) {
        setAuthExists(false);
      }
    } catch (e) {
      console.error('退出登录失败:', e);
    }
  }, []);

  // 加载中状态
  if (loading) {
    return (
      <Layout authExists={authExists} onLogout={handleLogout}>
        <div className="flex justify-center items-center h-64">
          <div className="text-gray-500">加载中...</div>
        </div>
      </Layout>
    );
  }

  // 后端未启动
  if (backendOk === false) {
    return (
      <Layout authExists={authExists} onLogout={handleLogout}>
        <div className="flex justify-center items-center h-64">
          <div className="bg-white rounded-lg shadow-sm border border-red-200 p-8 max-w-md text-center">
            <h1 className="text-xl font-bold text-red-600 mb-4">
              ⚠️ 后端服务未启动
            </h1>
            <p className="text-gray-600 mb-6">
              请先运行 start.bat 启动服务，或手动启动后端：
            </p>
            <code className="block bg-gray-100 rounded-md p-3 text-sm text-gray-800">
              cd backend && python run_server.py
            </code>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout authExists={authExists} onLogout={handleLogout}>
      {/* 同步控制面板 */}
      <SyncPanel
        authExists={authExists}
        syncState={sync}
        onStart={(limit) => sync.start(limit)}
        onStop={sync.stop}
      />

      {/* 视频列表 */}
      <VideoTable
        videos={videos}
        categories={['全部', ...categories]}
        selectedCategory={selectedCategory}
        onCategoryChange={handleCategoryChange}
        onVideosChange={() => loadVideos(selectedCategory || undefined)}
      />
    </Layout>
  );
}

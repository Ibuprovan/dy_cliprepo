/**
 * 布局组件
 */

import type { ReactNode } from 'react';

interface LayoutProps {
  children: ReactNode;
  authExists?: boolean;
  onLogout?: () => void;
}

export function Layout({ children, authExists, onLogout }: LayoutProps) {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* 顶部导航栏 */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 h-14 flex items-center justify-between">
          <h1 className="text-lg font-bold text-gray-900">🎬 抖音收藏AI知识库</h1>
          {authExists && onLogout && (
            <button
              onClick={onLogout}
              className="text-sm text-gray-500 hover:text-red-600 transition-colors"
            >
              退出登录
            </button>
          )}
        </div>
      </header>
      <div className="max-w-7xl mx-auto px-4 py-6">
        {children}
      </div>
    </div>
  );
}

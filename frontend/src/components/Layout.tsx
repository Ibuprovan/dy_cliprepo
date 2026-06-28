/**
 * 布局组件 — 极简设计系统
 * 全宽布局，无两侧空白
 */

import type { ReactNode } from 'react';

interface LayoutProps {
  children: ReactNode;
  authExists?: boolean;
  onLogout?: () => void;
}

export function Layout({ children, authExists, onLogout }: LayoutProps) {
  return (
    <div className="min-h-screen bg-surface-100">
      {/* 顶部导航栏 */}
      <header className="bg-surface-50 border-b border-brand-200 shadow-2xs">
        <div className="px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-brand-900 font-bold tracking-tight text-base">
              抖音收藏AI知识库
            </span>
          </div>
          {authExists && onLogout && (
            <button
              onClick={onLogout}
              className="text-xs text-ink-400 hover:text-danger transition-colors tracking-tight"
            >
              退出登录
            </button>
          )}
        </div>
      </header>
      {/* 主内容区 — 全宽 */}
      <div className="px-6 py-6">
        {children}
      </div>
    </div>
  );
}

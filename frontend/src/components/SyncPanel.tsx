/**
 * 同步控制面板组件 — 极简设计系统
 */

import { useState } from 'react';
import type { SyncState } from '../hooks/useSync';

interface SyncPanelProps {
  authExists: boolean;
  syncState: SyncState;
  onStart: (limit: number) => void;
  onStop: () => void;
}

const LIMIT_OPTIONS = [
  { label: '10 条', value: 10 },
  { label: '30 条', value: 30 },
  { label: '50 条', value: 50 },
  { label: '全部', value: 0 },
];

export function SyncPanel({ authExists, syncState, onStart, onStop }: SyncPanelProps) {
  const { status, progress, currentTitle, message } = syncState;
  const isRunning = status === 'running';
  const [limit, setLimit] = useState(10);

  return (
    <div className="bg-surface-50 rounded-lg border border-brand-200 p-6 mb-6 shadow-sm">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-sm font-semibold text-ink-900 tracking-tight uppercase">
          同步收藏
        </h2>
        <div className="flex items-center gap-3">
          <select
            disabled={isRunning}
            value={limit}
            onChange={(e) => setLimit(Number(e.target.value))}
            className="text-xs border border-brand-200 rounded-md px-3 py-2 bg-surface-50 text-ink-700 disabled:opacity-50 tracking-tight focus:outline-none focus:ring-1 focus:ring-brand-900"
          >
            {LIMIT_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
          <button
            onClick={isRunning ? onStop : () => onStart(limit)}
            disabled={!authExists && !isRunning}
            className={`px-5 py-2 rounded-md font-medium text-xs tracking-tight transition-colors ${
              isRunning
                ? 'bg-danger text-white hover:bg-danger-text'
                : authExists
                  ? 'bg-brand-900 text-brand-50 hover:bg-brand-800'
                  : 'bg-brand-100 text-ink-400 cursor-not-allowed'
            }`}
          >
            {isRunning ? '停止同步' : '开始同步'}
          </button>
        </div>
      </div>

      {/* 登录提示 */}
      {!authExists && !isRunning && (
        <div className="bg-warning-subtle border border-warning-border rounded-md p-4 mb-4">
          <p className="text-warning-text text-xs tracking-tight">
            请先运行 <code className="bg-brand-100 px-1.5 py-0.5 rounded text-xs">backend/login_manual.py</code> 完成抖音登录
          </p>
        </div>
      )}

      {/* 同步消息 */}
      {message && (
        <div className={`rounded-md p-4 mb-4 text-xs tracking-tight ${
          message.includes('完成')
            ? 'bg-success-subtle text-success-text border border-success-border'
            : message.includes('失败') || message.includes('错误')
              ? 'bg-danger-subtle text-danger-text border border-danger-border'
              : 'bg-brand-100 text-ink-600 border border-brand-200'
        }`}>
          {message}
        </div>
      )}

      {/* 进度条 */}
      {isRunning && (
        <div>
          <div className="flex justify-between text-xs text-ink-400 mb-2 tracking-tight">
            <span>当前处理：{currentTitle || '准备中...'}</span>
            <span>{progress}%</span>
          </div>
          <div className="w-full bg-brand-100 rounded-full h-1.5">
            <div
              className="bg-brand-900 h-1.5 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}
    </div>
  );
}

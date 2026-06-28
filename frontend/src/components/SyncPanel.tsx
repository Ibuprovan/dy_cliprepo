/**
 * 同步控制面板组件
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
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold text-gray-900">同步收藏</h2>
        <div className="flex items-center gap-3">
          {/* 数量选择 */}
          <select
            disabled={isRunning}
            value={limit}
            onChange={(e) => setLimit(Number(e.target.value))}
            className="text-sm border border-gray-300 rounded-md px-3 py-2 bg-white text-gray-700 disabled:opacity-50"
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
            className={`px-6 py-2 rounded-md font-medium text-sm transition-colors ${
              isRunning
                ? 'bg-red-500 hover:bg-red-600 text-white'
                : authExists
                  ? 'bg-blue-500 hover:bg-blue-600 text-white'
                  : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
          >
            {isRunning ? '停止同步' : '开始同步'}
          </button>
        </div>
      </div>

      {/* 登录提示 */}
      {!authExists && !isRunning && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4 mb-4">
          <p className="text-yellow-800 text-sm">
            请先运行 <code className="bg-yellow-100 px-1 py-0.5 rounded">backend/login_manual.py</code> 完成抖音登录
          </p>
        </div>
      )}

      {/* 同步消息 */}
      {message && (
        <div className={`rounded-md p-4 mb-4 text-sm ${
          message.includes('完成')
            ? 'bg-green-50 text-green-800'
            : message.includes('失败') || message.includes('错误')
              ? 'bg-red-50 text-red-800'
              : 'bg-blue-50 text-blue-800'
        }`}>
          {message}
        </div>
      )}

      {/* 进度条 */}
      {isRunning && (
        <div>
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>当前处理：{currentTitle || '准备中...'}</span>
            <span>{progress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}
    </div>
  );
}

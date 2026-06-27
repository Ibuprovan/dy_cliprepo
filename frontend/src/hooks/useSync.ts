/**
 * 同步任务 Hook
 * 管理 SSE 连接和同步状态
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import { startSync, stopSync, createSyncSSE } from '../api/client';

export interface SyncState {
  taskId: string | null;
  status: 'idle' | 'running' | 'completed' | 'failed' | 'cancelled';
  progress: number;
  currentTitle: string;
  error: string | null;
  message: string;
}

const INITIAL_STATE: SyncState = {
  taskId: null,
  status: 'idle',
  progress: 0,
  currentTitle: '',
  error: null,
  message: '',
};

export function useSync(onComplete?: () => void) {
  const [state, setState] = useState<SyncState>(INITIAL_STATE);
  const eventSourceRef = useRef<EventSource | null>(null);

  // 清理 SSE 连接
  const cleanup = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
  }, []);

  // 组件卸载时清理
  useEffect(() => {
    return cleanup;
  }, [cleanup]);

  // 启动同步
  const start = useCallback(async (limit = 10) => {
    try {
      setState(prev => ({ ...prev, message: '正在启动同步...', error: null }));

      const result = await startSync(limit);

      setState(prev => ({
        ...prev,
        taskId: result.task_id,
        status: 'running',
        message: '同步任务已启动',
      }));

      // 创建 SSE 连接（修复 #7: 增加断连回调）
      const eventSource = createSyncSSE(
        result.task_id,
        (data: unknown) => {
        const taskData = data as {
          type?: string;
          status: string;
          progress: number;
          current_title: string;
          error: string | null;
        };

        // 处理完成消息（修复 #9: 正确映射 cancelled 状态）
        if (taskData.type === 'done') {
          const statusMap: Record<string, SyncState['status']> = {
            'completed': 'completed',
            'failed': 'failed',
            'cancelled': 'cancelled',
          };
          const newStatus = statusMap[taskData.status] || 'failed';
          const messageMap: Record<string, string> = {
            'completed': '同步完成！',
            'failed': '同步失败',
            'cancelled': '同步已停止',
          };
          setState(prev => ({
            ...prev,
            status: newStatus,
            progress: 100,
            message: messageMap[taskData.status] || `同步${taskData.status}`,
          }));
          cleanup();
          if (onComplete) onComplete();
          return;
        }

        // 更新状态
        setState(prev => ({
          ...prev,
          progress: taskData.progress,
          currentTitle: taskData.current_title,
          error: taskData.error,
        }));

        // 检查是否完成
        if (taskData.status === 'completed' || taskData.status === 'failed') {
          setState(prev => ({
            ...prev,
            status: taskData.status as SyncState['status'],
            message: taskData.status === 'completed' ? '同步完成！' : `同步失败: ${taskData.error}`,
          }));
          cleanup();
          if (onComplete) onComplete();
        }
      },
      // 修复 #7: SSE 断连时通知用户
      () => {
        setState(prev => ({
          ...prev,
          status: 'failed',
          message: '连接中断，请重试',
        }));
      }
      );

      eventSourceRef.current = eventSource;
    } catch (e: unknown) {
      const error = e as Error;
      setState(prev => ({
        ...prev,
        status: 'failed',
        message: `启动失败: ${error.message}`,
      }));
    }
  }, [cleanup, onComplete]);

  // 停止同步
  const stop = useCallback(async () => {
    try {
      await stopSync(state.taskId || undefined);
      setState(prev => ({
        ...prev,
        status: 'cancelled',
        message: '同步已停止',
      }));
      cleanup();
    } catch (e: unknown) {
      const error = e as Error;
      setState(prev => ({
        ...prev,
        message: `停止失败: ${error.message}`,
      }));
    }
  }, [state.taskId, cleanup]);

  return {
    ...state,
    start,
    stop,
    isRunning: state.status === 'running',
  };
}

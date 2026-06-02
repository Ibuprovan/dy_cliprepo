import { useEffect, useState } from 'react';
import { checkAuth, login, confirmLogin, logout } from '../api/client';
import type { AuthStatus } from '../types';

export default function Settings() {
  const [auth, setAuth] = useState<AuthStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');

  useEffect(() => {
    loadAuth();
  }, []);

  async function loadAuth() {
    try {
      const data = await checkAuth();
      setAuth(data);
    } catch (e) {
      console.error('Failed to check auth:', e);
    } finally {
      setLoading(false);
    }
  }

  async function handleLogin() {
    try {
      const result = await login();
      setMessage(result.message);
      if (result.status === 'waiting') {
        setMessage(result.message + ' 登录完成后请点击"确认登录"按钮。');
      }
    } catch (e) {
      setMessage('登录失败');
    }
  }

  async function handleConfirm() {
    try {
      const result = await confirmLogin();
      setMessage(result.message);
      loadAuth();
    } catch (e) {
      setMessage('确认失败');
    }
  }

  async function handleLogout() {
    try {
      const result = await logout();
      setMessage(result.message);
      loadAuth();
    } catch (e) {
      setMessage('退出失败');
    }
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">设置</h1>

      <div className="bg-white rounded-lg border p-6">
        <h2 className="text-lg font-semibold mb-4">抖音登录</h2>

        {loading ? (
          <p className="text-gray-500">加载中...</p>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <div
                className={`w-3 h-3 rounded-full ${auth?.logged_in ? 'bg-green-500' : 'bg-gray-300'}`}
              />
              <span className="text-gray-700">
                {auth?.logged_in ? '已登录' : '未登录'}
              </span>
            </div>

            <div className="flex gap-3">
              {!auth?.logged_in && (
                <button
                  onClick={handleLogin}
                  className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
                >
                  扫码登录
                </button>
              )}
              {auth?.logged_in && (
                <>
                  <button
                    onClick={handleLogin}
                    className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                  >
                    重新登录
                  </button>
                  <button
                    onClick={handleLogout}
                    className="px-4 py-2 border border-red-300 text-red-600 rounded-lg hover:bg-red-50"
                  >
                    退出登录
                  </button>
                </>
              )}
            </div>

            {message && (
              <div className="p-3 bg-blue-50 text-blue-700 rounded-lg text-sm">
                {message}
              </div>
            )}

            <button
              onClick={handleConfirm}
              className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600"
            >
              确认登录
            </button>
          </div>
        )}
      </div>

      <div className="bg-white rounded-lg border p-6">
        <h2 className="text-lg font-semibold mb-4">AI 模型配置</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm text-gray-600 mb-1">AI Provider</label>
            <p className="text-sm text-gray-500">
              在后端 .env 文件中配置 AI_PROVIDER（ollama / openai / deepseek）
            </p>
          </div>
          <div>
            <label className="block text-sm text-gray-600 mb-1">Ollama 模型</label>
            <p className="text-sm text-gray-500">
              在后端 .env 文件中配置 OLLAMA_MODEL（默认 qwen2.5:14b）
            </p>
          </div>
          <div>
            <label className="block text-sm text-gray-600 mb-1">API Key</label>
            <p className="text-sm text-gray-500">
              在后端 .env 文件中配置 OPENAI_API_KEY 或 DEEPSEEK_API_KEY
            </p>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg border p-6">
        <h2 className="text-lg font-semibold mb-4">数据管理</h2>
        <p className="text-sm text-gray-500 mb-4">
          数据导出和清空功能将在后续版本中提供。
        </p>
      </div>
    </div>
  );
}

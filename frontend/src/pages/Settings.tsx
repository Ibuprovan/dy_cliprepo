import { useEffect, useState } from 'react';
import { checkAuth, login, confirmLogin, logout } from '../api/client';
import type { AuthStatus } from '../types';

interface ConfigStatus {
  ai_provider: string;
  has_api_key: boolean;
  api_key_preview: string | null;
}

export default function Settings() {
  const [auth, setAuth] = useState<AuthStatus | null>(null);
  const [config, setConfig] = useState<ConfigStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');
  const [loginStep, setLoginStep] = useState<'idle' | 'waiting' | 'done'>('idle');

  useEffect(() => {
    loadAuth();
    loadConfig();
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

  async function loadConfig() {
    try {
      const res = await fetch('/api/stats/config');
      const data = await res.json();
      setConfig(data);
    } catch (e) {
      console.error('Failed to load config:', e);
    }
  }

  async function handleLogin() {
    try {
      setMessage('正在打开浏览器...');
      const result = await login();
      if (result.status === 'waiting') {
        setMessage('浏览器已打开，请使用抖音APP扫码登录，然后点击下方"确认登录"按钮');
        setLoginStep('waiting');
      } else if (result.status === 'error') {
        setMessage(result.message);
      } else {
        setMessage(result.message);
      }
    } catch (e: any) {
      setMessage('登录失败: ' + (e.message || '未知错误'));
    }
  }

  async function handleConfirm() {
    try {
      setMessage('正在保存登录态...');
      const result = await confirmLogin();
      setMessage(result.message);
      if (result.status === 'success') {
        setLoginStep('done');
        loadAuth();
      }
    } catch (e: any) {
      setMessage('确认失败: ' + (e.message || '未知错误'));
    }
  }

  async function handleLogout() {
    try {
      const result = await logout();
      setMessage(result.message);
      setLoginStep('idle');
      loadAuth();
    } catch (e) {
      setMessage('退出失败');
    }
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">设置</h1>

      <div className="bg-white rounded-lg border p-6">
        <h2 className="text-lg font-semibold mb-4">AI 模型配置状态</h2>
        {config ? (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-gray-600">AI Provider</span>
              <span className="font-medium">{config.ai_provider}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-600">API Key 状态</span>
              <span className={`font-medium ${config.has_api_key ? 'text-green-600' : 'text-red-600'}`}>
                {config.has_api_key ? '已配置' : '未配置'}
              </span>
            </div>
            {config.api_key_preview && (
              <div className="flex items-center justify-between">
                <span className="text-gray-600">API Key</span>
                <span className="font-mono text-sm">{config.api_key_preview}</span>
              </div>
            )}
          </div>
        ) : (
          <p className="text-gray-500">加载中...</p>
        )}
      </div>

      <div className="bg-white rounded-lg border p-6">
        <h2 className="text-lg font-semibold mb-4">抖音登录</h2>

        {loading ? (
          <p className="text-gray-500">加载中...</p>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <div className={`w-3 h-3 rounded-full ${auth?.logged_in ? 'bg-green-500' : 'bg-gray-300'}`} />
              <span className="text-gray-700">
                {auth?.logged_in ? '已登录' : '未登录'}
              </span>
            </div>

            {auth?.logged_in ? (
              <div className="flex gap-3">
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
              </div>
            ) : (
              <div className="space-y-3">
                <div className="flex gap-3">
                  <button
                    onClick={handleLogin}
                    disabled={loginStep === 'waiting'}
                    className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {loginStep === 'waiting' ? '等待扫码...' : '扫码登录'}
                  </button>
                  {loginStep === 'waiting' && (
                    <button
                      onClick={handleConfirm}
                      className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600"
                    >
                      确认登录
                    </button>
                  )}
                </div>

                {loginStep === 'waiting' && (
                  <div className="p-3 bg-blue-50 text-blue-700 rounded-lg text-sm">
                    <p className="font-semibold mb-1">请按以下步骤操作：</p>
                    <ol className="list-decimal list-inside space-y-1">
                      <li>在弹出的浏览器窗口中，使用抖音APP扫码登录</li>
                      <li>登录成功后，回到此页面点击"确认登录"按钮</li>
                    </ol>
                  </div>
                )}
              </div>
            )}

            {message && (
              <div className={`p-3 rounded-lg text-sm ${
                message.includes('成功') || message.includes('已保存')
                  ? 'bg-green-50 text-green-700'
                  : message.includes('失败') || message.includes('错误')
                  ? 'bg-red-50 text-red-700'
                  : 'bg-blue-50 text-blue-700'
              }`}>
                {message}
              </div>
            )}
          </div>
        )}
      </div>

      <div className="bg-white rounded-lg border p-6">
        <h2 className="text-lg font-semibold mb-4">配置说明</h2>
        <div className="space-y-2 text-sm text-gray-600">
          <p>配置文件位置：<code className="bg-gray-100 px-1 rounded">backend/.env</code></p>
          <p>修改配置后需要重启后端服务才能生效。</p>
        </div>
      </div>
    </div>
  );
}

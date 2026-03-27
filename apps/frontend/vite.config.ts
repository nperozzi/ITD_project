import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, '.', '');
  const backendUrl = env.VITE_BACKEND_URL;
  const proxyTarget = env.VITE_PROXY_TARGET || 'http://localhost:5000';
  const useProxy = !backendUrl;

  return {
    plugins: [react()],
    server: {
      port: 4200,
      host: '0.0.0.0',
      proxy: useProxy
        ? {
            '/api': {
              target: proxyTarget,
              changeOrigin: true,
            },
            '/battery': {
              target: proxyTarget,
              changeOrigin: true,
            },
            '/socket.io': {
              target: proxyTarget,
              changeOrigin: true,
              ws: true,
            },
          }
        : undefined,
    },
  };
});

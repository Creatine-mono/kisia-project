/** @type {import('next').NextConfig} */
const nextConfig = {
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
  output: 'standalone',

  // 개발 환경에서 localhost와 127.0.0.1 간 cross-origin 요청 허용
  experimental: {
    allowedDevOrigins: ['127.0.0.1', 'localhost'],
  },
}

export default nextConfig

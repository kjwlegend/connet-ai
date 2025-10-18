import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  experimental: {},
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
      },
    ],
  },

}

export default nextConfig

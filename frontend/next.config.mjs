/** @type {import('next').NextConfig} */
const API_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

const nextConfig = {
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          { key: "X-Content-Type-Options",  value: "nosniff" },
          { key: "X-Frame-Options",         value: "DENY" },
          { key: "X-XSS-Protection",        value: "1; mode=block" },
          { key: "Referrer-Policy",          value: "strict-origin-when-cross-origin" },
          { key: "Permissions-Policy",       value: "camera=(), microphone=(), geolocation=()" },
          {
            key: "Content-Security-Policy",
            value: [
              "default-src 'self'",
              "script-src 'self' 'unsafe-inline' 'unsafe-eval'",
              "style-src 'self' 'unsafe-inline'",
              "img-src 'self' data: blob:",
              "font-src 'self' https://fonts.gstatic.com",
              `connect-src 'self' ${API_URL}`,
              "frame-ancestors 'none'",
            ].join("; "),
          },
        ],
      },
      {
        // Prevent indexing of app pages (auth, dashboard, documents, sample)
        source: "/(dashboard|documents|login|register|sample)(.*)",
        headers: [{ key: "X-Robots-Tag", value: "noindex, nofollow" }],
      },
    ];
  },
};

export default nextConfig;

import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  reactStrictMode: true,
  // Phones that ask for the touch icon at its old fixed paths (an iPhone did, in the deploy logs)
  // get the one of src/app/apple-icon.png, as those that read its <link> tag
  rewrites() {
    return [
      { source: "/apple-touch-icon.png", destination: "/apple-icon.png" },
      { source: "/apple-touch-icon-precomposed.png", destination: "/apple-icon.png" },
    ];
  },
};

export default nextConfig;

/**
 * Run `build` or `dev` with `SKIP_ENV_VALIDATION` to skip env validation. This is especially useful
 * for Docker builds.
 */
import "./src/env.js";

/** @type {import("next").NextConfig} */
const config = {
  allowedDevOrigins: ["*"],
  async redirects() {
    return [
      {
        source: "/login",
        destination: "/sign-in",
        permanent: true,
      },
      {
        source: "/log-in",
        destination: "/sign-in",
        permanent: true,
      },
      {
        source: "/signin",
        destination: "/sign-in",
        permanent: true,
      },
      {
        source: "/register",
        destination: "/sign-up",
        permanent: true,
      },
      {
        source: "/signup",
        destination: "/sign-up",
        permanent: true,
      },
      {
        source: "/create-account",
        destination: "/sign-up",
        permanent: true,
      },
      {
        source: "/signout",
        destination: "/sign-out",
        permanent: true,
      },
      {
        source: "/logout",
        destination: "/sign-out",
        permanent: true,
      },
      {
        source: "/log-out",
        destination: "/sign-out",
        permanent: true,
      },
    ];
  },
};

export default config;

"use client";

import { useEffect, useState, useMemo } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { motion } from "framer-motion";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useTranslations } from "@/lib/i18n/client";
import { useAuth } from "@/store";
import { useAuthOAuth } from "@/hooks/business/auth";
import { CheckCircle, AlertCircle, ArrowLeft } from "lucide-react";
import Link from "next/link";

/**
 * OAuth Callback Page
 *
 * Handles OAuth authentication callbacks from Google and GitHub.
 * Processes the authorization code and completes the authentication flow.
 */
export default function OAuthCallbackPage() {
  const t = useTranslations();
  const router = useRouter();
  const searchParams = useSearchParams();
  const { ui } = useAuth();
  const { handleOAuthCallback } = useAuthOAuth();
  const isLoading = ui.isLoading;

  const [status, setStatus] = useState<"loading" | "success" | "error">(
    "loading"
  );
  const [error, setError] = useState<string | null>(null);
  const [isNewUser, setIsNewUser] = useState(false);
  const [provider, setProvider] = useState<"google" | "github" | null>(null);

  // Fixed positions for background dots to avoid hydration mismatch
  const backgroundDots = useMemo(() => [
    { left: 15, top: 20, duration: 4.2, delay: 0.8 },
    { left: 78, top: 15, duration: 3.7, delay: 1.3 },
    { left: 23, top: 65, duration: 4.8, delay: 0.2 },
    { left: 67, top: 45, duration: 3.4, delay: 1.9 },
    { left: 89, top: 75, duration: 4.5, delay: 0.6 },
    { left: 34, top: 35, duration: 3.9, delay: 1.5 },
    { left: 56, top: 82, duration: 4.1, delay: 0.4 },
    { left: 18, top: 48, duration: 3.6, delay: 1.7 },
    { left: 82, top: 22, duration: 4.3, delay: 0.1 },
    { left: 45, top: 78, duration: 3.8, delay: 1.2 },
  ], []);

  /**
   * Process OAuth callback
   * Extracts parameters from URL and completes authentication
   */
  useEffect(() => {
    const processCallback = async () => {
      try {
        // Extract OAuth parameters from URL
        const code = searchParams.get("code");
        const state = searchParams.get("state");
        const providerParam = searchParams.get("provider");
        const error = searchParams.get("error");
        const errorDescription = searchParams.get("error_description");

        // Check for OAuth errors
        if (error) {
          console.error("OAuth error:", error, errorDescription);
          setError(errorDescription || error || "Authentication failed");
          setStatus("error");
          return;
        }

        // Validate required parameters
        if (!code || !state || !providerParam) {
          console.error("Missing required OAuth parameters:", {
            code: !!code,
            state: !!state,
            provider: !!providerParam,
          });
          setError(
            "Invalid authentication response. Missing required parameters."
          );
          setStatus("error");
          return;
        }

        // Validate provider
        if (providerParam !== "google" && providerParam !== "github") {
          setError(`Unsupported authentication provider: ${providerParam}`);
          setStatus("error");
          return;
        }

        setProvider(providerParam);

        // Complete OAuth authentication
        const redirectUri = `${window.location.origin}/auth/callback`;
        const result = await handleOAuthCallback(
          providerParam,
          code,
          state,
          redirectUri
        );

        setIsNewUser(result.isNewUser);
        setStatus("success");

        // Redirect to dashboard after a brief success display
        setTimeout(() => {
          router.push("/dashboard");
        }, 2000);
      } catch (err) {
        console.error("OAuth callback processing failed:", err);
        setError(err instanceof Error ? err.message : "Authentication failed");
        setStatus("error");
      }
    };

    processCallback();
  }, [searchParams, handleOAuthCallback, router]);

  /**
   * Get provider display name and icon
   */
  const getProviderInfo = () => {
    switch (provider) {
      case "google":
        return {
          name: "Google",
          icon: (
            <svg className="w-6 h-6" viewBox="0 0 24 24">
              <path
                fill="#4285f4"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="#34a853"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="#fbbc05"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
              />
              <path
                fill="#ea4335"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
              />
            </svg>
          ),
        };
      case "github":
        return {
          name: "GitHub",
          icon: (
            <svg className="w-6 h-6" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
            </svg>
          ),
        };
      default:
        return { name: "OAuth Provider", icon: null };
    }
  };

  const providerInfo = getProviderInfo();

  return (
    <div className="h-screen w-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 overflow-hidden fixed inset-0">
      {/* Background Network Animation Layer */}
      <div className="fixed inset-0 z-0 opacity-20">
        {backgroundDots.map((dot, i) => (
          <motion.div
            key={i}
            className={`absolute w-1 h-1 rounded-full ${
              status === "success"
                ? "bg-green-400"
                : status === "error"
                ? "bg-red-400"
                : "bg-blue-400"
            }`}
            style={{
              left: `${dot.left}%`,
              top: `${dot.top}%`,
            }}
            animate={{
              opacity: [0.2, 0.8, 0.2],
              scale: [0.8, 1.3, 0.8],
            }}
            transition={{
              duration: dot.duration,
              repeat: Infinity,
              delay: dot.delay,
            }}
          />
        ))}
      </div>

      {/* Main Content */}
      <div className="relative z-10 h-full flex items-center justify-center p-6">
        <motion.div
          className="w-full max-w-md text-center"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          {/* Status Icon */}
          <motion.div
            className="flex justify-center mb-8"
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6, delay: 0.1 }}
          >
            <div
              className={`w-20 h-20 rounded-full flex items-center justify-center ${
                status === "success"
                  ? "bg-green-600"
                  : status === "error"
                  ? "bg-red-600"
                  : "bg-blue-600"
              }`}
            >
              {status === "loading" && (
                <div className="w-8 h-8 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              )}
              {status === "success" && (
                <CheckCircle className="w-12 h-12 text-white" />
              )}
              {status === "error" && (
                <AlertCircle className="w-12 h-12 text-white" />
              )}
            </div>
          </motion.div>

          {/* Logo */}
          <motion.div
            className="flex justify-center mb-6"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <img
              src="/static/logo-light.png"
              alt="Connet.AI"
              className="w-16 h-16"
            />
          </motion.div>

          {/* Content */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
          >
            <Card className="bg-slate-800/80 backdrop-blur-md border-slate-700/50 shadow-2xl">
              <CardContent className="p-8">
                {status === "loading" && (
                  <div className="space-y-4">
                    <h1 className="text-2xl font-bold text-white">
                      Completing Authentication
                    </h1>
                    {provider && (
                      <div className="flex items-center justify-center space-x-3 text-slate-300">
                        {providerInfo.icon}
                        <span>Authenticating with {providerInfo.name}...</span>
                      </div>
                    )}
                    <p className="text-slate-400">
                      Please wait while we complete your authentication.
                    </p>
                  </div>
                )}

                {status === "success" && (
                  <div className="space-y-4">
                    <h1 className="text-2xl font-bold text-white">
                      {isNewUser ? "Welcome to Connet.AI!" : "Welcome Back!"}
                    </h1>
                    {provider && (
                      <div className="flex items-center justify-center space-x-3 text-slate-300">
                        {providerInfo.icon}
                        <span>
                          Successfully authenticated with {providerInfo.name}
                        </span>
                      </div>
                    )}
                    <div className="p-4 text-sm text-green-300 bg-green-900/30 rounded-xl border border-green-700/30">
                      {isNewUser
                        ? "Your account has been created successfully. Redirecting to your dashboard..."
                        : "You have been logged in successfully. Redirecting to your dashboard..."}
                    </div>
                  </div>
                )}

                {status === "error" && (
                  <div className="space-y-6">
                    <h1 className="text-2xl font-bold text-white">
                      Authentication Failed
                    </h1>
                    {provider && (
                      <div className="flex items-center justify-center space-x-3 text-slate-300">
                        {providerInfo.icon}
                        <span>
                          Failed to authenticate with {providerInfo.name}
                        </span>
                      </div>
                    )}
                    <div className="p-4 text-sm text-red-300 bg-red-900/30 rounded-xl border border-red-700/30">
                      {error ||
                        "An error occurred during authentication. Please try again."}
                    </div>

                    <div className="space-y-3">
                      <Link href="/login">
                        <Button className="w-full h-12 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-semibold shadow-lg hover:shadow-xl transition-all duration-300">
                          <ArrowLeft className="w-4 h-4 mr-2" />
                          Back to Login
                        </Button>
                      </Link>

                      <Button
                        variant="outline"
                        className="w-full h-12 rounded-xl bg-slate-700/50 border-slate-600 text-slate-200 hover:bg-slate-600/50 hover:text-white"
                        onClick={() => window.location.reload()}
                      >
                        Try Again
                      </Button>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>

          {/* Footer */}
          <motion.div
            className="text-center mt-8 text-slate-400 text-sm"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.5 }}
          >
            © 2024 Connet.AI. Connecting the future, one interaction at a time.
          </motion.div>
        </motion.div>
      </div>
    </div>
  );
}

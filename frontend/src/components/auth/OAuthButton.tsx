"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Github } from "lucide-react";
import useStore from "@/store";

interface OAuthButtonProps {
  provider: "google" | "github";
  variant?: "login" | "register";
  className?: string;
  disabled?: boolean;
}

/**
 * OAuth Login Button Component
 *
 * Renders a styled OAuth button for Google or GitHub authentication.
 * Handles the OAuth flow initiation and loading states.
 */
export function OAuthButton({
  provider,
  variant = "login",
  className = "",
  disabled = false,
}: OAuthButtonProps) {
  const { loginWithOAuth, isLoading } = useStore();
  const [isLocalLoading, setIsLocalLoading] = useState(false);

  /**
   * Handle OAuth button click
   * Initiates the OAuth flow by redirecting to the provider's authorization page
   */
  const handleOAuthLogin = async () => {
    try {
      setIsLocalLoading(true);
      await loginWithOAuth(provider);
    } catch (error) {
      console.error(`${provider} OAuth failed:`, error);
      setIsLocalLoading(false);
    }
  };

  /**
   * Get provider-specific styling and icons
   */
  const getProviderConfig = () => {
    switch (provider) {
      case "google":
        return {
          icon: (
            <svg className="w-5 h-5" viewBox="0 0 24 24">
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
          label:
            variant === "login"
              ? "Continue with Google"
              : "Sign up with Google",
          bgColor: "bg-white hover:bg-gray-50",
          textColor: "text-gray-700",
          borderColor: "border-gray-300",
        };
      case "github":
        return {
          icon: <Github className="w-5 h-5" />,
          label:
            variant === "login"
              ? "Continue with GitHub"
              : "Sign up with GitHub",
          bgColor: "bg-gray-900 hover:bg-gray-800",
          textColor: "text-white",
          borderColor: "border-gray-700",
        };
      default:
        return {
          icon: null,
          label: "Continue",
          bgColor: "bg-gray-500",
          textColor: "text-white",
          borderColor: "border-gray-500",
        };
    }
  };

  const config = getProviderConfig();
  const isButtonLoading = isLoading || isLocalLoading;

  return (
    <motion.div
      whileHover={{ scale: isButtonLoading ? 1 : 1.02 }}
      whileTap={{ scale: isButtonLoading ? 1 : 0.98 }}
      transition={{ duration: 0.1 }}
    >
      <Button
        type="button"
        variant="outline"
        onClick={handleOAuthLogin}
        disabled={disabled || isButtonLoading}
        className={`
          w-full h-12 rounded-xl font-semibold transition-all duration-300 
          ${config.bgColor} ${config.textColor} ${config.borderColor}
          disabled:opacity-50 disabled:cursor-not-allowed
          focus:ring-4 focus:ring-opacity-20
          ${
            provider === "google"
              ? "focus:ring-blue-500"
              : "focus:ring-gray-500"
          }
          ${className}
        `}
      >
        {isButtonLoading ? (
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
            <span>Connecting...</span>
          </div>
        ) : (
          <div className="flex items-center justify-center space-x-3">
            {config.icon}
            <span>{config.label}</span>
          </div>
        )}
      </Button>
    </motion.div>
  );
}

/**
 * OAuth Buttons Group Component
 *
 * Renders a group of OAuth provider buttons with divider
 */
interface OAuthButtonsGroupProps {
  variant?: "login" | "register";
  className?: string;
  disabled?: boolean;
}

export function OAuthButtonsGroup({
  variant = "login",
  className = "",
  disabled = false,
}: OAuthButtonsGroupProps) {
  return (
    <div className={`space-y-3 ${className}`}>
      {/* OAuth Buttons */}
      <div className="grid grid-cols-1 gap-3">
        <OAuthButton provider="google" variant={variant} disabled={disabled} />
        <OAuthButton provider="github" variant={variant} disabled={disabled} />
      </div>

      {/* Divider with "or" text */}
      <div className="relative flex items-center my-6">
        <div className="flex-grow border-t border-slate-600/50"></div>
        <span className="flex-shrink mx-4 text-sm text-slate-400 bg-slate-800 px-2">
          or
        </span>
        <div className="flex-grow border-t border-slate-600/50"></div>
      </div>
    </div>
  );
}

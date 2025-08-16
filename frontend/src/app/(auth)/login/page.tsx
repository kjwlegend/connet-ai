"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { useTranslations } from "@/lib/i18n/client";
import useStore from "@/store";
import {
  LoginFormData,
  validateLoginForm,
  ValidationResult,
} from "@/lib/utils/validation";
import { cn } from "@/lib/utils/cn";
import { LanguageToggle } from "@/components/ui/LanguageToggle";
import { OAuthButtonsGroup } from "@/components/auth/OAuthButton";

function LoginForm() {
  const t = useTranslations();
  const router = useRouter();
  const { loginWithCredentials, isLoading, error } = useStore();

  const [formData, setFormData] = useState<LoginFormData>({
    email: "",
    password: "",
    rememberMe: false,
  });

  const [fieldErrors, setFieldErrors] = useState<
    Record<string, ValidationResult>
  >({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});

  const handleInputChange = (
    field: keyof LoginFormData,
    value: string | boolean
  ) => {
    setFormData((prev) => ({ ...prev, [field]: value }));

    // Clear field error when user starts typing
    if (fieldErrors[field] && !fieldErrors[field].isValid) {
      setFieldErrors((prev) => ({ ...prev, [field]: { isValid: true } }));
    }
  };

  const handleBlur = (field: keyof LoginFormData) => {
    setTouched((prev) => ({ ...prev, [field]: true }));

    // Validate single field on blur
    const validation = validateLoginForm(formData);
    if (validation[field]) {
      setFieldErrors((prev) => ({ ...prev, [field]: validation[field] }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Mark all fields as touched
    setTouched({
      email: true,
      password: true,
    });

    // Validate form
    const validation = validateLoginForm(formData);
    setFieldErrors(validation);

    // Check if form is valid
    const isFormValid = Object.values(validation).every(
      (result) => result.isValid
    );

    if (!isFormValid) {
      return;
    }

    try {
      await loginWithCredentials(
        formData.email,
        formData.password,
        formData.rememberMe
      );
      console.log("Login successful, redirecting to dashboard");
      router.push("/dashboard");
    } catch (err) {
      // Error is handled by the store and displayed via error state
    }
  };

  return (
    <div className="h-screen w-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 overflow-hidden fixed inset-0">
      {/* Background Network Animation Layer */}
      <div className="fixed inset-0 z-0 opacity-20">
        {/* Floating network dots */}
        {[...Array(20)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-1 h-1 bg-blue-400 rounded-full"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
            animate={{
              opacity: [0.2, 0.8, 0.2],
              scale: [0.8, 1.3, 0.8],
            }}
            transition={{
              duration: 3 + Math.random() * 2,
              repeat: Infinity,
              delay: Math.random() * 2,
            }}
          />
        ))}
      </div>

      {/* Top Navigation */}
      <div className="absolute top-6 right-6 z-20">
        <LanguageToggle
          className="text-slate-300 hover:text-white"
          variant="ghost"
        />
      </div>

      {/* Main Content */}
      <div className="relative z-10 h-full flex items-center justify-center p-6">
        <motion.div
          className="w-full max-w-md"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          {/* Logo and Branding */}
          <motion.div
            className="text-center mb-8"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6, delay: 0.1 }}
          >
            <div className="flex justify-center mb-6">
              <img
                src="/static/logo-light-vertical.png"
                alt="Connet.AI"
                className="w-48"
              />
            </div>
            <h1 className="text-4xl font-bold text-white mb-2">Welcome Back</h1>
            <p className="text-slate-300 text-lg">
              Sign in to your AI collaboration hub
            </p>
          </motion.div>

          {/* Login Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <Card className="bg-slate-800/80 backdrop-blur-md border-slate-700/50 shadow-2xl">
              <CardContent className="p-8">
                {error && (
                  <motion.div
                    className="p-4 text-sm text-red-300 bg-red-900/30 rounded-xl border border-red-700/30 mb-6"
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                  >
                    {error}
                  </motion.div>
                )}

                {/* OAuth Login Buttons */}
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.4, delay: 0.1 }}
                >
                  <OAuthButtonsGroup variant="login" disabled={isLoading} />
                </motion.div>

                <form onSubmit={handleSubmit} className="space-y-6">
                  <div className="space-y-4">
                    <div className="space-y-2">
                      <Label
                        htmlFor="email"
                        className="text-sm font-medium text-slate-200"
                      >
                        {t("auth.login.emailLabel")}
                      </Label>
                      <Input
                        id="email"
                        type="email"
                        placeholder={t("auth.login.emailPlaceholder")}
                        value={formData.email}
                        onChange={(e) =>
                          handleInputChange("email", e.target.value)
                        }
                        onBlur={() => handleBlur("email")}
                        className={cn(
                          "h-12 rounded-xl bg-slate-900/50 border-slate-600/50 text-white placeholder:text-slate-400",
                          "focus:border-blue-500/50 focus:ring-4 focus:ring-blue-500/20",
                          "hover:border-slate-500/70 transition-all duration-200",
                          touched.email &&
                            fieldErrors.email &&
                            !fieldErrors.email.isValid &&
                            "border-red-500/50 focus:border-red-500/50 focus:ring-red-500/20"
                        )}
                        disabled={isLoading}
                      />
                      {touched.email &&
                        fieldErrors.email &&
                        !fieldErrors.email.isValid && (
                          <p className="text-sm text-red-400">
                            {t(fieldErrors.email.error!)}
                          </p>
                        )}
                    </div>

                    <div className="space-y-2">
                      <Label
                        htmlFor="password"
                        className="text-sm font-medium text-slate-200"
                      >
                        {t("auth.login.passwordLabel")}
                      </Label>
                      <Input
                        id="password"
                        type="password"
                        placeholder={t("auth.login.passwordPlaceholder")}
                        value={formData.password}
                        onChange={(e) =>
                          handleInputChange("password", e.target.value)
                        }
                        onBlur={() => handleBlur("password")}
                        className={cn(
                          "h-12 rounded-xl bg-slate-900/50 border-slate-600/50 text-white placeholder:text-slate-400",
                          "focus:border-blue-500/50 focus:ring-4 focus:ring-blue-500/20",
                          "hover:border-slate-500/70 transition-all duration-200",
                          touched.password &&
                            fieldErrors.password &&
                            !fieldErrors.password.isValid &&
                            "border-red-500/50 focus:border-red-500/50 focus:ring-red-500/20"
                        )}
                        disabled={isLoading}
                      />
                      {touched.password &&
                        fieldErrors.password &&
                        !fieldErrors.password.isValid && (
                          <p className="text-sm text-red-400">
                            {t(fieldErrors.password.error!)}
                          </p>
                        )}
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id="rememberMe"
                        checked={formData.rememberMe}
                        onCheckedChange={(checked) =>
                          handleInputChange("rememberMe", !!checked)
                        }
                        disabled={isLoading}
                        className="border-slate-600 data-[state=checked]:bg-blue-600 data-[state=checked]:border-blue-600"
                      />
                      <Label
                        htmlFor="rememberMe"
                        className="text-sm text-slate-300 font-medium cursor-pointer"
                      >
                        {t("auth.login.rememberMe")}
                      </Label>
                    </div>

                    <Link
                      href="/forgot-password"
                      className="text-sm text-blue-400 hover:text-blue-300 transition-colors"
                    >
                      {t("auth.login.forgotPassword")}
                    </Link>
                  </div>

                  <Button
                    type="submit"
                    className="w-full h-12 rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold shadow-lg hover:shadow-xl transition-all duration-300"
                    disabled={isLoading}
                  >
                    {isLoading ? (
                      <div className="flex items-center space-x-2">
                        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                        <span>Signing in...</span>
                      </div>
                    ) : (
                      t("auth.login.loginButton")
                    )}
                  </Button>

                  <div className="text-center text-sm">
                    <span className="text-slate-400">
                      {t("auth.login.noAccount")}{" "}
                    </span>
                    <Link
                      href="/register"
                      className="text-blue-400 hover:text-blue-300 font-medium transition-colors"
                    >
                      {t("auth.login.signUp")}
                    </Link>
                  </div>
                </form>
              </CardContent>
            </Card>
          </motion.div>

          {/* Footer */}
          <motion.div
            className="text-center mt-8 text-slate-400 text-sm"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.4 }}
          >
            © 2024 Connet.AI. Connecting the future, one interaction at a time.
          </motion.div>
        </motion.div>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return <LoginForm />;
}

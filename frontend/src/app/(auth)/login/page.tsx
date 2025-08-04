"use client";

import { useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { useTranslations } from "@/lib/i18n/client";
import useStore from "@/store";
import {
  LoginFormData,
  validateLoginForm,
  ValidationResult,
} from "@/lib/utils/validation";
import { cn } from "@/lib/utils/cn";
import { AuthLayout } from "@/components/auth/AuthLayout";

function LoginForm() {
  const t = useTranslations();
  const router = useRouter();
  const searchParams = useSearchParams();
  const { loginWithCredentials, isLoading, error } = useStore();

  // Get redirect URL from search params (simplified for now)
  const redirectTo = '/dashboard';

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

    // Skip validation for now - allow any login
    console.log('Skipping validation, redirecting to home');
    router.push('/');
  };

  return (
    <AuthLayout 
      title={t("auth.login.title")}
      subtitle={t("auth.login.subtitle")}
    >
      <Card className="w-full border-0 shadow-2xl bg-card/50 backdrop-blur-md">
        <form onSubmit={handleSubmit}>
          <CardContent className="space-y-6 pt-6">
            {error && (
              <div className="p-4 text-sm text-destructive bg-destructive/10 rounded-xl border border-destructive/20">
                {error}
              </div>
            )}

            <div className="space-y-2">
              <Label htmlFor="email" className="text-sm font-medium">
                {t("auth.login.emailLabel")}
              </Label>
              <Input
                id="email"
                type="email"
                placeholder={t("auth.login.emailPlaceholder")}
                value={formData.email}
                onChange={(e) => handleInputChange("email", e.target.value)}
                onBlur={() => handleBlur("email")}
                className={cn(
                  "h-12 rounded-xl border-border/50 bg-background/50 backdrop-blur-sm transition-all duration-200",
                  "focus:border-primary/50 focus:ring-4 focus:ring-primary/10",
                  "hover:border-border/80",
                  touched.email &&
                    fieldErrors.email &&
                    !fieldErrors.email.isValid &&
                    "border-destructive/50 focus:border-destructive/50 focus:ring-destructive/10"
                )}
                disabled={isLoading}
              />
              {touched.email &&
                fieldErrors.email &&
                !fieldErrors.email.isValid && (
                  <p className="text-sm text-destructive">
                    {t(fieldErrors.email.error!)}
                  </p>
                )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="password" className="text-sm font-medium">
                {t("auth.login.passwordLabel")}
              </Label>
              <Input
                id="password"
                type="password"
                placeholder={t("auth.login.passwordPlaceholder")}
                value={formData.password}
                onChange={(e) => handleInputChange("password", e.target.value)}
                onBlur={() => handleBlur("password")}
                className={cn(
                  "h-12 rounded-xl border-border/50 bg-background/50 backdrop-blur-sm transition-all duration-200",
                  "focus:border-primary/50 focus:ring-4 focus:ring-primary/10",
                  "hover:border-border/80",
                  touched.password &&
                    fieldErrors.password &&
                    !fieldErrors.password.isValid &&
                    "border-destructive/50 focus:border-destructive/50 focus:ring-destructive/10"
                )}
                disabled={isLoading}
              />
              {touched.password &&
                fieldErrors.password &&
                !fieldErrors.password.isValid && (
                  <p className="text-sm text-destructive">
                    {t(fieldErrors.password.error!)}
                  </p>
                )}
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
                  className="rounded-md"
                />
                <Label
                  htmlFor="rememberMe"
                  className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                >
                  {t("auth.login.rememberMe")}
                </Label>
              </div>

              <Link
                href="/forgot-password"
                className="text-sm text-primary hover:text-primary/80 transition-colors"
              >
                {t("auth.login.forgotPassword")}
              </Link>
            </div>

            <Button 
              type="submit" 
              className="w-full h-12 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 shadow-lg hover:shadow-xl transition-all duration-200" 
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
              <span className="text-muted-foreground">
                {t("auth.login.noAccount")}{" "}
              </span>
              <Link
                href="/register"
                className="text-primary hover:text-primary/80 font-medium transition-colors"
              >
                {t("auth.login.signUp")}
              </Link>
            </div>
          </CardContent>
        </form>
      </Card>
    </AuthLayout>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <LoginForm />
    </Suspense>
  );
}

"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
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
  RegisterFormData,
  validateRegisterForm,
  ValidationResult,
} from "@/lib/utils/validation";
import { getRegistrationTracking } from "@/lib/utils/url";
import { cn } from "@/lib/utils/cn";
import { AuthLayout } from "@/components/auth/AuthLayout";

export default function RegisterPage() {
  const t = useTranslations();
  const router = useRouter();
  const { registerWithCredentials, isLoading, error } = useStore();

  const [formData, setFormData] = useState<RegisterFormData>({
    full_name: "",
    email: "",
    password: "",
    confirmPassword: "",
    username: "",
    invited_by_code: "",
    agreeToTerms: false,
  });

  const [fieldErrors, setFieldErrors] = useState<
    Record<string, ValidationResult>
  >({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});

  // Auto-fill invite code from URL on component mount
  useEffect(() => {
    const trackingInfo = getRegistrationTracking();
    if (trackingInfo.invited_by_code) {
      setFormData((prev) => ({
        ...prev,
        invited_by_code: trackingInfo.invited_by_code || "",
      }));
    }
  }, []);

  const handleInputChange = (
    field: keyof RegisterFormData,
    value: string | boolean
  ) => {
    setFormData((prev) => ({ ...prev, [field]: value }));

    // Clear field error when user starts typing
    if (fieldErrors[field] && !fieldErrors[field].isValid) {
      setFieldErrors((prev) => ({ ...prev, [field]: { isValid: true } }));
    }
  };

  const handleBlur = (field: keyof RegisterFormData) => {
    setTouched((prev) => ({ ...prev, [field]: true }));

    // Validate single field on blur
    const validation = validateRegisterForm(formData);
    if (validation[field]) {
      setFieldErrors((prev) => ({ ...prev, [field]: validation[field] }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Mark all fields as touched
    setTouched({
      full_name: true,
      email: true,
      password: true,
      confirmPassword: true,
      username: true,
      invited_by_code: true,
    });

    // Validate form
    const validation = validateRegisterForm(formData);
    setFieldErrors(validation);

    // Check terms agreement
    if (!formData.agreeToTerms) {
      setFieldErrors((prev) => ({
        ...prev,
        agreeToTerms: {
          isValid: false,
          error: "auth.validation.termsRequired",
        },
      }));
      return;
    }

    // Check if form is valid
    const isFormValid =
      Object.values(validation).every((result) => result.isValid) &&
      formData.agreeToTerms;

    if (!isFormValid) {
      return;
    }

    try {
      const trackingInfo = getRegistrationTracking();
      const registerData = {
        email: formData.email,
        password: formData.password,
        full_name: formData.full_name,
        username: formData.username || undefined,
        invited_by_code:
          formData.invited_by_code || trackingInfo.invited_by_code,
        registration_source: trackingInfo.registration_source,
        registration_channel: trackingInfo.registration_channel,
        utm_source: trackingInfo.utm_source,
        utm_medium: trackingInfo.utm_medium,
        utm_campaign: trackingInfo.utm_campaign,
      };

      await registerWithCredentials(registerData);

      // Redirect to main app
      router.push("/dashboard");
    } catch (err) {
      // Error is handled by the store
    }
  };

  return (
    <AuthLayout 
      title={t("auth.register.title")}
      subtitle={t("auth.register.subtitle")}
    >
      <Card className="w-full border-0 shadow-2xl bg-card/50 backdrop-blur-md">

        <form onSubmit={handleSubmit}>
          <CardContent className="space-y-4 pt-6">
            {error && (
              <div className="p-4 text-sm text-destructive bg-destructive/10 rounded-xl border border-destructive/20">
                {error}
              </div>
            )}

            <div className="space-y-2">
              <Label htmlFor="full_name">{t("auth.register.nameLabel")}</Label>
              <Input
                id="full_name"
                type="text"
                placeholder={t("auth.register.namePlaceholder")}
                value={formData.full_name}
                onChange={(e) => handleInputChange("full_name", e.target.value)}
                onBlur={() => handleBlur("full_name")}
                className={cn(
                  touched.full_name &&
                    fieldErrors.full_name &&
                    !fieldErrors.full_name.isValid &&
                    "border-destructive focus-visible:ring-destructive"
                )}
                disabled={isLoading}
              />
              {touched.full_name &&
                fieldErrors.full_name &&
                !fieldErrors.full_name.isValid && (
                  <p className="text-sm text-destructive">
                    {t(fieldErrors.full_name.error!)}
                  </p>
                )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="username">
                {t("auth.register.usernameLabel")}
              </Label>
              <Input
                id="username"
                type="text"
                placeholder={t("auth.register.usernamePlaceholder")}
                value={formData.username}
                onChange={(e) => handleInputChange("username", e.target.value)}
                onBlur={() => handleBlur("username")}
                className={cn(
                  touched.username &&
                    fieldErrors.username &&
                    !fieldErrors.username.isValid &&
                    "border-destructive focus-visible:ring-destructive"
                )}
                disabled={isLoading}
              />
              {touched.username &&
                fieldErrors.username &&
                !fieldErrors.username.isValid && (
                  <p className="text-sm text-destructive">
                    {t(fieldErrors.username.error!)}
                  </p>
                )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="email">{t("auth.register.emailLabel")}</Label>
              <Input
                id="email"
                type="email"
                placeholder={t("auth.register.emailPlaceholder")}
                value={formData.email}
                onChange={(e) => handleInputChange("email", e.target.value)}
                onBlur={() => handleBlur("email")}
                className={cn(
                  touched.email &&
                    fieldErrors.email &&
                    !fieldErrors.email.isValid &&
                    "border-destructive focus-visible:ring-destructive"
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
              <Label htmlFor="password">
                {t("auth.register.passwordLabel")}
              </Label>
              <Input
                id="password"
                type="password"
                placeholder={t("auth.register.passwordPlaceholder")}
                value={formData.password}
                onChange={(e) => handleInputChange("password", e.target.value)}
                onBlur={() => handleBlur("password")}
                className={cn(
                  touched.password &&
                    fieldErrors.password &&
                    !fieldErrors.password.isValid &&
                    "border-destructive focus-visible:ring-destructive"
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

            <div className="space-y-2">
              <Label htmlFor="confirmPassword">
                {t("auth.register.confirmPasswordLabel")}
              </Label>
              <Input
                id="confirmPassword"
                type="password"
                placeholder={t("auth.register.confirmPasswordPlaceholder")}
                value={formData.confirmPassword}
                onChange={(e) =>
                  handleInputChange("confirmPassword", e.target.value)
                }
                onBlur={() => handleBlur("confirmPassword")}
                className={cn(
                  touched.confirmPassword &&
                    fieldErrors.confirmPassword &&
                    !fieldErrors.confirmPassword.isValid &&
                    "border-destructive focus-visible:ring-destructive"
                )}
                disabled={isLoading}
              />
              {touched.confirmPassword &&
                fieldErrors.confirmPassword &&
                !fieldErrors.confirmPassword.isValid && (
                  <p className="text-sm text-destructive">
                    {t(fieldErrors.confirmPassword.error!)}
                  </p>
                )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="invited_by_code">
                {t("auth.register.inviteCodeLabel")}
              </Label>
              <Input
                id="invited_by_code"
                type="text"
                placeholder={t("auth.register.inviteCodePlaceholder")}
                value={formData.invited_by_code}
                onChange={(e) =>
                  handleInputChange(
                    "invited_by_code",
                    e.target.value.toUpperCase()
                  )
                }
                onBlur={() => handleBlur("invited_by_code")}
                className={cn(
                  touched.invited_by_code &&
                    fieldErrors.invited_by_code &&
                    !fieldErrors.invited_by_code.isValid &&
                    "border-destructive focus-visible:ring-destructive"
                )}
                disabled={isLoading}
                maxLength={6}
              />
              {touched.invited_by_code &&
                fieldErrors.invited_by_code &&
                !fieldErrors.invited_by_code.isValid && (
                  <p className="text-sm text-destructive">
                    {t(fieldErrors.invited_by_code.error!)}
                  </p>
                )}
            </div>

            <div className="flex items-start space-x-2">
              <Checkbox
                id="agreeToTerms"
                checked={formData.agreeToTerms}
                onCheckedChange={(checked) =>
                  handleInputChange("agreeToTerms", !!checked)
                }
                disabled={isLoading}
                className="mt-1"
              />
              <div className="space-y-1">
                <Label
                  htmlFor="agreeToTerms"
                  className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                >
                  {t("auth.register.agreeTerms")}
                </Label>
                {fieldErrors.agreeToTerms &&
                  !fieldErrors.agreeToTerms.isValid && (
                    <p className="text-sm text-destructive">
                      {t(fieldErrors.agreeToTerms.error!)}
                    </p>
                  )}
              </div>
            </div>
          </CardContent>

          <CardFooter className="flex flex-col space-y-4">
            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? "Loading..." : t("auth.register.registerButton")}
            </Button>

            <div className="text-center text-sm">
              <span className="text-muted-foreground">
                {t("auth.register.hasAccount")}{" "}
              </span>
              <Link
                href="/login"
                className="text-primary hover:underline font-medium"
              >
                {t("auth.register.signIn")}
              </Link>
            </div>
          </CardFooter>
        </form>
      </Card>
    </AuthLayout>
  );
}

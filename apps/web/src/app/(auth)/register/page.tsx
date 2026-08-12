"use client";

import Link from "next/link";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import Logo from "@/components/Logo";

export default function RegisterPage() {
  const [displayName, setDisplayName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await register(email, password, displayName);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="rounded-lg border border-clipmind-border bg-clipmind-surface p-8">
      <div className="mb-8 text-center">
        <Logo />
        <h1 className="mt-4 text-xl font-semibold">Create your account</h1>
      </div>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        {error && (
          <div
            role="alert"
            className="rounded-md border border-clipmind-danger/30 bg-clipmind-danger/10 px-4 py-3 text-sm text-clipmind-danger"
          >
            {error}
          </div>
        )}
        <div>
          <label
            htmlFor="displayName"
            className="mb-1 block text-sm font-medium text-clipmind-text-muted"
          >
            Display name
          </label>
          <input
            id="displayName"
            type="text"
            required
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
            className="w-full rounded-md border border-clipmind-border bg-clipmind-surface-raised px-4 py-3 text-clipmind-text outline-none focus:border-clipmind-focus focus:shadow-focus"
            placeholder="Maya Chen"
          />
        </div>
        <div>
          <label
            htmlFor="email"
            className="mb-1 block text-sm font-medium text-clipmind-text-muted"
          >
            Email
          </label>
          <input
            id="email"
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full rounded-md border border-clipmind-border bg-clipmind-surface-raised px-4 py-3 text-clipmind-text outline-none focus:border-clipmind-focus focus:shadow-focus"
            placeholder="you@example.com"
          />
        </div>
        <div>
          <label
            htmlFor="password"
            className="mb-1 block text-sm font-medium text-clipmind-text-muted"
          >
            Password
          </label>
          <input
            id="password"
            type="password"
            required
            minLength={8}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full rounded-md border border-clipmind-border bg-clipmind-surface-raised px-4 py-3 text-clipmind-text outline-none focus:border-clipmind-focus focus:shadow-focus"
            placeholder="Minimum 8 characters"
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="mt-2 rounded-md bg-clipmind-primary px-4 py-3 font-semibold text-clipmind-bg transition-colors hover:bg-clipmind-primary-hover disabled:cursor-not-allowed disabled:opacity-45"
        >
          {loading ? "Creating account..." : "Create account"}
        </button>
      </form>
      <p className="mt-6 text-center text-sm text-clipmind-text-muted">
        Already have an account?{" "}
        <Link
          href="/login"
          className="font-medium text-clipmind-primary hover:text-clipmind-primary-hover"
        >
          Log in
        </Link>
      </p>
    </div>
  );
}

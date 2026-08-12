import Link from "next/link";
import Logo from "@/components/Logo";

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col">
      <header className="flex items-center justify-between border-b border-clipmind-border px-6 py-4">
        <Logo />
        <div className="flex items-center gap-4">
          <Link
            href="/login"
            className="rounded-md px-4 py-2 text-sm font-medium text-clipmind-text-muted transition-colors hover:text-clipmind-text"
          >
            Log in
          </Link>
          <Link
            href="/register"
            className="rounded-md bg-clipmind-primary px-4 py-2 text-sm font-semibold text-clipmind-bg transition-colors hover:bg-clipmind-primary-hover"
          >
            Summarize a video
          </Link>
        </div>
      </header>

      <main className="flex flex-1 flex-col items-center justify-center px-6 py-24 text-center">
        <h1 className="max-w-3xl text-5xl font-bold leading-tight tracking-tight md:text-6xl">
          Turn a 40-minute video into a{" "}
          <span className="text-clipmind-primary">2-minute read</span>.
        </h1>
        <p className="mt-6 max-w-xl text-lg text-clipmind-text-muted">
          Upload a lecture, meeting or creator video. Get the answer first.
        </p>
        <div className="mt-10 flex flex-col gap-4 sm:flex-row">
          <Link
            href="/register"
            className="rounded-md bg-clipmind-primary px-6 py-3 text-base font-semibold text-clipmind-bg transition-colors hover:bg-clipmind-primary-hover"
          >
            Summarize a video
          </Link>
          <Link
            href="#how-it-works"
            className="rounded-md border border-clipmind-border px-6 py-3 text-base font-semibold text-clipmind-text transition-colors hover:bg-clipmind-surface-raised"
          >
            See how it works
          </Link>
        </div>

        <div className="mt-20 grid max-w-2xl grid-cols-1 gap-8 sm:grid-cols-3">
          <div className="rounded-lg border border-clipmind-border bg-clipmind-surface p-6">
            <p className="text-3xl font-bold text-clipmind-primary">92%</p>
            <p className="mt-2 text-sm text-clipmind-text-muted">
              less review time*
            </p>
          </div>
          <div className="rounded-lg border border-clipmind-border bg-clipmind-surface p-6">
            <p className="text-3xl font-bold text-clipmind-primary">40+</p>
            <p className="mt-2 text-sm text-clipmind-text-muted">
              languages*
            </p>
          </div>
          <div className="rounded-lg border border-clipmind-border bg-clipmind-surface p-6">
            <p className="text-3xl font-bold text-clipmind-primary">Private</p>
            <p className="mt-2 text-sm text-clipmind-text-muted">
              by default*
            </p>
          </div>
        </div>
      </main>

      <section
        id="how-it-works"
        className="border-t border-clipmind-border bg-clipmind-surface px-6 py-20"
      >
        <h2 className="text-center text-2xl font-bold">How it works</h2>
        <div className="mx-auto mt-12 grid max-w-3xl grid-cols-1 gap-8 sm:grid-cols-4">
          {[
            { step: "Upload", desc: "Drop your video file" },
            { step: "Transcript", desc: "Timestamped text" },
            { step: "Summary", desc: "Short and detailed" },
            { step: "Key moments", desc: "Important timestamps" },
          ].map((item, i) => (
            <div key={item.step} className="text-center">
              <div className="mx-auto flex h-10 w-10 items-center justify-center rounded-full bg-clipmind-primary text-sm font-bold text-clipmind-bg">
                {i + 1}
              </div>
              <p className="mt-3 font-semibold">{item.step}</p>
              <p className="mt-1 text-sm text-clipmind-text-muted">
                {item.desc}
              </p>
            </div>
          ))}
        </div>
      </section>

      <footer className="border-t border-clipmind-border px-6 py-8 text-center text-sm text-clipmind-text-muted">
        <p>
          * Use only clearly labelled illustrative/demo metrics until real data
          exists.
        </p>
        <p className="mt-2">
          ClipMind AI &mdash; an Infosys Springboard project
        </p>
      </footer>
    </div>
  );
}

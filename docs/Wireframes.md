# ClipMind AI — Day 2 Wireframes

These text wireframes define hierarchy and interaction before visual implementation. Day 3 will create shells only; functionality follows the roadmap.

## 1. Landing page

```text
┌ ClipMind AI ─────────────────────────────── Log in  [Summarize a video] ┐
│ Turn a 40-minute video into a 2-minute read.                           │
│ Upload a lecture, meeting or creator video. Get the answer first.      │
│ [Summarize a video]          [See how it works]                         │
├ 92% less review time* ─ 40+ languages* ─ Private by default* ──────────┤
│ How it works:  Upload  →  Transcript  →  Summary  →  Key moments       │
├──────────────────────── soft divider ──────────────────────────────────┤
│ A preview: Summary card / timestamped moment cards / transcript sample │
└────────────────────────────────────────────────────────────────────────┘
* Use only clearly labelled illustrative/demo metrics until real data exists.
```

## 2. Signed-in dashboard and upload

```text
┌──────────────┬─────────────────────────────────────────────────────────┐
│ ClipMind AI  │ Good morning, Maya                    [Profile ▾]       │
│ Dashboard    ├─────────────────────────────────────────────────────────┤
│ My videos    │ Turn a long video into something you can read.          │
│ Upload       │ [Summarize a video]                                     │
│ Bookmarks    ├─────────────────────────────────────────────────────────┤
│ History      │ Recent videos                                            │
│ (Admin only) │ [Card: title/status/duration] [Card] [Card]              │
└──────────────┴─────────────────────────────────────────────────────────┘

Upload dialog
┌ Upload a video ────────────────────────────────────────────────────────┐
│ Drop MP4, MOV, WebM or AVI here, or [Choose a file]                    │
│ Up to 500 MB • up to 60 minutes • Your video stays private             │
│ File name / validation message                                          │
│                                    [Cancel] [Upload and summarize]     │
└────────────────────────────────────────────────────────────────────────┘
```

## 3. Processing state

```text
┌ Product meeting.mp4                                      [Back to library] ┐
│ We’re turning your video into a readable brief.                            │
│ ✓ Video uploaded  →  ● Extracting audio  →  ○ Transcribing  →  ○ Summary  │
│ Extracting audio… This usually takes a moment.                              │
│ [Progress bar only when worker reports a real value]                        │
│ Need help? [View supported formats]                                        │
└───────────────────────────────────────────────────────────────────────────┘
```

## 4. Video intelligence view

```text
┌ Product meeting.mp4                         Ready  [Share] [Export ▾] ┐
│ 2-minute brief                                                     │
│ A decision was made to launch…                                    │
│ [Short summary] [Detailed summary]                                │
├─────────────────────────────┬─────────────────────────────────────┤
│ Key moments                 │ Video player                         │
│ 02:14 Launch decision       │                                     │
│ 12:46 Budget concern        │  ▶  12:46 / 42:13                   │
│ 31:08 Next steps            │                                     │
├─────────────────────────────┴─────────────────────────────────────┤
│ Transcript                                      [Search transcript]│
│ 12:46  We need to confirm…                                         │
│ 13:08  The budget…                                                  │
└───────────────────────────────────────────────────────────────────┘
```

## Responsive and accessibility decisions

- At widths below 1024 px, navigation becomes a labelled menu; below 640 px, summary, timeline and transcript stack vertically.
- Every timestamp is a keyboard-operable button, not plain text. Activating it seeks the video and announces the new time.
- Upload validation, job state and errors are written in text and announced through a polite live region; colour is supplementary.
- The summary always appears before the raw transcript. The interface never represents a guessed percent as real processing progress.

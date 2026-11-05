import "./globals.css";

export const metadata = {
  title: "AURA Studio",
  description: "Project workspace and video management",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="dark bg-slate-950 text-slate-100">{children}</body>
    </html>
  );
}

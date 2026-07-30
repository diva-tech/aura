"use client";

import { useParams } from "next/navigation";
import { PreviewLayout } from "@/components/preview/PreviewLayout";

export default function PreviewPage() {
  const params = useParams();
  const projectId = params.projectId as string;

  return <PreviewLayout projectId={projectId} />;
}
